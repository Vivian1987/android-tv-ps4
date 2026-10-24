#define BUNDLED_APP_COUNT 3
#define BUNDLED_APP_BYTES 39ULL
struct bundled_app_asset { const char *file; const char *label; uint64_t bytes; };
static const struct bundled_app_asset bundled_apps[BUNDLED_APP_COUNT]={
 {"app-youtube-base.apk","YouTube",13ULL},
 {"app-spotify-base.apk","Spotify",13ULL},
 {"app-spotify-x86_64.apk","Spotify",13ULL}
};
