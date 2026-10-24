#ifndef ATV_DISPLAY_RELEASE_H
#define ATV_DISPLAY_RELEASE_H
#include "launch-protocol.h"
/* Only an explicit, matching release advances boot. Elapsed time can abort it,
 * never authorize it. Used by the actual GoldHEN runner and the host tests. */
static int atv_wait_display_release(unsigned long long nonce,
 int (*read_control)(struct atv_launch_control *),
 unsigned long long (*clock_us)(void),int (*sleep_us)(unsigned)){
 unsigned long long start=clock_us();
 while(clock_us()-start<60000000ULL){
  struct atv_launch_control c;
  if(read_control(&c)||!atv_control_valid(&c,nonce))return -111;
  if(c.cancelled)return -112;
  if(c.released==1)return 0;
  sleep_us(10000);
 }
 return -113;
}
#endif
