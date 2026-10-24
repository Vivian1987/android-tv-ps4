ENTRY(_start)
SECTIONS {
 . = 0;
 .text : { *(.text.start) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) *(.got*) }
 /* Include zero initialized storage in the actual BIN: loaders need no BSS ABI. */
 .bss : { *(.bss*) *(COMMON) BYTE(0); }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) *(.interp) }
}
