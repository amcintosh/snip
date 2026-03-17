import pytest
from unittest.mock import patch
from click.testing import CliRunner

from snip.cli import main
from snip.models import Snippet


@pytest.fixture
def runner():
    return CliRunner()


class TestNewCommand:
    def test_saves_snippet(self, runner):
        with patch("snip.cli.save_snippet") as mock_save:
            result = runner.invoke(main, ["new"], input="my key\nmy content\n\n")
        assert result.exit_code == 0
        snippet = mock_save.call_args[0][0]
        assert snippet.key == "my key"
        assert snippet.content == "my content"
        assert snippet.tags == []

    def test_saves_tags(self, runner):
        with patch("snip.cli.save_snippet") as mock_save:
            result = runner.invoke(main, ["new"], input="my key\nmy content\ntag1, tag2\n")
        assert result.exit_code == 0
        assert mock_save.call_args[0][0].tags == ["tag1", "tag2"]


class TestListCommand:
    SNIPPETS = [
        Snippet(key="key1", content="content1", tags=["t1"]),
        Snippet(key="key2", content="content2"),
    ]

    def test_output(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "key1" in result.output
        assert "content1" in result.output
        assert "t1" in result.output
        assert "key2" in result.output

    def test_no_tags_line_when_empty(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["list"])
        lines = result.output.splitlines()
        key2_idx = next(i for i, line in enumerate(lines) if "key2" in line)
        assert not any("Tags" in line for line in lines[key2_idx:key2_idx + 3])

    def test_empty(self, runner):
        with patch("snip.cli.load_snippets", return_value=[]):
            result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert result.output == ""


class TestConfigureCommand:
    def test_opens_editor(self, runner, tmp_path):
        config_path = str(tmp_path / "config.toml")
        with patch("snip.cli.config_init", return_value=config_path), \
             patch("click.edit") as mock_edit:
            result = runner.invoke(main, ["configure"])
        assert result.exit_code == 0
        mock_edit.assert_called_once_with(filename=config_path)
