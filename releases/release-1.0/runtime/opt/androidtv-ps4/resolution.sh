# WindowManager is unavailable during init.sh eglsetup and post-fs.
# Apply the TV image's display preference only after framework startup.
if [ "$(getprop sys.boot_completed)" = 1 ]; then
    wm size 1920x1080
    wm density 320
fi
