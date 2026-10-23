/* Native Orbis display; installation remains on the PS4's internal disk. */
#include "installer-ui.h"
#include <orbis/libkernel.h>
#include <orbis/VideoOut.h>
#include <stb/stb_easy_font.h>
#include <stdio.h>
#include <string.h>
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
static void text(int x,int y,int scale,const char *message,uint32_t color){
 struct vertex {float x,y,z;unsigned char rgba[4];};
 static struct vertex vertices[8192];
 char copy[256];snprintf(copy,sizeof(copy),"%s",message);
 int count=stb_easy_font_print(0,0,copy,NULL,vertices,sizeof(vertices));
 for(int i=0;i<count;i++){
  struct vertex *v=vertices+i*4;
  rectangle(x+(int)(v[0].x*scale),y+(int)(v[0].y*scale),
            (int)((v[2].x-v[0].x)*scale),(int)((v[2].y-v[0].y)*scale),color);
 }
}
static void render(void){
 if(video<0)return;
 rectangle(0,0,WIDTH,HEIGHT,0xff10202c);
 text(80,70,4,"PS4 ANDROID TV",0xfff4f8fa);
 text(80,135,2,"ANDROID 13 / INTERNAL HDD SETUP",0xffa6bdca);
 text(80,230,3,"Setup progress",0xfff4f8fa);
 /* Wrap status by words to keep errors and stage descriptions readable. */
 char line[73];const char *p=status;int y=300;
 while(*p&&y<390){size_t n=strlen(p);if(n>70){n=70;while(n>0&&p[n]!=' ')n--;if(!n)n=70;}
  memcpy(line,p,n);line[n]=0;text(80,y,2,line,0xffa6bdca);p+=n;while(*p==' ')p++;y+=30;}
 rectangle(80,420,1120,30,0xff2b4252);
 int percent=total_bytes?(int)(done_bytes*100/total_bytes):0;
 rectangle(80,420,1120*percent/100,30,0xff50ddb0);
 char detail[160];
 if(total_bytes)snprintf(detail,sizeof(detail),"%d%%   %.1f / %.1f GiB written",percent,(double)done_bytes/1073741824.,(double)total_bytes/1073741824.);
 else snprintf(detail,sizeof(detail),"Checking existing installation before making changes");
 text(80,480,2,detail,0xfff4f8fa);
 text(80,620,2,"Keep the console powered on while setup is running.",0xffa6bdca);
 int id=++frame_id;
 if(sceVideoOutSubmitFlip(video,buffer_index,ORBIS_VIDEO_OUT_FLIP_VSYNC,id)<0)return;
 for(int i=0;i<200;i++){OrbisVideoOutFlipStatus flip;
  if(sceVideoOutGetFlipStatus(video,&flip)<0||flip.flipArg==id)break;
  sceKernelUsleep(5000);
 }
 buffer_index^=1;
}
int installer_ui_init(void){
 video=sceVideoOutOpen(ORBIS_VIDEO_USER_MAIN,ORBIS_VIDEO_OUT_BUS_MAIN,0,NULL);
 if(video<0)return -1;
 if(sceKernelAllocateDirectMemory(0,sceKernelGetDirectMemorySize(),MEMORY_BYTES,0x200000,3,&memory_offset)<0)goto failed;
 if(sceKernelMapDirectMemory(&memory,MEMORY_BYTES,0x33,0,memory_offset,0x200000)<0){sceKernelReleaseDirectMemory(memory_offset,MEMORY_BYTES);goto failed;}
 buffers[0]=memory;buffers[1]=(uint32_t*)((char*)memory+FRAME_BYTES);
 OrbisVideoOutBufferAttribute attr;
 sceVideoOutSetBufferAttribute(&attr,0x80000000,1,0,WIDTH,HEIGHT,WIDTH);
 if(sceVideoOutRegisterBuffers(video,0,(void**)buffers,2,&attr)<0){installer_ui_close();return -1;}
 render();return 0;
failed:sceVideoOutClose(video);video=-1;return -1;
}
void installer_ui_status(const char *message){snprintf(status,sizeof(status),"%s",message);render();}
void installer_ui_progress(uint64_t written,uint64_t total){
 done_bytes=written;total_bytes=total;int percent=total?(int)(written*100/total):0;
 if(percent!=displayed_percent){displayed_percent=percent;
  render();}
}
void installer_ui_close(void){
 if(video>=0){sceVideoOutClose(video);video=-1;}
 if(memory){sceKernelMunmap(memory,MEMORY_BYTES);sceKernelReleaseDirectMemory(memory_offset,MEMORY_BYTES);memory=NULL;}
}
