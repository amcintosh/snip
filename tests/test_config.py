from unittest.mock import mock_open, patch

import pytest

from snip.config import DEFAULT_CONFIG, config_init, load_config

CONFIG_PATH = "/mock/snip/config.toml"


def test_config_init__creates_config_with_defaults():
    mock_file = mock_open()
    with (
        patch("snip.config.get_config_path", return_value=CONFIG_PATH),
        patch("snip.config.os.path.exists", return_value=False),
        patch("snip.config.os.makedirs"),
        patch("builtins.open", mock_file),
    ):
        result = config_init()
    mock_file().write.assert_called_once_with(DEFAULT_CONFIG)
    assert result == CONFIG_PATH


def test_config_init__does_not_overwrite_existing():
    mock_file = mock_open()
    with (
        patch("snip.config.get_config_path", return_value=CONFIG_PATH),
        patch("snip.config.os.path.exists", return_value=True),
        patch("builtins.open", mock_file),
    ):
        config_init()
    mock_file().write.assert_not_called()


def test_load_config():
    gist_data = {"access_token": "tok", "gist_id": "abc", "file_name": "snip.toml", "Public": False}
    with (
        patch("snip.config.get_config_path", return_value=CONFIG_PATH),
        patch("snip.config.os.path.exists", return_value=True),
        patch("builtins.open", mock_open()),
        patch("snip.config.tomllib.load", return_value={"Gist": gist_data}),
    ):
        result = load_config()
    assert result == {"Gist": gist_data}


def test_load_config__raises_when_no_config():
    with (
        patch("snip.config.get_config_path", return_value=CONFIG_PATH),
        patch("snip.config.os.path.exists", return_value=False),
    ):
        from click import ClickException

        with pytest.raises(ClickException, match="Config not found"):
            load_config()
