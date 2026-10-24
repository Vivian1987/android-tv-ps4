/* The PS4 display path is validated at 60 Hz. Filter connector modes BEFORE
 * SurfaceFlinger starts, including boot animation before DisplayManager policy.
 * Used only by the drmfb composer through its service's LD_PRELOAD setting.
 * This does not alter framebuffer allocation, composition or page-flip code. */
#include <stddef.h>
#ifdef __ANDROID__
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef unsigned long long uint64_t;
extern void *dlsym(void *,const char *);
#define RTLD_NEXT ((void *)-1L)
#else
#include <stdint.h>
#include <dlfcn.h>
#endif

/* Stable public libdrm ABI, xf86drmMode.h. */
struct atv_mode {
 uint32_t clock;
 uint16_t hdisplay,hsync_start,hsync_end,htotal,hskew;
 uint16_t vdisplay,vsync_start,vsync_end,vtotal,vscan;
 uint32_t vrefresh,flags,type;
 char name[32];
};
struct atv_connector {
 uint32_t connector_id,encoder_id,connector_type,connector_type_id;
 int connection;
 uint32_t mmWidth,mmHeight;
 int subpixel,count_modes;
 struct atv_mode *modes;
 int count_props;
 uint32_t *props;
 uint64_t *prop_values;
 int count_encoders;
 uint32_t *encoders;
};
_Static_assert(sizeof(struct atv_mode)==68,"libdrm mode ABI");
_Static_assert(offsetof(struct atv_connector,modes)==40,"libdrm connector ABI");
static int atv_filter_modes(struct atv_connector *c){
 if(!c||c->count_modes<=0||!c->modes)return 0;
 int kept=0;
 for(int i=0;i<c->count_modes;i++){
  const struct atv_mode *m=&c->modes[i];
  if(!m->vrefresh||m->vrefresh>60||(m->flags&((1U<<4)|(1U<<5))))continue;
  c->modes[kept++]=*m;
 }
 c->count_modes=kept;
 return kept;
}
__attribute__((visibility("default")))
struct atv_connector *drmModeGetConnector(int fd,uint32_t id){
 struct atv_connector *(*next)(int,uint32_t)=dlsym(RTLD_NEXT,"drmModeGetConnector");
 if(!next)return NULL;
 struct atv_connector *c=next(fd,id);atv_filter_modes(c);return c;
}
__attribute__((visibility("default")))
struct atv_connector *drmModeGetConnectorCurrent(int fd,uint32_t id){
 struct atv_connector *(*next)(int,uint32_t)=dlsym(RTLD_NEXT,"drmModeGetConnectorCurrent");
 if(!next)return NULL;
 struct atv_connector *c=next(fd,id);atv_filter_modes(c);return c;
}
