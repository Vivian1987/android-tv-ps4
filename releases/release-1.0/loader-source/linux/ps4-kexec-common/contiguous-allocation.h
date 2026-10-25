/* Keep ownership of the original kernel VA. The Linux boot code receives a
 * DMAP alias, but kmem_free must receive the allocation's original VA/size.
 * Boot buffers remain owned until shutdown or explicit failure cleanup.
 *
 * The kernel image and initramfs are staged in pieces rather than as two
 * large contiguous blocks: a busy or Pro console often has no single free
 * run of 10+ MiB in low memory, but always has plenty of smaller ones. The
 * transition stub gathers the pieces into place once Orbis is gone.
 */
#define ATV_BOOT_SLOTS 192
struct boot_allocation { void *alias; vm_offset_t original; size_t bytes; };
static struct boot_allocation boot_allocations[ATV_BOOT_SLOTS];
static vm_paddr_t boot_low, boot_high;

int kernel_set_allocation_range(vm_paddr_t low, vm_paddr_t high)
{
    if (!low || high <= low) return 0;
    for (unsigned slot = 0; slot < ATV_BOOT_SLOTS; slot++)
        if (boot_allocations[slot].alias) return 0;
    boot_low = low;
    boot_high = high;
    return 1;
}

void *kernel_alloc_contig_in(size_t size, vm_paddr_t low, vm_paddr_t high,
                             unsigned tries)
{
    unsigned slot;
    for (slot = 0; slot < ATV_BOOT_SLOTS; slot++)
        if (!boot_allocations[slot].alias) break;
    if (!size || slot == ATV_BOOT_SLOTS || high <= low || size > high - low)
        return NULL;

    for (unsigned attempt = 1; attempt <= tries; attempt++) {
        vm_offset_t raw = kern.kmem_alloc_contig(*kern.kernel_map, size,
                M_ZERO | M_WAITOK, low, high, 0x4000, 0,
                VM_MEMATTR_DEFAULT);
        if (!raw) continue;
        vm_paddr_t physical = kern.pmap_extract(kern.kernel_pmap_store, raw);
        if (physical < low || physical >= high ||
            size > high - physical) {
            kern.kmem_free(*kern.kernel_map, raw, size);
            return NULL;
        }
        void *alias = (void *)PA_TO_DM(physical);
        boot_allocations[slot].alias = alias;
        boot_allocations[slot].original = raw;
        boot_allocations[slot].bytes = size;
        return alias;
    }
    return NULL;
}

void *kernel_alloc_contig(size_t size)
{
    void *alias = kernel_alloc_contig_in(size, boot_low, boot_high, 3);
    if (!alias)
        kern.printf("ATV boot allocation failed: %zu bytes\n", size);
    return alias;
}

void kernel_free_contig(void *alias, size_t size)
{
    (void)size;
    if (!alias) return;
    for (unsigned slot = 0; slot < ATV_BOOT_SLOTS; slot++) {
        if (boot_allocations[slot].alias != alias) continue;
        kern.kmem_free(*kern.kernel_map, boot_allocations[slot].original,
                boot_allocations[slot].bytes);
        boot_allocations[slot].alias = NULL;
        boot_allocations[slot].original = 0;
        boot_allocations[slot].bytes = 0;
        return;
    }
    kern.printf("ATV refused to free an unowned boot buffer\n");
}

void kernel_free_all_contig(void)
{
    for (unsigned slot = 0; slot < ATV_BOOT_SLOTS; slot++)
        if (boot_allocations[slot].alias)
            kernel_free_contig(boot_allocations[slot].alias, 0);
}

/* Whether one block of `size` is free in [low, high) right now, without
 * waiting for Orbis to reclaim memory (a miss with M_WAITOK stalls for about
 * 15 seconds); the block is released immediately. */
int kernel_probe_contig(size_t size, vm_paddr_t low, vm_paddr_t high)
{
    vm_offset_t raw = kern.kmem_alloc_contig(*kern.kernel_map, size, M_NOWAIT,
            low, high, 0x4000, 0, VM_MEMATTR_DEFAULT);
    if (!raw) return 0;
    kern.kmem_free(*kern.kernel_map, raw, size);
    return 1;
}
