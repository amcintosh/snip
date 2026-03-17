import pytest

from snip.models import Snippet
from snip.search import search


SNIPPETS = [
    Snippet(key="git commit", content="git commit -m 'msg'"),
    Snippet(key="git push", content="git push origin main"),
    Snippet(key="docker run", content="docker run -it ubuntu"),
]


def test_exact_match():
    results = search(SNIPPETS, "git commit")
    assert len(results) == 1
    assert results[0].key == "git commit"


def test_case_insensitive_by_default():
    results = search(SNIPPETS, "GIT COMMIT")
    assert len(results) == 1
    assert results[0].key == "git commit"


def test_case_sensitive_no_match():
    results = search(SNIPPETS, "GIT COMMIT", case_sensitive=True)
    assert results == []


def test_fuzzy_match():
    results = search(SNIPPETS, "git committ")
    assert len(results) >= 1
    assert results[0].key == "git commit"


def test_no_match():
    results = search(SNIPPETS, "kubectl apply")
    assert results == []


def test_empty_snippets():
    assert search([], "anything") == []
