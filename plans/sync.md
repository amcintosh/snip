Add a command line task "sync" that will use the "Gist" configuration in the project config.toml to sync the "snippets.toml" data to the configured github gist file.

Ignore the config "auto_sync" flag for now.

Please use https://github.com/knqyf263/pet/blob/main/sync/sync.go and https://github.com/knqyf263/pet/blob/main/sync/gist.go for a reference as to how the functionality should work. Please ignore all other sync engines in sync.go (ie. build only a gist sync).