/*
 * ps4-kexec - a kexec() implementation for Orbis OS / FreeBSD
 *
 * Copyright (C) 2015-2016 shuffle2 <godisgovernment@gmail.com>
 * Copyright (C) 2015-2016 Hector Martin "marcan" <marcan@marcan.st>
 *
 * This code is licensed to you under the 2-clause BSD license. See the LICENSE
 * file for more information.
 */

#include "kernel.h"
#include "linux_boot.h"
#include "x86.h"
#include "kexec.h"
#include "firmware.h"
#include "string.h"
#include "acpi.h"
#include "../sb_detect.h"
#include "crc32.h"
#include "boot-control.h"
#include "boot-validation.h"

u8 sb_id = 0;

static int k_copyin(const void *uaddr, void *kaddr, size_t len)
{
    if (!uaddr || !kaddr)
        return EFAULT;
    memcpy(kaddr, uaddr, len);
    return 0;
}

static int k_copyinstr(const void *uaddr, void *kaddr, size_t len, size_t *done)
{
    const char *ustr = (const char*)uaddr;
    char *kstr = (char*)kaddr;
    size_t ret;
    if (!uaddr || !kaddr)
        return EFAULT;
    ret = strlcpy(kstr, ustr, len);
    if (ret >= len) {
        if (done)
            *done = len;
        return ENAMETOOLONG;
    } else {
        if (done)
            *done = ret + 1;
    }
    return 0;
}

static int k_copyout(const void *kaddr, void *uaddr, size_t len)
{
    if (!uaddr || !kaddr)
        return EFAULT;
    memcpy(uaddr, kaddr, len);
    return 0;
}

#define KEXEC_VRAM_MASK 0xFFFFu
#define KEXEC_FW_MASK   0xFFFu
#define KEXEC_SB_MASK   0xFu

static u16 kexec_get_vram_mb(int packed)
{
    return (u16)((u32)packed & KEXEC_VRAM_MASK);
}

static u16 kexec_get_fw_ver(int packed)
{
    // Shift past VRAM, then mask for 12 bits
    return (u16)(((u32)packed >> 16) & KEXEC_FW_MASK);
}

static u8 kexec_get_sb_id(int packed)
{
    // Shift to the very end for the 4-bit SB ID
    return (u8)(((u32)packed >> 28) & KEXEC_SB_MASK);
}

static const char* kexec_get_sb_name(u8 id)
{
    switch (id) {
        case SB_AEOLIA:  return "Aeolia";
        case SB_BELIZE:  return "Belize";
        case SB_BAIKAL:  return "Baikal";
        case SB_BELIZE2: return "Belize2";
        default:         return "Unknown Southbridge";
    }
}

static void kexec_print_banner(u16 fw_ver, u16 vram_mb, u8 sb_id)
{
    kern.printf("========================================\n");
    kern.printf("PS4 Linux Payloads AIO\n");
    if (fw_ver) {
        kern.printf("FW %u.%02u (%u)\n",
            (unsigned int)(fw_ver / 100),
            (unsigned int)(fw_ver % 100),
            (unsigned int)fw_ver);
    } else {
        kern.printf("FW unknown\n");
    }
    kern.printf("VRAM %u MB\n", (unsigned int)vram_mb);
    kern.printf("Southbridge: %s\n", kexec_get_sb_name(sb_id));
    kern.printf("========================================\n");
}

static struct atv_boot_report prepared;

/* Staging: the kernel and initramfs are copied in as pieces of up to 2 MiB
 * wherever Orbis has free memory, and the transition stub gathers them into
 * place. Window 0 sits above the gathered layout, window 1 below it. */
#define ATV_PIECE_MAX (2u << 20)
#define ATV_PIECE_MIN (64u << 10)
static struct atv_copy copies[ATV_MAX_COPIES];
static unsigned copy_count, smallest_piece;
static u64 stage_low[2], stage_high[2];

static void *alloc_whole(size_t bytes)
{
    for (unsigned w = 0; w < 2; w++) {
        void *p = kernel_alloc_contig_in(bytes, stage_low[w], stage_high[w], 3);
        if (p) return p;
    }
    kern.printf("ATV boot allocation failed: %zu bytes\n", bytes);
    return NULL;
}

static void *alloc_piece(size_t want, size_t *got)
{
    size_t size = want < ATV_PIECE_MAX ? want : ATV_PIECE_MAX;
    for (;;) {
        for (unsigned w = 0; w < 2; w++) {
            void *p = kernel_alloc_contig_in(size, stage_low[w], stage_high[w], 1);
            if (p) { *got = size; return p; }
        }
        if (size <= ATV_PIECE_MIN) return NULL;
        size = size / 2 > ATV_PIECE_MIN ? size / 2 : ATV_PIECE_MIN;
    }
}

