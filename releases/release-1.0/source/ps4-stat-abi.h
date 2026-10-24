#ifndef PS4_STAT_ABI_H
#define PS4_STAT_ABI_H
/* OpenOrbis 0.5.4 declares mode_t twice; the first (32-bit) wins.
 * Orbis/FreeBSD9 stat uses a 16-bit mode_t. A 32-bit mode shifts size
 * from byte 72 to byte 80, making st_size read st_blocks instead.
 * Set the native type before any SDK header can define it. */
#ifdef __FreeBSD__
#ifdef __DEFINED_mode_t
#error ps4-stat-abi.h must precede SDK headers
#endif
typedef unsigned short mode_t;
#define __DEFINED_mode_t
#include <sys/stat.h>
#include <stddef.h>
_Static_assert(sizeof(mode_t)==2,"Orbis mode_t ABI");
_Static_assert(offsetof(struct stat,st_mode)==8,"Orbis stat mode ABI");
_Static_assert(offsetof(struct stat,st_size)==72,"Orbis stat size ABI");
_Static_assert(offsetof(struct stat,st_blocks)==80,"Orbis stat blocks ABI");
_Static_assert(sizeof(struct stat)==120,"Orbis stat size");
#endif
#endif
