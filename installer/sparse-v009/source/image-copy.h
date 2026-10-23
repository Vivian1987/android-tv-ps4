#ifndef PS4_IMAGE_COPY_H
#define PS4_IMAGE_COPY_H
#include <stdint.h>
int ps4_copy_image(int source, int target, uint64_t expected_size,
                   void (*progress)(uint64_t,uint64_t));
#endif
