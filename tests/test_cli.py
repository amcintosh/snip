import pytest
from unittest.mock import patch
from click.testing import CliRunner

from snip.cli import main
from snip.models import Snippet


@pytest.fixture
def runner():
    return CliRunner()


class TestNewCommand:
    def test_save_snippet(self, runner):
        with patch("snip.cli.save_snippet") as mock_save:
            result = runner.invoke(main, ["new"], input="my key\nmy content\n\n")
        assert result.exit_code == 0
        snippet = mock_save.call_args[0][0]
        assert snippet.key == "my key"
        assert snippet.content == "my content"
        assert snippet.tags == []

    def test_save_snippet__tags(self, runner):
        with patch("snip.cli.save_snippet") as mock_save:
            result = runner.invoke(main, ["new"], input="my key\nmy content\ntag1, tag2\n")
        assert result.exit_code == 0
        assert mock_save.call_args[0][0].tags == ["tag1", "tag2"]


class TestListCommand:
    SNIPPETS = [
        Snippet(key="key1", content="content1", tags=["t1"]),
        Snippet(key="key2", content="content2"),
    ]

    def test_list(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "key1" in result.output
        assert "content1" in result.output
        assert "t1" in result.output
        assert "key2" in result.output

    def test_list__no_tags(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["list"])
        lines = result.output.splitlines()
        key2_idx = next(i for i, line in enumerate(lines) if "key2" in line)
        assert not any("Tags" in line for line in lines[key2_idx:key2_idx + 3])

    def test_list__empty(self, runner):
        with patch("snip.cli.load_snippets", return_value=[]):
            result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert result.output == ""


class TestSearchCommand:
    SNIPPETS = [
        Snippet(key="who-are-you", content="http://imgur.com/12345", tags=["gif", "meme"]),
        Snippet(key="splunk-index", content="index=blah", tags=["work", "logs"]),
        Snippet(key="myemail", content="someone@test.com", tags=["work", "email"])
    ]

    def test_match__exact(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["search", "splunk-index"])
        assert result.exit_code == 0
        assert "index=blah" in result.output

    def test_no_match__exits_with_error(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["search", "nothing"])
        assert result.exit_code == 1
        assert "No snippet found for: nothing" in result.output

    def test_no_args__exits_with_error(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["search"])
        assert result.exit_code == 1

    def test_tag__returns_matching_snippets(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["search", "--tag", "work"])
        assert result.exit_code == 0
        assert "index=blah" in result.output
        assert "someone@test.com" in result.output

    def test_tag__short_flag(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["search", "-t", "meme"])
        assert result.exit_code == 0
        assert "http://imgur.com/12345" in result.output

    def test_tag__no_match_exits_with_error(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["search", "--tag", "python"])
        assert result.exit_code == 1

    def test_tag_and_query_combined(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["search", "splunk-index", "--tag", "work"])
        assert result.exit_code == 0
        assert "index=blah" in result.output

    def test_match__no_clipboard_flag(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS), \
             patch("snip.cli.subprocess.run") as mock_run:
            result = runner.invoke(main, ["search", "splunk-index", "--no-clipboard"])
        assert result.exit_code == 0
        mock_run.assert_not_called()

    def test_default_command(self, runner):
        with patch("snip.cli.load_snippets", return_value=self.SNIPPETS):
            result = runner.invoke(main, ["splunk-index"])
        assert result.exit_code == 0
        assert "index=blah" in result.output


class TestConfigureCommand:
    def test_opens_editor(self, runner, tmp_path):
        config_path = str(tmp_path / "config.toml")
        with patch(
            "snip.cli.config_init",
            return_value=config_path
        ), patch("click.edit") as mock_edit:
            result = runner.invoke(main, ["configure"])
        assert result.exit_code == 0
        mock_edit.assert_called_once_with(filename=config_path)
