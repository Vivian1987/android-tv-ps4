#ifndef ATV_BOOT_CONTROL_H
#define ATV_BOOT_CONTROL_H
/* Private protocol on syscall 153. A NULL image distinguishes control calls
 * from preparation. No control operation requests shutdown. */
#define ATV_BOOT_QUERY  0x41545601ULL
#define ATV_BOOT_ARM    0x41545602ULL
#define ATV_BOOT_CANCEL 0x41545603ULL
#define ATV_BOOT_REPORT_MAGIC 0x41545631U
struct atv_boot_report {
    unsigned int magic, state; /* 0 empty, 1 prepared, 2 armed */
    unsigned long long image_pa, image_bytes, initrd_pa, initrd_bytes;
    unsigned long long params_pa, cmdline_pa, hook_address, hook_target;
    unsigned int image_crc32, initrd_crc32, firmware_bytes, e820_entries;
};
_Static_assert(sizeof(struct atv_boot_report) == 88, "boot report ABI");
#endif
