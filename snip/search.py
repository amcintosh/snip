import difflib

from snip.models import Snippet


def search(snippets: list[Snippet], query: str, case_sensitive: bool = False) -> list[Snippet]:
    """Return snippets matching query.

    Returns exact match(es) if found, otherwise up to 3 fuzzy matches.
    """
    cmp = (lambda s: s) if case_sensitive else str.lower
    q = cmp(query)
    abbrs = [cmp(s.key) for s in snippets]

    exact = [s for s, a in zip(snippets, abbrs) if a == q]
    if exact:
        return exact

    close = difflib.get_close_matches(q, abbrs, n=3, cutoff=0.6)
    close_index = {name: i for i, name in enumerate(close)}
    fuzzy = [s for s, a in zip(snippets, abbrs) if a in close_index]
    fuzzy.sort(key=lambda s: close_index[cmp(s.key)])
    return fuzzy
