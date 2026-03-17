import pytest
from unittest.mock import patch

from snip.models import Snippet
from snip.storage import load_snippets, save_snippet


@pytest.fixture
def snippets_path(tmp_path):
    path = str(tmp_path / "snippets.toml")
    with patch("snip.storage.get_snippets_path", return_value=path):
        yield path


def test_load_missing_file(snippets_path):
    assert load_snippets() == []


def test_save_and_load(snippets_path):
    save_snippet(Snippet(key="test", content="echo hello", tags=["shell"]))
    results = load_snippets()
    assert len(results) == 1
    assert results[0] == Snippet(key="test", content="echo hello", tags=["shell"])


def test_save_no_tags(snippets_path):
    save_snippet(Snippet(key="bare", content="ls"))
    assert load_snippets()[0].tags == []


def test_save_multiple(snippets_path):
    save_snippet(Snippet(key="a", content="aaa"))
    save_snippet(Snippet(key="b", content="bbb"))
    results = load_snippets()
    assert [snippet.key for snippet in results] == ["a", "b"]
