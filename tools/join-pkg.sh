#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

expected=5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25
output=Android-TV-for-PS4.pkg
partial=
cleanup() { [ -z "$partial" ] || rm -f -- "$partial"; }
trap cleanup EXIT
trap 'exit 1' HUP INT TERM
fail() { printf '\n%s\n' "$*" >&2; exit 1; }
hash() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{print $1}'
    else
        fail 'No SHA256 tool found. Install sha256sum or shasum.'
    fi
}

printf 'Android TV for PS4 1.0\n\n'
if [ -e "$output" ]; then
    printf 'A PKG already exists. Checking it without replacing it...\n'
    [ "$(hash "$output")" = "$expected" ] || fail 'The existing PKG is different or cannot be checked. Move it out of this folder, then run this tool again.'
else
    for part in 1 2; do
        file="Android-TV-for-PS4.pkg.part$part"
        [ -f "$file" ] || fail "Missing $file. Put both downloads beside this tool."
        case "$part" in 1) size=1610612736 ;; 2) size=1497694208 ;; esac
        actual=$(wc -c < "$file" | tr -d '[:space:]')
        [ "$actual" = "$size" ] || fail "$file has the wrong size. Finish the download or download it again."
    done
    printf 'Step 1 of 2: Joining downloads. Allow about 3.2 GB of additional free space.\n'
    partial=$(mktemp './.Android-TV-for-PS4.pkg.joining.XXXXXXXX')
    cat Android-TV-for-PS4.pkg.part1 Android-TV-for-PS4.pkg.part2 > "$partial" || fail 'Could not join downloads. Check free space and folder permissions.'
    printf 'Step 2 of 2: Checking the completed package SHA256...\n'
    [ "$(hash "$partial")" = "$expected" ] || fail 'Verification failed. Do not install this output. Download both parts again.'
    mv -n "$partial" "$output" || fail 'Could not save the PKG. Check folder permissions.'
    [ ! -e "$partial" ] || fail 'Another PKG appeared while joining. It has been left unchanged.'
    partial=
fi

printf '\nREADY: %s\nSHA256 verified. Both downloaded parts have been kept.\n\n' "$output"
printf 'Copy the PKG to the top level of an exFAT USB drive.\n'
printf 'Load GoldHEN on the PS4 and install it with the Package Installer.\n'
printf 'Enable BinLoader on port 9090, then open Android TV for PS4.\n'
printf 'Allow 5–10 minutes for first installation and boot; about 2 minutes later.\n'
