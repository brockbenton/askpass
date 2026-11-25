#!/bin/sh
# Usage: ./install.sh [--uninstall]   (run in a normal terminal)
set -eu
cd "$(dirname "$0")"
BIN=/usr/local/bin
WRAP=/usr/local/lib/askpass

if [ "${1-}" = --uninstall ]; then
    sudo rm -f "$BIN/askpass" "$WRAP/sudo"
    [ ! -d "$WRAP" ] || sudo rmdir "$WRAP"
    echo "Removed. Also delete any askpass line from /etc/sudo.conf and $WRAP from your PATH."
    exit 0
fi

for py in /usr/bin/python3 /usr/local/bin/python3 /run/current-system/sw/bin/python3 ''; do
    [ -x "$py" ] && break
done
[ -n "$py" ] || { echo "Install python3 first." >&2; exit 1; }
"$py" -c 'import sys; sys.exit(sys.version_info < (3, 6))' || { echo "Needs a working python3 3.6+." >&2; exit 1; }
if [ "$(uname)" != Darwin ] && ! command -v kdialog >/dev/null && ! command -v zenity >/dev/null; then
    echo "Install kdialog or zenity first." >&2; exit 1
fi

tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT
sed "1s|.*|#!$py -I|" askpass > "$tmp"
sudo mkdir -p "$BIN" "$WRAP"
sudo install -m 755 "$tmp" "$BIN/askpass"
sudo install -m 755 sudo-wrapper "$WRAP/sudo"
cat <<MSG
Installed. Last step: put the wrapper first in your PATH, then restart your agent.
  zsh:  echo 'export PATH="$WRAP:\$PATH"' >> ~/.zshenv
  bash: echo 'export PATH="$WRAP:\$PATH"' >> ~/.bashrc
  fish: fish_add_path --prepend $WRAP
MSG
