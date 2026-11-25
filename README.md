# askpass

When an AI agent (or any program without a terminal) runs `sudo`, it fails with
"a terminal is required to read the password". `askpass` fixes that: sudo
pops up a dialog showing the exact command and which program asked for it, and
only gets your password if you click **Allow**. Every request is logged, without
the password.

## Setup (about 2 minutes)

1. **Make sure you have a dialog tool.** GNOME usually ships `zenity`; KDE ships `kdialog`.

   ```bash
   command -v zenity || command -v kdialog || sudo apt install zenity
   ```

2. **Install the script.** It goes in a root-owned directory so that agents running
   as you can't edit it. You also need `python3`. Run this and the next step in a
   normal terminal:

   ```bash
   sudo install -m 755 askpass /usr/local/bin/askpass
   ```

3. **Tell sudo to use it.** This adds one line to `/etc/sudo.conf`, which works for
   every program, including agents:

   ```bash
   echo "Path askpass /usr/local/bin/askpass" | sudo tee -a /etc/sudo.conf
   ```

   Alternative: set `SUDO_ASKPASS=/usr/local/bin/askpass` in your shell's config and
   restart your agent from a new terminal.

4. **Test it.** This runs sudo detached from your terminal, the way an agent does:

   ```bash
   sudo -k && setsid -w sudo true < /dev/null && echo "it works"
   ```

   The dialog should appear. Click Allow, enter your password, and you'll see "it works".

Your agent's `sudo` commands, like the battery threshold one, will now show the dialog
instead of failing.

## See what your agents asked for

```bash
cat ~/.local/state/askpass/requests.log
```

Each line has the time, the decision (allowed, blocked or cancelled), which programs
asked, and the command.

## Good to know

- **It needs a desktop session.** sudo only uses the helper when `DISPLAY` or
  `WAYLAND_DISPLAY` is set. Over plain SSH it still fails.
- **sudo may remember an approval for a few minutes,** so later sudo commands from the
  same session can run without a dialog. To be asked every time, run
  `sudo visudo -f /etc/sudoers.d/askpass` and add `Defaults timestamp_timeout=0`.
  This also makes your own terminal ask every time.
- **Only enter your password in a dialog you expected.** Read the command before
  clicking Allow.
- **It shows sudo's arguments, not piped input.** For `echo 96 | sudo tee FILE` you
  see `sudo tee FILE`, not the `96`. Likewise, it shows a script's name, not its contents.
- **It stops surprises, not malware.** A hostile program running as you can set its own
  `SUDO_ASKPASS` or fake a dialog. The program names shown can be faked too.
- **Dialogs time out after 2 minutes** and commands over 2000 characters are blocked,
  because they can't be shown in full.
- **The log contains command arguments,** so don't put secrets in them.
- **To uninstall,** delete the `Path askpass` line from `/etc/sudo.conf` (or the
  `SUDO_ASKPASS` export) and remove `/usr/local/bin/askpass`.
