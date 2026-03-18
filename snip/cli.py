import subprocess
import sys

import click

from snip.config import config_init
from snip.models import Snippet
from snip.search import search
from snip.storage import load_snippets, save_snippet

PROMPT_KEY_COLOR = "green"
PROMPT_CONTENT_COLOR = "cyan"
PROMPT_USER_CONTENT = "white"


class DefaultSearchGroup(click.Group):
    def resolve_command(self, ctx, args):
        cmd_name = args[0] if args else None
        if cmd_name is not None and cmd_name not in self.commands and not cmd_name.startswith("-"):
            args.insert(0, "search")
        return super().resolve_command(ctx, args)


@click.group(cls=DefaultSearchGroup)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Simple tool for storing and searching text snippets."""
    ctx.ensure_object(dict)


@main.command()
@click.argument("snippet", required=False, default=None)
@click.option(
    "--tag",
    "-t",
    default=None,
    help="Filter snippets by tag.",
)
@click.option(
    "--case-sensitive",
    "-c",
    is_flag=True,
    default=False,
    help="Use case-sensitive matching.",
)
@click.option(
    "--no-clipboard",
    "-n",
    is_flag=True,
    default=False,
    help="Do not copy the top result to the clipboard.",
)
@click.pass_context
def search_cmd(ctx: click.Context, snippet: str | None, tag: str | None, case_sensitive: bool, no_clipboard: bool) -> None:
    """Search for a snippet and print its content. Save to clipboard by default."""
    if snippet is None and tag is None:
        click.echo("Provide a search query or --tag.", err=True)
        sys.exit(1)

    snippets = load_snippets()
    results = search(snippets, snippet, case_sensitive=case_sensitive, tag=tag)

    if not results:
        label = snippet
        if snippet is None:
            label = f"tag:{tag}"
        click.echo(f"No snippet found for: {label}", err=True)
        sys.exit(1)

    if sys.platform == "darwin" and not no_clipboard:
        subprocess.run(["pbcopy"], input=results[0].content.encode(), check=True)

    for snippet in results:
        click.echo(snippet.content)


@main.command("list")
def list_cmd() -> None:
    """List all snippets."""
    snippets = load_snippets()
    for snippet in snippets:
        click.echo(click.style("Key: ", fg=PROMPT_KEY_COLOR) + click.style(snippet.key, fg=PROMPT_USER_CONTENT))
        click.echo(
            click.style("  Content: ", fg=PROMPT_CONTENT_COLOR) + click.style(snippet.content, fg=PROMPT_USER_CONTENT)
        )
        if snippet.tags:
            click.echo(
                click.style("  Tags: ", fg=PROMPT_CONTENT_COLOR)
                + click.style(", ".join(snippet.tags), fg=PROMPT_USER_CONTENT)
            )
        click.echo("-" * 30)


@main.command("new")
def new_cmd() -> None:
    """Create a new snippet"""
    key = click.prompt(click.style("key", fg=PROMPT_KEY_COLOR))
    content = click.prompt(click.style("content", fg=PROMPT_CONTENT_COLOR))
    tags_input = click.prompt(click.style("tags", fg=PROMPT_CONTENT_COLOR), default="")
    tags = [t.strip() for t in tags_input.split(",") if t.strip()]
    save_snippet(Snippet(key=key, content=content, tags=tags))


@main.command("configure")
def configure_cmd() -> None:
    """Edit config file"""
    config_path = config_init()
    click.edit(filename=config_path)
