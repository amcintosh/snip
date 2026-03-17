import os
import tomllib

import click

from snip.models import Snippet


def get_snippets_path() -> str:  # pragma: no cover
    app_dir = click.get_app_dir("snip")
    return os.path.join(app_dir, "snippets.toml")


def load_snippets() -> list[Snippet]:
    snippets_path = get_snippets_path()
    if not os.path.exists(snippets_path):
        return []
    with open(snippets_path, "rb") as f:
        data = tomllib.load(f)
    return [Snippet(**s) for s in data.get("snippets", [])]


def save_snippet(snippet: Snippet) -> None:
    snippets_path = get_snippets_path()
    os.makedirs(os.path.dirname(snippets_path), exist_ok=True)
    tags = ", ".join(f'"{t}"' for t in snippet.tags)
    entry = f'\n[[snippets]]\n  key = "{snippet.key}"\n  content = "{snippet.content}"\n  tags = [{tags}]\n'
    with open(snippets_path, "a") as f:
        f.write(entry)
