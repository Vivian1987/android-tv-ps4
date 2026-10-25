/*
 * ps4-kexec - a kexec() implementation for Orbis OS / FreeBSD
 *
 * Copyright (C) 2015-2016 shuffle2 <godisgovernment@gmail.com>
 * Copyright (C) 2015-2016 Hector Martin "marcan" <marcan@marcan.st>
 *
 * This code is licensed to you under the 2-clause BSD license. See the LICENSE
 * file for more information.
 */

.intel_syntax noprefix

.equ setup_sects, 0x1f1
.equ shdr_syssize, 0x1f4
.equ pref_address, 0x258

.text

#void jmp_to_linux(
#    uintptr_t copy_list,       rdi  {src, dst, len} entries, len 0 ends
#    uintptr_t bootargs,        rsi
#    uintptr_t new_cr3,         rdx
#    uintptr_t gdt_ptr          rcx
#);
.globl jmp_to_linux
jmp_to_linux:
    # switch to new gdt + data segments
    cli
    lgdt [rcx]
    #xor eax, eax
    mov eax, 0x18
    mov ds, eax
    mov ss, eax
    mov es, eax
    mov fs, eax
    mov gs, eax

    # switch to our own page tables (in low mem)
    mov cr3, rdx

    # now we're on our own page tables, so we can obliterate the rest of memory
    # save args
    mov r12, rdi
    mov r13, rsi

    # Gather the staged pieces into place: the kernel's protected-mode code
    # at 0x6000000 and the initramfs after the kernel's workspace. The loader
    # guarantees no source piece overlaps any destination.
    cld
1:
    mov rcx, [r12 + 16]             # len
    test rcx, rcx
    jz 2f
    mov rsi, [r12]                  # src
    mov rdi, [r12 + 8]              # dst
    rep movsb
    add r12, 24
    jmp 1b
2:

    # make a tiny stack - we just need it for the lretq.
    # what we jump to will not use this stack
    lea rsp, [rip + jmp_to_linux_end + 0x200]
    and rsp, -0x10
    push 0x10                       # cs = GDT[2]
    mov r14, 0x6000200              # 0x6000000 + startup_64
    push r14                        # rip
    mov rsi, r13                    # bootargs
    lretq
jmp_to_linux_end:

.data

.globl jmp_to_linux_size
jmp_to_linux_size: .quad jmp_to_linux_end - jmp_to_linux

.att_syntax prefix
