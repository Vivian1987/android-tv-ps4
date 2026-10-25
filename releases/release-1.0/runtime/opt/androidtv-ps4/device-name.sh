#!/system/bin/sh
# Boot-time Android defaults for the PS4. Runs once Android reports boot
# completion, so SettingsProvider is available.
set -eu

# Android sleep locks up PS4 Linux, so idle time runs the screensaver instead
# and never goes to sleep. A screensaver chosen in Settings is kept. This runs
# first so a later failure cannot skip it.
backdrop=com.google.android.apps.tv.dreamx/com.google.android.apps.tv.dreamx.service.Backdrop
case "$(settings get secure screensaver_components)" in
    ''|null)
        settings put secure screensaver_components "$backdrop"
        settings put secure screensaver_default_component "$backdrop"
        ;;
esac
settings put secure screensaver_enabled 1
settings put secure screensaver_activate_on_sleep 1
settings put secure sleep_timeout -1

# Name the device "PlayStation 4" without altering Build.MODEL. The stock
# default is derived from the certified phone model, so the name is set once
# per installation; a name chosen later in setup or Settings is kept.
if [ "$(getprop persist.vendor.androidtv.named)" != 1 ]; then
    if settings put global device_name 'PlayStation 4'; then
        setprop persist.vendor.androidtv.named 1 || true
    fi
fi
