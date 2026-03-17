import os

import click

from snip.models import Snippet


def get_snippets_path() -> str:
    app_dir = click.get_app_dir("snip")
    return os.path.join(app_dir, "snippets.toml")


def save_snippet(snippet: Snippet) -> None:
    snippets_path = get_snippets_path()
    os.makedirs(os.path.dirname(snippets_path), exist_ok=True)
    tags = ", ".join(f'"{t}"' for t in snippet.tags)
    entry = f'\n[[snippets]]\n  key = "{snippet.key}"\n  content = "{snippet.content}"\n  tags = [{tags}]\n'
    with open(snippets_path, "a") as f:
        f.write(entry)
