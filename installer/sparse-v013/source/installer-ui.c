/* Native Orbis display; installation remains on the PS4's internal disk. */
#include "installer-ui.h"
#include <orbis/libkernel.h>
#include <orbis/VideoOut.h>
#include <orbis/SystemService.h>
#include <sys/time.h>
#include "installer-font.h"
#include <stdio.h>
#include <string.h>
#include "installer-artwork.h"
#define WIDTH 1280
#define HEIGHT 720
#define FRAME_BYTES (WIDTH*HEIGHT*4)
#define MEMORY_BYTES (8*1024*1024)
static int video=-1, buffer_index, frame_id, displayed_percent=-1;
static off_t memory_offset;
static void *memory;
static uint32_t *buffers[2];
static char status[256]="Checking installation and free space";
static uint64_t done_bytes,total_bytes;
static void rectangle(int x,int y,int w,int h,uint32_t color){
 for(int row=y;row<y+h&&row<HEIGHT;row++){
  if(row<0)continue;
  for(int col=x;col<x+w&&col<WIDTH;col++)if(col>=0)buffers[buffer_index][row*WIDTH+col]=color;
 }
}
static void log_result(const char *op,int rc){
 char message[160];snprintf(message,sizeof(message),"[PS4ATV UI] %s: 0x%x\n",op,(unsigned)rc);sceKernelDebugOutText(0,message);
}
static void text(int x,int y,int scale,const char *message,uint32_t color){
 const unsigned char *atlas=scale==3?font34:font22;
 const unsigned char *advance=scale==3?advance34:advance22;
 for(const unsigned char *p=(const unsigned char*)message;*p;p++){
  unsigned ch=*p>=32&&*p<=126?*p-32:'?'-32;
  for(int yy=0;yy<48&&y+yy<HEIGHT;yy++)for(int xx=0;xx<40&&x+xx<WIDTH;xx++){
   if(x+xx<0||y+yy<0)continue;
   unsigned alpha=atlas[yy*3800+ch*40+xx];if(!alpha)continue;
   uint32_t *dst=&buffers[buffer_index][(y+yy)*WIDTH+x+xx],bg=*dst;
   unsigned r=(((color>>16)&255)*alpha+((bg>>16)&255)*(255-alpha))/255;
   unsigned g=(((color>>8)&255)*alpha+((bg>>8)&255)*(255-alpha))/255;
   unsigned b=((color&255)*alpha+(bg&255)*(255-alpha))/255;
   *dst=0xff000000|(r<<16)|(g<<8)|b;
  }
  x+=advance[ch];
 }
}
static double seconds(void){struct timeval tv;gettimeofday(&tv,NULL);return tv.tv_sec+tv.tv_usec/1000000.;}
static double started,last_draw;
static int splash_hidden;
static void render(void){
 if(video<0)return;
 memcpy(buffers[buffer_index],installer_artwork,FRAME_BYTES);
 text(80,255,3,"Android TV setup",0xfff4f8fa);
 /* Wrap status by words to keep errors and stage descriptions readable. */
 char line[90];const char *p=status;int y=315;
 while(*p&&y<410){size_t n=strlen(p);if(n>85){n=85;while(n>0&&p[n]!=' ')n--;if(!n)n=85;}
  memcpy(line,p,n);line[n]=0;text(80,y,2,line,0xffa6bdca);p+=n;while(*p==' ')p++;y+=30;}
 rectangle(80,435,1120,16,0xff2b4252);
 int percent=total_bytes?(int)(done_bytes*100/total_bytes):0;
 rectangle(80,435,1120*percent/100,16,0xff6ba5d7);
 char detail[160];
 if(total_bytes)snprintf(detail,sizeof(detail),"%d%%   %.1f / %.1f GiB written",percent,(double)done_bytes/1073741824.,(double)total_bytes/1073741824.);
 else snprintf(detail,sizeof(detail),"Preparing the next step; progress appears during file transfer");
 text(80,475,2,detail,0xfff4f8fa);
 if(started&&total_bytes&&done_bytes<total_bytes){
  double elapsed=seconds()-started;
  if(elapsed>1&&done_bytes){double rate=done_bytes/elapsed;
   snprintf(detail,sizeof(detail),"%.1f MiB/s average  |  About %.0f minutes remaining for file transfer",rate/1048576.,(total_bytes-done_bytes)/rate/60.);
   text(80,515,2,detail,0xffa6bdca);
  }
 }
 int stage=strstr(status,"Booting")||strstr(status,"System installed")?2:
  strstr(status,"graphics")||strstr(status,"first-boot")?1:0;
 text(80,575,2,"01  SYSTEM FILES",stage==0?0xfff4f8fa:0xffa6bdca);
 text(430,575,2,"02  GRAPHICS & BOOT",stage==1?0xfff4f8fa:0xffa6bdca);
 text(860,575,2,"03  START ANDROID",stage==2?0xfff4f8fa:0xffa6bdca);
 text(80,620,2,"Keep the console powered on while setup is running.",0xffa6bdca);
 int id=++frame_id;
 int rc=sceVideoOutSubmitFlip(video,buffer_index,ORBIS_VIDEO_OUT_FLIP_VSYNC,id);
 if(rc<0){log_result("submit flip",rc);return;}
 for(int i=0;i<200;i++){OrbisVideoOutFlipStatus flip;
  if(sceVideoOutGetFlipStatus(video,&flip)<0||flip.flipArg==id)break;
  sceKernelUsleep(5000);
 }
 if(!splash_hidden){int rc=sceSystemServiceHideSplashScreen();log_result("hide splash",rc);if(rc>=0)splash_hidden=1;}
 buffer_index^=1;
}
int installer_ui_init(void){
 video=sceVideoOutOpen(ORBIS_VIDEO_USER_MAIN,ORBIS_VIDEO_OUT_BUS_MAIN,0,NULL);
 log_result("open VideoOut",video);if(video<0)return -1;
 if(sceKernelAllocateDirectMemory(0,sceKernelGetDirectMemorySize(),MEMORY_BYTES,0x200000,3,&memory_offset)<0)goto failed;
 if(sceKernelMapDirectMemory(&memory,MEMORY_BYTES,0x33,0,memory_offset,0x200000)<0){sceKernelReleaseDirectMemory(memory_offset,MEMORY_BYTES);goto failed;}
 buffers[0]=memory;buffers[1]=(uint32_t*)((char*)memory+FRAME_BYTES);
 OrbisVideoOutBufferAttribute attr;
 sceVideoOutSetBufferAttribute(&attr,0x80000000,1,0,WIDTH,HEIGHT,WIDTH);
 int rc=sceVideoOutRegisterBuffers(video,0,(void**)buffers,2,&attr);log_result("register buffers",rc);if(rc<0){installer_ui_close();return -1;}
 render();return 0;
failed:sceVideoOutClose(video);video=-1;return -1;
}
void installer_ui_status(const char *message){snprintf(status,sizeof(status),"%s",message);render();}
void installer_ui_progress(uint64_t written,uint64_t total){
 if(!started)started=seconds();done_bytes=written;total_bytes=total;int percent=total?(int)(written*100/total):0;
 if(percent!=displayed_percent||seconds()-last_draw>=1){displayed_percent=percent;last_draw=seconds();
  render();}
}
void installer_ui_close(void){
 if(video>=0){sceVideoOutClose(video);video=-1;}
 if(memory){sceKernelMunmap(memory,MEMORY_BYTES);sceKernelReleaseDirectMemory(memory_offset,MEMORY_BYTES);memory=NULL;}
}
