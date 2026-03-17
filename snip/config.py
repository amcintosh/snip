import os

import click

DEFAULT_CONFIG = """\
[Gist]
  Public = false
  access_token = ""
  auto_sync = false
  file_name = "snip.toml"
  gist_id = ""
"""


def get_config_path() -> str:  # pragma: no cover
    app_dir = click.get_app_dir("snip")
    return os.path.join(app_dir, "config.toml")


def config_init() -> str:
    config_path = get_config_path()
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            f.write(DEFAULT_CONFIG)
    return config_path
