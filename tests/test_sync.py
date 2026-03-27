from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from snip.cli import main
from snip.sync import _download, _get_access_token, _get_gist, _upload, sync

MOCK_CONFIG = {
    "Gist": {
        "access_token": "test-token",
        "gist_id": "abc123",
        "file_name": "snip.toml",
        "Public": False
    }
}

REMOTE_CONTENT = '[[snippets]]\n  key = "remote"\n  content = "remote content"\n  tags = []\n'
LOCAL_CONTENT = '[[snippets]]\n  key = "local"\n  content = "local content"\n  tags = []\n'


class TestGetAccessToken:
    def test_returns_token_from_config(self):
        assert _get_access_token({"access_token": "my-token"}) == "my-token"

    def test_returns_token_from_env(self, monkeypatch):
        monkeypatch.setenv("SNIP_GITHUB_ACCESS_TOKEN", "env-token")
        assert _get_access_token({}) == "env-token"

    def test_raises_when_no_token(self, monkeypatch):
        monkeypatch.delenv("SNIP_GITHUB_ACCESS_TOKEN", raising=False)
        from click import ClickException

        with pytest.raises(ClickException, match="access_token is empty"):
            _get_access_token({})


class TestGetGist:
    def test_returns_none_when_no_gist_id(self):
        content, updated_at = _get_gist("", "snip.toml", "token")
        assert content is None
        assert updated_at is None

    def test_returns_content_and_timestamp(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "files": {"snip.toml": {"content": REMOTE_CONTENT}},
            "updated_at": "2026-03-17T12:00:00Z",
        }
        with patch("snip.sync.requests.get", return_value=mock_response):
            content, updated_at = _get_gist("abc123", "snip.toml", "token")
        assert content == REMOTE_CONTENT
        assert updated_at == datetime(2026, 3, 17, 12, 0, 0, tzinfo=timezone.utc)

    def test_raises_on_404(self):
        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch("snip.sync.requests.get", return_value=mock_response):
            from click import ClickException

            with pytest.raises(ClickException, match="Gist not found"):
                _get_gist("bad-id", "snip.toml", "token")

    def test_raises_when_file_not_in_gist(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "files": {"other.toml": {"content": "stuff"}},
            "updated_at": "2026-03-17T12:00:00Z",
        }
        with patch("snip.sync.requests.get", return_value=mock_response):
            from click import ClickException

            with pytest.raises(ClickException, match="not found in gist"):
                _get_gist("abc123", "snip.toml", "token")


class TestUpload:
    def test_patches_existing_gist(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        with patch("snip.sync.requests.patch", return_value=mock_response) as mock_patch:
            _upload(LOCAL_CONTENT, MOCK_CONFIG["Gist"], "token")
        mock_patch.assert_called_once()
        assert "abc123" in mock_patch.call_args[0][0]

    def test_creates_new_gist_when_no_id(self, capsys):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "new-gist-id"}
        config = {**MOCK_CONFIG["Gist"], "gist_id": ""}
        with patch("snip.sync.requests.post", return_value=mock_response):
            _upload(LOCAL_CONTENT, config, "token")
        captured = capsys.readouterr()
        assert "new-gist-id" in captured.out

    def test_prints_upload_success(self, capsys):
        mock_response = MagicMock()
        mock_response.status_code = 200
        with patch("snip.sync.requests.patch", return_value=mock_response):
            _upload(LOCAL_CONTENT, MOCK_CONFIG["Gist"], "token")
        captured = capsys.readouterr()
        assert "Upload success" in captured.out


class TestDownload:
    def test_writes_content_to_file(self, tmp_path):
        snippets_path = str(tmp_path / "snippets.toml")
        _download(REMOTE_CONTENT, snippets_path)
        with open(snippets_path) as f:
            assert f.read() == REMOTE_CONTENT

    def test_prints_download_success(self, tmp_path, capsys):
        snippets_path = str(tmp_path / "snippets.toml")
        _download(REMOTE_CONTENT, snippets_path)
        captured = capsys.readouterr()
        assert "Download success" in captured.out

    def test_already_up_to_date(self, tmp_path, capsys):
        snippets_path = str(tmp_path / "snippets.toml")
        with open(snippets_path, "w") as f:
            f.write(REMOTE_CONTENT)
        _download(REMOTE_CONTENT, snippets_path)
        captured = capsys.readouterr()
        assert "Already up-to-date" in captured.out


