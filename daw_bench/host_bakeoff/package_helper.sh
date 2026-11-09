#!/bin/sh
# Packages the plughost helper as a background (LSUIElement) .app, signed ad-hoc with Hardened
# Runtime and the entitlements plughost requires (adapted from plughost's
# scripts/macos/package-app.sh, MIT OR Apache-2.0). Prints the executable path to pass to host_rs.
# usage: package_helper.sh <built plughost-helper binary> <output dir>
set -eu
here=$(cd "$(dirname "$0")" && pwd)
exe=$1
app="$2/PlughostHelper.app"
rm -rf "$app"
mkdir -p "$app/Contents/MacOS"
sed -e "s/@EXECUTABLE@/plughost-helper/g" -e "s/@IDENTIFIER@/com.serumllm.bakeoff.helper/g" \
    -e "s/@VERSION@/0.2.1/g" "$here/macos/Info.plist" > "$app/Contents/Info.plist"
cp "$exe" "$app/Contents/MacOS/plughost-helper"
codesign --force --sign - --options runtime --entitlements "$here/macos/helper.entitlements" "$app"
echo "$app/Contents/MacOS/plughost-helper"
