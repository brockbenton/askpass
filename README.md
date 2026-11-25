# askpass

When an AI agent (or any program without a terminal) runs `sudo`, it fails with
"a terminal is required to read the password". `askpass` fixes that: sudo
pops up a dialog showing the exact command and which program asked for it, and
only gets your password if you click **Allow**. Every request is logged, without
the password.

## Setup

Needs `python3`, and on Linux `kdialog` or `zenity`. On a Mac, get python3 with
`xcode-select --install`; dialogs are built in. In a normal terminal:

```bash
./install.sh
```

It installs root-owned files, so agents running as you can't edit them, and prints one
line to add to your shell config. That puts a small `sudo` wrapper first in your PATH,
which uses the dialog only when there is no terminal. Restart your agent, then test from
a normal terminal:

```bash
sudo -k; SUDO_ASKPASS=/usr/local/bin/askpass sudo -A true && echo "it works"
```

**Linux with classic sudo** can skip the wrapper with one system-wide line instead:

```bash
echo "Path askpass /usr/local/bin/askpass" | sudo tee -a /etc/sudo.conf
```

## Where it works

| System | How |
| --- | --- |
| Linux, classic sudo | `sudo.conf` line or wrapper |
| Linux, sudo-rs 0.2.11+ | Wrapper only: sudo-rs has no automatic fallback |
| macOS | Wrapper |

## See what your agents asked for

```bash
cat ~/.local/state/askpass/requests.log
```

Each line has the time, the decision (allowed, blocked or cancelled), which programs
asked, and the command.

## License

MIT