typedef int (*copyin_t)(const void *uaddr, void *kaddr, size_t len);

static int stage(copyin_t copyin, const u8 *user, size_t bytes, u64 dst,
                 u32 *crc, const char *what)
{
    size_t done = 0;
    unsigned first = copy_count;
    while (done < bytes) {
        size_t got;
        void *piece = copy_count < ATV_MAX_COPIES ?
            alloc_piece(bytes - done, &got) : NULL;
        if (!piece) {
            kern.printf("ATV could not stage the %s: %zu of %zu bytes placed in %u pieces\n",
                        what, done, bytes, copy_count - first);
            return ENOMEM;
        }
        int err = copyin(user + done, piece, got);
        if (err) return err;
        *crc = crc32(*crc, piece, got);
        if (!smallest_piece || got < smallest_piece) smallest_piece = got;
        copies[copy_count].src = DM_TO_ID(piece);
        copies[copy_count].dst = dst + done;
        copies[copy_count].len = got;
        copy_count++;
        done += got;
    }
    kern.printf("ATV staged the %s: %zu bytes in %u pieces\n",
                what, bytes, copy_count - first);
    if (what[0] == 'k') prepared.kernel_pieces = copy_count - first;
    else prepared.initrd_pieces = copy_count - first;
    return 0;
}


static void cancel_preparation(void)
{
    kernel_free_all_contig();
    copy_count = 0;
    memset(&prepared, 0, sizeof(prepared));
}

static int boot_control(void *td, struct sys_kexec_args *uap)
{
    if (uap->image_size == ATV_BOOT_QUERY) {
        if (uap->initramfs_size != sizeof(prepared)) return EINVAL;
        return td ? kern.copyout(&prepared, uap->initramfs, sizeof(prepared)) :
                    k_copyout(&prepared, uap->initramfs, sizeof(prepared));
    }
    if (uap->image_size == ATV_BOOT_CANCEL) {
        if (prepared.state == 2) return EINVAL;
        cancel_preparation();
        return 0;
    }
    if (uap->image_size != ATV_BOOT_ARM || prepared.state != 1) return EINVAL;
    /* No display teardown, allocation, or network operation after this call. */
    if (!kernel_hook_install(hook_icc_query_nowait, kern.icc_query_nowait))
        return EINVAL;
    prepared.state = 2;
    kern.printf("ATV handoff hook written and verified; ready for shutdown\n");
    return 0;
}

