#ifndef PS4_INSTALLER_UI_H
#define PS4_INSTALLER_UI_H
#include <stdint.h>
int installer_ui_init(void);
void installer_ui_status(const char *message);
void installer_ui_progress(uint64_t written, uint64_t total);
void installer_ui_boot_status(const char *message, const char *detail);
int installer_ui_close(void);
#endif
