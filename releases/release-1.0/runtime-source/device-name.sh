#!/system/bin/sh
# Set a friendly discovery name without altering Build.MODEL or user data.
# Keep names chosen in Android Settings; migrate only an unset/stock name.
set -eu
current=$(settings get global device_name)
model=$(getprop ro.product.model)
case "$current" in
    ''|null|"$model")
        settings put global device_name 'PlayStation 4'
        [ "$(settings get global device_name)" = 'PlayStation 4' ]
        ;;
esac
