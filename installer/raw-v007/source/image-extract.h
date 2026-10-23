#ifndef PS4_IMAGE_EXTRACT_H
#define PS4_IMAGE_EXTRACT_H
#include <stdint.h>
const char *ps4_extract_error(void);
int ps4_extract_image(int source,int target,uint64_t offset,uint64_t compressed,
 uint64_t expected,int window_bits,uint32_t checksum,int check_checksum,
 void (*progress)(uint64_t,uint64_t));
#endif
