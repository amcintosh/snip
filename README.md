# snip

A CLI tool for storing and searching text snippets.

## Installation

```bash
poetry install
```

## Usage

```shell
> snip
Usage: snip [OPTIONS] COMMAND [ARGS]...

  Simple tool for storing and searching text snippets.

Options:
  --help  Show this message and exit.

Commands:
  configure  Edit config file
  list       List all snippets.
  new        Create a new snippet
  search     Search for a snippet and print its content.
```

### Setup

Creates a default `config.toml` and opens it in your editor.

```shell
> snip configure
```

### Add a snippet

```shell
> snip new
key> my snippet
content> hello world
tags> shell, example
```

### List all snippets

```shell
> snip list
Key: my snippet
  Content: hello world
  Tags: shell, example
------------------------------
```

### Search for a snippet

Searches by key and copies the top result to the clipboard (macOS).

```shell
snip search my snippet
snip my snippet        # shorthand, search is the default command
```

Options:

- `-c`, `--case-sensitive` — use case-sensitive matching
- `-n`, `--no-clipboard` — print result without copying to clipboard