class TestSync:
    def test_uploads_when_local_is_newer(self, tmp_path):
        snippets_path = str(tmp_path / "snippets.toml")
        with open(snippets_path, "w") as f:
            f.write(LOCAL_CONTENT)

        remote_time = datetime(2026, 3, 1, tzinfo=timezone.utc)
        local_time = datetime(2026, 3, 17, tzinfo=timezone.utc)

        with (
            patch("snip.sync.load_config", return_value=MOCK_CONFIG),
            patch("snip.sync.get_snippets_path", return_value=snippets_path),
            patch("snip.sync._get_gist", return_value=(REMOTE_CONTENT, remote_time)),
            patch("snip.sync.os.path.getmtime", return_value=local_time.timestamp()),
            patch("snip.sync._upload") as mock_upload,
        ):
            sync()
        mock_upload.assert_called_once_with(LOCAL_CONTENT, MOCK_CONFIG["Gist"], "test-token")

    def test_downloads_when_remote_is_newer(self, tmp_path):
        snippets_path = str(tmp_path / "snippets.toml")
        with open(snippets_path, "w") as f:
            f.write(LOCAL_CONTENT)

        remote_time = datetime(2026, 3, 17, tzinfo=timezone.utc)
        local_time = datetime(2026, 3, 1, tzinfo=timezone.utc)

        with (
            patch("snip.sync.load_config", return_value=MOCK_CONFIG),
            patch("snip.sync.get_snippets_path", return_value=snippets_path),
            patch("snip.sync._get_gist", return_value=(REMOTE_CONTENT, remote_time)),
            patch("snip.sync.os.path.getmtime", return_value=local_time.timestamp()),
            patch("snip.sync._download") as mock_download,
        ):
            sync()
        mock_download.assert_called_once_with(REMOTE_CONTENT, snippets_path)

    def test_already_up_to_date(self, tmp_path, capsys):
        snippets_path = str(tmp_path / "snippets.toml")
        with open(snippets_path, "w") as f:
            f.write(LOCAL_CONTENT)

        sync_time = datetime(2026, 3, 17, tzinfo=timezone.utc)

        with (
            patch("snip.sync.load_config", return_value=MOCK_CONFIG),
            patch("snip.sync.get_snippets_path", return_value=snippets_path),
            patch("snip.sync._get_gist", return_value=(REMOTE_CONTENT, sync_time)),
            patch("snip.sync.os.path.getmtime", return_value=sync_time.timestamp()),
        ):
            sync()
        assert "Already up-to-date" in capsys.readouterr().out

    def test_downloads_when_local_missing(self, tmp_path):
        snippets_path = str(tmp_path / "snippets.toml")
        remote_time = datetime(2026, 3, 17, tzinfo=timezone.utc)

        with (
            patch("snip.sync.load_config", return_value=MOCK_CONFIG),
            patch("snip.sync.get_snippets_path", return_value=snippets_path),
            patch("snip.sync._get_gist", return_value=(REMOTE_CONTENT, remote_time)),
            patch("snip.sync._download") as mock_download,
        ):
            sync()
        mock_download.assert_called_once_with(REMOTE_CONTENT, snippets_path)

    def test_uploads_when_no_gist_id(self, tmp_path):
        snippets_path = str(tmp_path / "snippets.toml")
        with open(snippets_path, "w") as f:
            f.write(LOCAL_CONTENT)

        config = {**MOCK_CONFIG["Gist"], "gist_id": ""}
        with (
            patch("snip.sync.load_gist_config", return_value=config),
            patch("snip.sync.get_snippets_path", return_value=snippets_path),
            patch("snip.sync._get_gist", return_value=(None, None)),
            patch("snip.sync._upload") as mock_upload,
        ):
            sync()
        mock_upload.assert_called_once()


class TestSyncCommand:
    def test_sync_command(self):
        runner = CliRunner()
        with patch("snip.cli.sync") as mock_sync:
            result = runner.invoke(main, ["sync"])
        assert result.exit_code == 0
        mock_sync.assert_called_once()