int sys_kexec(void *td, struct sys_kexec_args *uap)
{
    if (!uap->image) return boot_control(td, uap);
    if (prepared.state || uap->image_size < sizeof(struct boot_params) ||
        uap->image_size > 128 * 1024 * 1024 || !uap->initramfs ||
        !uap->initramfs_size || uap->initramfs_size > 128 * 1024 * 1024)
        return EINVAL;
    int err = 0;
    size_t initramfs_size = uap->initramfs_size;
    void *image = NULL;
    void *firmware = NULL;
    size_t firmware_size = 0;
    struct boot_params *bp = NULL;
    size_t cmd_line_maxlen = 0;
    char *cmd_line = NULL;
    u16 vram_mb = kexec_get_vram_mb(uap->vram_gb);
    u16 fw_ver = kexec_get_fw_ver(uap->vram_gb);
    sb_id = kexec_get_sb_id(uap->vram_gb);

    int (*copyin)(const void *uaddr, void *kaddr, size_t len) = td ? kern.copyin : k_copyin;
    int (*copyinstr)(const void *uaddr, void *kaddr, size_t len, size_t *done) = td ? kern.copyinstr : k_copyinstr;

    struct setup_header header;
    err = copyin((u8 *)uap->image + offsetof(struct boot_params, hdr),
                 &header, sizeof(header));
    if (err) return err;
    u64 initrd_dst, dest_end, allocation_high;
    if (!atv_valid_header(&header, uap->image_size) ||
        !atv_boot_layout(&header, uap->initramfs_size + FW_CPIO_SIZE,
                         &initrd_dst, &dest_end, &allocation_high))
        return EINVAL;
    stage_low[0] = (dest_end + 0x3fff) & ~0x3fffULL;
    stage_high[0] = allocation_high;
    stage_low[1] = ATV_STAGE_FLOOR;
    stage_high[1] = ATV_KERNEL_DEST;
    copy_count = 0;
    smallest_piece = 0;
    prepared.kernel_pieces = prepared.initrd_pieces = 0;
    prepared.smallest_piece = 0;

    // Diagnostic only: would the pre-1.1 loader's single kernel block have
    // been available? Taken from the same window it used, then released
    // straight away so staging sees the same memory.
    int probe = kernel_probe_contig(uap->image_size,
            (ATV_KERNEL_DEST + header.init_size + 0x3fff) & ~0x3fffULL,
            allocation_high);
    prepared.old_method = probe ? 1 : 2;
    kern.printf("ATV old method check: one %zu-byte block %s\n", uap->image_size,
                probe ? "was available" : "was NOT available (old loader: error 12)");
    kern.printf("ATV layout: kernel %llx, initramfs %llx, end %llx; staging %llx..%llx and %llx..%llx\n",
                ATV_KERNEL_DEST, initrd_dst, dest_end, stage_low[0], stage_high[0],
                stage_low[1], stage_high[1]);

    kern.printf("sys_kexec invoked\n");
    kexec_print_banner(fw_ver, vram_mb, sb_id);
    kern.printf("sys_kexec(%p, %zu, %p, %zu, \"%s\")\n", uap->image,
        uap->image_size, uap->initramfs, uap->initramfs_size, uap->cmd_line);

    // Look up our shutdown hook point
    void *icc_query_nowait = kern.icc_query_nowait;
    if (!icc_query_nowait) {
        err = ENOENT;
        goto cleanup;
    }


    // Set gpu frequencies and pstate   
    //                      FAT&SLIM / PRO
    if (kern.gpu_devid_is_9924()){
        // PS4 PRO
        kern.set_gpu_freq(1, 853); //673 //853
        kern.set_gpu_freq(2, 711); //610 //711
        kern.set_gpu_freq(4, 911); //800 //911
        kern.set_gpu_freq(5, 800); //711 //800
        kern.set_gpu_freq(6, 984); //711 //984
        
        kern.set_cu_power_gate(0x24);
    }else{
        // PS4 FAT/SLIM
        kern.set_pstate(3);
        kern.set_gpu_freq(0, 800); //800 //800
        kern.set_gpu_freq(1, 673); //673 //853
        kern.set_gpu_freq(2, 609); //610 //711
        kern.set_gpu_freq(4, 800); //800 //911
        kern.set_gpu_freq(5, 711); //711 //800
        kern.set_gpu_freq(6, 711); //711 //984

        kern.set_cu_power_gate(0x12);
    }
    // Both PRO & FAT/SLIM
    kern.set_pstate(3);
    kern.set_gpu_freq(0, 800); //800 //800
    kern.set_gpu_freq(3, 800); //800 //800
    kern.set_gpu_freq(7, 673); //673 //673
    kern.update_vddnp(0x12);


    // Copy in the kernel's setup sectors whole (boot params are built from
    // them), then stage its protected-mode code in pieces bound for
    // ATV_KERNEL_DEST.
    size_t setup_bytes = ((size_t)header.setup_sects + 1) * 512;
    u32 image_crc = 0, initrd_crc = 0;
    image = alloc_whole(setup_bytes);
    if (!image) {
        kern.printf("Failed to allocate image\n");
        err = ENOMEM;
        goto cleanup;
    }
    err = copyin(uap->image, image, setup_bytes);
    if (err) {
        kern.printf("Failed to copy in image\n");
        goto cleanup;
    }

    if (!atv_valid_header(&((struct boot_params *)image)->hdr, uap->image_size) ||
        ((struct boot_params *)image)->hdr.init_size != header.init_size ||
        ((struct boot_params *)image)->hdr.setup_sects != header.setup_sects ||
        uap->image_size - setup_bytes > header.init_size) {
        kern.printf("ATV invalid Linux boot header; staying in Orbis\n");
        err = EINVAL;
        goto cleanup;
    }
    image_crc = crc32(0, image, setup_bytes);
    err = stage(copyin, (const u8 *)uap->image + setup_bytes,
                uap->image_size - setup_bytes, ATV_KERNEL_DEST, &image_crc,
                "kernel");
    if (err) goto cleanup;

    // The GPU firmware archive goes first in the initramfs, followed by the
    // initramfs from the launcher.
    firmware = alloc_whole(FW_CPIO_SIZE);
    if (!firmware) {
        kern.printf("Failed to allocate initramfs\n");
        err = ENOMEM;
        goto cleanup;
    }

    err = firmware_extract(((u8*)firmware));
    if (err <= 0 || err > FW_CPIO_SIZE) {
        kern.printf("GPU firmware extraction failed; staying in Orbis\n");
        err = EINVAL;
        goto cleanup;
    } else {
        firmware_size = err;
    }
    copies[copy_count].src = DM_TO_ID(firmware);
    copies[copy_count].dst = initrd_dst;
    copies[copy_count].len = firmware_size;
    copy_count++;

    err = stage(copyin, uap->initramfs, initramfs_size,
                initrd_dst + firmware_size, &initrd_crc, "initramfs");
    if (err) goto cleanup;
    initramfs_size += firmware_size;

    // Copy in cmdline
    cmd_line_maxlen = ((struct boot_params *)image)->hdr.cmdline_size + 1;
    cmd_line = alloc_whole(cmd_line_maxlen);
    if (!cmd_line) {
        kern.printf("Failed to allocate cmdline\n");
        err = ENOMEM;
        goto cleanup;
    }
    err = copyinstr(uap->cmd_line, cmd_line, cmd_line_maxlen, NULL);
    if (err) {
        kern.printf("Failed to copy in cmdline\n");
        goto cleanup;
    }
    cmd_line[cmd_line_maxlen - 1] = 0;

    kern.printf("\nkexec parameters:\n");
    kern.printf("    Kernel image size:   %zu bytes\n", uap->image_size);
    kern.printf("    Initramfs size:      %zu bytes (%zu from user)\n",
                initramfs_size, uap->initramfs_size);
    kern.printf("    Kernel command line: %s\n", cmd_line);
    kern.printf("    Kernel setup buffer: %p\n", image);
    kern.printf("    Initramfs at:        %llx\n", initrd_dst);

    // Allocate our boot params
    bp = alloc_whole(sizeof(*bp));
    if (!bp) {
        kern.printf("Failed to allocate bp\n");
        err = ENOMEM;
        goto cleanup;
    }

    // Initialize bp
    // TODO should probably do this from cpu_quiesce_gate, then bp doesn't
    // need to be allocated here, just placed directly into low mem
    set_nix_info(image, bp, initrd_dst, initramfs_size, cmd_line, (int)vram_mb,
                 copies, copy_count);

    prepare_boot_params(bp, image);

    // No staged buffer may sit inside the gathered layout.
    u64 workspace = dest_end - ATV_KERNEL_DEST;
    int layout_ok = atv_valid_range(DM_TO_ID(image), setup_bytes, workspace) &&
        atv_valid_range(DM_TO_ID(bp), sizeof(*bp), workspace) &&
        atv_valid_range(DM_TO_ID(cmd_line), cmd_line_maxlen, workspace) &&
        initrd_dst + initramfs_size <= dest_end;
    for (unsigned i = 0; layout_ok && i < copy_count; i++)
        layout_ok = atv_valid_range(copies[i].src, copies[i].len, workspace);
    if (!layout_ok) {
        kern.printf("ATV invalid physical boot layout; staying in Orbis\n");
        err = EINVAL;
        goto cleanup;
    }
    prepared.magic = ATV_BOOT_REPORT_MAGIC;
    prepared.state = 1;
    prepared.image_pa = ATV_KERNEL_DEST;
    prepared.image_bytes = uap->image_size;
    prepared.initrd_pa = initrd_dst;
    prepared.initrd_bytes = initramfs_size;
    prepared.params_pa = DM_TO_ID(bp);
    prepared.cmdline_pa = DM_TO_ID(cmd_line);
    prepared.hook_address = (uintptr_t)icc_query_nowait;
    prepared.hook_target = (uintptr_t)hook_icc_query_nowait;
    prepared.image_crc32 = image_crc;
    prepared.initrd_crc32 = initrd_crc;
    prepared.firmware_bytes = firmware_size;
    prepared.e820_entries = bp->e820_entries;
    prepared.smallest_piece = smallest_piece;
    kern.printf("ATV Linux prepared; shutdown hook is NOT installed\n");
    return 0;

cleanup:
    prepared.smallest_piece = smallest_piece;
    kernel_free_all_contig();
    copy_count = 0;
    return err;

}

int kexec_init(void *_early_printf, sys_kexec_t *sys_kexec_ptr)
{
    int rv = 0;

    // potentially needed to write early_printf
    u64 flags = intr_disable();
    u64 wp = write_protect_disable();

    if (kernel_init(_early_printf) < 0) {
        rv = -1;
        goto cleanup;
    }

    kern.printf("Installing sys_kexec to system call #%d\n", SYS_KEXEC);
    kernel_syscall_install(SYS_KEXEC, sys_kexec, SYS_KEXEC_NARGS);
    kern.printf("kexec_init() successful\n\n");

    if (sys_kexec_ptr)
        *sys_kexec_ptr = sys_kexec;

cleanup:
    write_protect_restore(wp);
    if (kern.sched_unpin && wp & CR0_WP) {
        // If we're returning to a state with WP enabled, assume the caller
        // wants the thread unpinned. Else the caller is expected to
        // call kern.sched_unpin() manually.
        kern.sched_unpin();
    }
    intr_restore(flags);
    return rv;
}
