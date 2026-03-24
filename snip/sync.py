import os
from datetime import datetime, timezone

import click
import requests

from snip.config import load_config
from snip.storage import get_snippets_path

GITHUB_TOKEN_ENV = "SNIP_GITHUB_ACCESS_TOKEN"
GIST_API_URL = "https://api.github.com/gists"


def load_gist_config() -> dict:
    return load_config.get("Gist", {})


def _get_access_token(gist_config: dict) -> str:
    token = os.environ.get(GITHUB_TOKEN_ENV, "") or gist_config.get("access_token", "")
    if not token:
        raise click.ClickException(
            f"Gist access_token is empty.\n"
            f"Go to https://github.com/settings/tokens/new and create an access token (only 'gist' scope needed).\n"
            f"Set access_token in config (snip configure) or export ${GITHUB_TOKEN_ENV}."
        )
    return token


def _get_gist(gist_id: str, file_name: str, token: str) -> tuple[str | None, datetime | None]:
    if not gist_id:
        return None, None
    response = requests.get(f"{GIST_API_URL}/{gist_id}", headers={"Authorization": f"token {token}"})
    if response.status_code == 404:
        raise click.ClickException(f"Gist not found: {gist_id}")
    response.raise_for_status()
    data = response.json()
    files = data.get("files", {})
    if file_name not in files:
        raise click.ClickException(f"{file_name} not found in gist")
    content = files[file_name].get("content", "")
    updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
    return content, updated_at


def _upload(content: str, gist_config: dict, token: str) -> None:
    gist_id = gist_config.get("gist_id", "")
    file_name = gist_config.get("file_name", "snip.toml")
    public = gist_config.get("Public", False)
    payload = {
        "description": "snip snippets",
        "public": public,
        "files": {file_name: {"content": content}},
    }
    headers = {"Authorization": f"token {token}"}
    if gist_id:
        response = requests.patch(f"{GIST_API_URL}/{gist_id}", json=payload, headers=headers)
        response.raise_for_status()
        click.echo("Upload success")
    else:
        response = requests.post(GIST_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        new_id = response.json()["id"]
        click.echo(f'Gist created. Add to your config:\ngist_id = "{new_id}"')


def _download(content: str, snippets_path: str) -> None:
    if os.path.exists(snippets_path):
        with open(snippets_path) as f:
            if f.read() == content:
                click.echo("Already up-to-date")
                return
    os.makedirs(os.path.dirname(snippets_path), exist_ok=True)
    with open(snippets_path, "w") as f:
        f.write(content)
    click.echo("Download success")


def sync() -> None:
    gist_config = load_gist_config()
    token = _get_access_token(gist_config)
    gist_id = gist_config.get("gist_id", "")
    file_name = gist_config.get("file_name", "snip.toml")
    snippets_path = get_snippets_path()

    remote_content, remote_updated_at = _get_gist(gist_id, file_name, token)

    if remote_content and (
        not os.path.exists(snippets_path) or os.path.getsize(snippets_path) == 0
    ):
        _download(remote_content, snippets_path)
        return

    with open(snippets_path) as f:
        local_content = f.read()

    if remote_updated_at is None:
        _upload(local_content, gist_config, token)
        return

    local_updated_at = datetime.fromtimestamp(os.path.getmtime(snippets_path), tz=timezone.utc)
    if local_updated_at > remote_updated_at:
        _upload(local_content, gist_config, token)
    elif remote_updated_at > local_updated_at:
        _download(remote_content, snippets_path)
    else:
        click.echo("Already up-to-date")
