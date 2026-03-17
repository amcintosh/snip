import subprocess
import sys

import click

from snip.config import config_init
from snip.models import Snippet
from snip.search import search
from snip.storage import save_snippet

PROMPT_KEY_COLOR = "green"
PROMPT_CONTENT_COLOR = "cyan"


class DefaultSearchGroup(click.Group):
    def resolve_command(self, ctx, args):
        cmd_name = args[0] if args else None
        if cmd_name is not None and cmd_name not in self.commands and not cmd_name.startswith("-"):
            args.insert(0, "search")
        return super().resolve_command(ctx, args)


@click.group(cls=DefaultSearchGroup)
@click.pass_context
def main(ctx: click.Context) -> None:
    """CLI tool for storing and searching text snippet."""
    ctx.ensure_object(dict)


@main.command()
@click.argument("snippet")
@click.option(
    "--case-sensitive", "-c",
    is_flag=True,
    default=False,
    help="Use case-sensitive matching.",
)
@click.option(
    "--no-clipboard", "-n",
    is_flag=True,
    default=False,
    help="Do not copy the top result to the clipboard.",
)
@click.pass_context
def search_cmd(ctx: click.Context, snippet: str, case_sensitive: bool, no_clipboard: bool) -> None:
    """Search for SNIPPET and print its content. Saves to clipboard by default."""
    snippets = load_snippets(ctx.obj["file"])
    results = search(snippets, snippet, case_sensitive=case_sensitive)

    if not results:
        click.echo(f"No snippet found for: {snippet}", err=True)
        sys.exit(1)

    if sys.platform == "darwin" and not no_clipboard:
        subprocess.run(["pbcopy"], input=results[0].content.encode(), check=True)

    for snippet in results:
        click.echo(snippet.content)


@main.command("list")
@click.pass_context
def list_cmd(ctx: click.Context) -> None:
    """List all snippet."""
    snippets = load_snippets(ctx.obj["file"])
    for snippet in snippets:
        click.echo(snippet.key)


@main.command("new")
def new_cmd() -> None:
    """Create a new snippet."""
    key = click.prompt(click.style("key", fg=PROMPT_KEY_COLOR))
    content = click.prompt(click.style("content", fg=PROMPT_CONTENT_COLOR))
    tags_input = click.prompt(click.style("tags", fg=PROMPT_CONTENT_COLOR), default="")
    tags = [t.strip() for t in tags_input.split(",") if t.strip()]
    save_snippet(Snippet(key=key, content=content, tags=tags))


@main.command("configure")
def configure_cmd() -> None:
    """Create default configuration and open it in your editor."""
    config_path = config_init()
    click.edit(filename=config_path)
