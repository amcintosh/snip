import difflib

from snip.models import Snippet


def search(
    snippets: list[Snippet],
    query: str | None = None,
    case_sensitive: bool = False,
    tag: str | None = None,
) -> list[Snippet]:
    """Return snippets matching query and/or tag.

    When tag is given, filters to snippets containing that tag first.
    When query is given, returns exact match(es) if found, otherwise up to 3 fuzzy matches.
    When only tag is given, returns all snippets with that tag.
    """
    # Filter snippets by tag
    if tag is not None:
        snippets = [s for s in snippets if tag.lower() in s.tags]
    if query is None:
        return snippets

    for snippet in snippets:
        if (case_sensitive and snippet.key == query) or (not case_sensitive and snippet.key.lower() == query.lower()):
            return [snippet]

    if case_sensitive:  # Don't fuzzy match
        return []

    keys = [s.key for s in snippets]
    close_matches = difflib.get_close_matches(query, keys, n=3, cutoff=0.6)
    close_index = {name: i for i, name in enumerate(close_matches)}
    fuzzy = []
    for snippet in snippets:
        if snippet.key in close_index:
            fuzzy.append(snippet)
    fuzzy.sort(key=lambda snippet: close_index[snippet.key])
    return fuzzy
