/* Observe scanout without retaining DRM master or changing display state.
 * Stop kernel console output only after Android replaces the boot framebuffer.
 */
#include <drm/drm.h>
#include <drm/drm_mode.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static int record(const char *path,const char *text){
 int fd=open(path,O_WRONLY|O_CREAT|O_TRUNC,0600);if(fd<0)return -1;
 int result=write(fd,text,strlen(text))==(ssize_t)strlen(text)?0:-1;
 close(fd);return result;
}
static double elapsed(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec/1e9;}
int main(int argc,char **argv){
 int fd=open("/dev/dri/card0",O_RDONLY|O_CLOEXEC);if(fd<0)return 1;
 /* Opening the primary node can implicitly make us DRM master even with
  * O_RDONLY. Release it BEFORE announcing readiness or waiting for Android.
  * If that cannot be confirmed, close the descriptor and stop observing. */
 if(ioctl(fd,DRM_IOCTL_DROP_MASTER,NULL)){close(fd);return 7;}
 uint32_t ids[16]={0},original[16]={0};struct drm_mode_card_res resources={0};
 resources.crtc_id_ptr=(uintptr_t)ids;resources.count_crtcs=16;
 if(ioctl(fd,DRM_IOCTL_MODE_GETRESOURCES,&resources)||!resources.count_crtcs||resources.count_crtcs>16)return 2;
 for(unsigned i=0;i<resources.count_crtcs;i++){
  struct drm_mode_crtc crtc={.crtc_id=ids[i]};
  if(ioctl(fd,DRM_IOCTL_MODE_GETCRTC,&crtc))return 3;
  original[i]=crtc.fb_id;
  if(argc==2&&!strcmp(argv[1],"--snapshot"))printf("crtc=%u framebuffer=%u active=%u mode=%s\n",ids[i],crtc.fb_id,crtc.mode_valid,crtc.mode.name);
 }
 if(argc==2&&!strcmp(argv[1],"--snapshot")){close(fd);return 0;}
 if(record("/run/androidtv-ps4/display-watch-ready","ready\n"))return 4;
 double start=elapsed();
 while(elapsed()-start<300){
  for(unsigned i=0;i<resources.count_crtcs;i++){
   struct drm_mode_crtc crtc={.crtc_id=ids[i]};
   if(ioctl(fd,DRM_IOCTL_MODE_GETCRTC,&crtc))continue;
   if(crtc.mode_valid&&crtc.fb_id&&crtc.fb_id!=original[i]){
    char text[256];snprintf(text,sizeof(text),"[%.2f seconds] First Android scanout: crtc=%u framebuffer=%u (boot framebuffer=%u) mode=%s refresh=%u clock_khz=%u totals=%ux%u\n",elapsed(),ids[i],crtc.fb_id,original[i],crtc.mode.name,crtc.mode.vrefresh,crtc.mode.clock,crtc.mode.htotal,crtc.mode.vtotal);
    /* No further writes to the Linux console after this point. */
    record("/proc/sys/kernel/printk","1\n");
    int result=record("/run/androidtv-ps4/display-ready",text);close(fd);return result?5:0;
   }
  }
  struct timespec delay={.tv_nsec=10000000};nanosleep(&delay,NULL);
 }
 record("/run/androidtv-ps4/display-watch-failed","No new active framebuffer observed within 300 seconds\n");
 close(fd);return 6;
}
