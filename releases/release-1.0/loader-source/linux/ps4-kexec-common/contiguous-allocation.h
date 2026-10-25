/* Keep ownership of the original kernel VA. The Linux boot code receives a
 * DMAP alias, but kmem_free must receive the allocation's original VA/size.
 * The four boot buffers remain owned until shutdown or explicit failure cleanup.
 */
struct boot_allocation { void *alias; vm_offset_t original; size_t bytes; };
static struct boot_allocation boot_allocations[4];
static vm_paddr_t boot_low, boot_high;

int kernel_set_allocation_range(vm_paddr_t low, vm_paddr_t high)
{
    if (!low || high <= low) return 0;
    for (unsigned slot = 0; slot < 4; slot++)
        if (boot_allocations[slot].alias) return 0;
    boot_low = low;
    boot_high = high;
    return 1;
}

/* Allocate inside [low, high). Buffers Linux reads in place (initramfs,
 * command line, boot params) use the boot window. The kernel image is only a
 * staging copy that jmp_to_linux moves with 64-bit addresses, so it can come
 * from high memory and leave the crowded low window to the initramfs. */
void *kernel_alloc_contig_in(size_t size, vm_paddr_t low, vm_paddr_t high)
{
    unsigned slot;
    for (slot = 0; slot < 4; slot++)
        if (!boot_allocations[slot].alias) break;
    if (!size || slot == 4 || high <= low || size > high - low) return NULL;

    for (unsigned attempt = 1; attempt <= 3; attempt++) {
        kern.printf("ATV boot allocation: %zu bytes in %llx..%llx, attempt %u/3\n",
                    size, (unsigned long long)low, (unsigned long long)high, attempt);
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
        kern.printf("ATV boot allocation ready: %zu bytes at physical %llx\n",
                    size, (unsigned long long)physical);
        return alias;
    }
    kern.printf("ATV boot allocation failed: %zu bytes; shutdown not armed\n", size);
    return NULL;
}

void *kernel_alloc_contig(size_t size)
{
    return kernel_alloc_contig_in(size, boot_low, boot_high);
}

void kernel_free_contig(void *alias, size_t size)
{
    (void)size;
    if (!alias) return;
    for (unsigned slot = 0; slot < 4; slot++) {
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
