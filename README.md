# snip

A CLI tool for storing and searching text snippets.

## Installation

```bash
poetry install
```

## Usage

### Add a snippet

```shell
snip new
key> my snippet
content> echo "hello world"
tags> shell, example
```

### List all snippets

```shell
snip list
Key: my snippet
  Content: echo "hello world"
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

### Configure

Creates a default `config.toml` and opens it in your editor.

```shell
snip configure
```
