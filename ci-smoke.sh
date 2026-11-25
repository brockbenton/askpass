#!/bin/sh
# CI only: real sudo, no terminal, dialog stubbed to decline. Run as a user who needs a password.
set -eu
cd "$(dirname "$0")"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
py=$(command -v python3)
sed -e "1s|.*|#!$py -I|" -e 's|^if __name__.*|ZENITY = "stub"; confirm = lambda *x: False\n&|' askpass > "$tmp/askpass"
chmod 755 "$tmp/askpass"
out=$(SUDO_ASKPASS="$tmp/askpass" python3 -c 'import subprocess,sys; sys.exit(subprocess.call(sys.argv[1:], start_new_session=True, stdin=subprocess.DEVNULL))' ./sudo-wrapper true 2>&1) && { echo "sudo unexpectedly succeeded"; exit 1; }
echo "$out"
echo "$out" | grep -q 'request was blocked'
