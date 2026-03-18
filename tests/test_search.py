from snip.models import Snippet
from snip.search import search

SNIPPETS = [
    Snippet(key="who-are-you", content="http://imgur.com/12345", tags=["gif", "meme"]),
    Snippet(key="splunk-index", content="index=blah", tags=["work", "logs"]),
    Snippet(key="myemail", content="someone@test.com", tags=["work", "email"])
]


def test_match__exact():
    results = search(SNIPPETS, "who-are-you")
    assert len(results) == 1
    assert results[0].key == "who-are-you"


def test_no_match__case_sensitive():
    results = search(SNIPPETS, "WHO-ARE-YOU", case_sensitive=True)
    assert results == []


def test_match__fuzzy():
    results = search(SNIPPETS, "who-are-u")
    assert len(results) >= 1
    assert results[0].key == "who-are-you"


def test_no_match():
    results = search(SNIPPETS, "diary")
    assert results == []


def test_no_match__empty_snippets():
    assert search([], "anything") == []


def test_tag__returns_matching_snippets():
    results = search(SNIPPETS, tag="work")
    assert len(results) == 2
    assert all("work" in s.tags for s in results)


def test_tag__no_query_returns_all_tagged():
    results = search(SNIPPETS, tag="logs")
    assert len(results) == 1
    assert results[0].key == "splunk-index"


def test_tag__case_insensitive():
    results = search(SNIPPETS, tag="WORK")
    assert len(results) == 2


def test_tag__case_sensitive_query_only():
    results = search(SNIPPETS, tag="WORK", case_sensitive=True)
    assert len(results) == 2


def test_tag__no_match():
    results = search(SNIPPETS, tag="python")
    assert results == []


def test_tag_and_query_combined():
    results = search(SNIPPETS, query="splunk-index", tag="work")
    assert len(results) == 1
    assert results[0].key == "splunk-index"


def test_tag__query_not_in_tag():
    # "git push" has tag "git", but query is "docker run" — no match within git-tagged snippets
    results = search(SNIPPETS, query="splunk-index", tag="meme")
    assert results == []
