"""Execute the real UI with host VideoOut stubs, including its image lifetime."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp);(d/'orbis').mkdir();(d/'images').mkdir()
 (d/'orbis/libkernel.h').write_text('''#include <stdint.h>
#include <sys/types.h>
int sceKernelDebugOutText(int,const char*); int sceKernelUsleep(unsigned);
size_t sceKernelGetDirectMemorySize(void);
int sceKernelAllocateDirectMemory(off_t,off_t,size_t,size_t,int,off_t*);
int sceKernelMapDirectMemory(void**,size_t,int,int,off_t,size_t);
int sceKernelReleaseDirectMemory(off_t,size_t);int sceKernelMunmap(void*,size_t);
''')
 (d/'orbis/SystemService.h').write_text('int sceSystemServiceHideSplashScreen(void);\n')
 (d/'orbis/VideoOut.h').write_text('''#define ORBIS_VIDEO_USER_MAIN 0
#define ORBIS_VIDEO_OUT_BUS_MAIN 0
#define ORBIS_VIDEO_OUT_FLIP_VSYNC 0
typedef struct {int unused;} OrbisVideoOutBufferAttribute;
typedef struct {int flipArg;} OrbisVideoOutFlipStatus;
int sceVideoOutOpen(int,int,int,void*);int sceVideoOutClose(int);
void sceVideoOutSetBufferAttribute(OrbisVideoOutBufferAttribute*,int,int,int,int,int,int);
int sceVideoOutRegisterBuffers(int,int,void**,int,OrbisVideoOutBufferAttribute*);
int sceVideoOutSubmitFlip(int,int,int,int);int sceVideoOutGetFlipStatus(int,OrbisVideoOutFlipStatus*);
''')
 for i in range(4):(d/f'images/slide-{i}.rgba').write_bytes(bytes([i+1,2,3,255])*(1280*720))
 (d/'test.c').write_text(r'''
#include "installer-ui.c"
#include <stdlib.h>
#include <assert.h>
static int flip,allocations,frees;
int sceKernelDebugOutText(int a,const char*b){(void)a;(void)b;return 0;}
int sceKernelUsleep(unsigned n){(void)n;return 0;}
size_t sceKernelGetDirectMemorySize(void){return 16*1024*1024;}
int sceKernelAllocateDirectMemory(off_t a,off_t b,size_t n,size_t align,int t,off_t*out){
 (void)a;(void)b;(void)align;(void)t;assert(n==MEMORY_BYTES);*out=0;allocations++;return 0;}
int sceKernelMapDirectMemory(void**out,size_t n,int p,int f,off_t o,size_t a){
 (void)p;(void)f;(void)o;(void)a;*out=calloc(1,n);return *out?0:-1;}
int sceKernelReleaseDirectMemory(off_t o,size_t n){(void)o;(void)n;frees++;return 0;}
int sceKernelMunmap(void*p,size_t n){(void)n;free(p);return 0;}
int sceVideoOutOpen(int a,int b,int c,void*d){(void)a;(void)b;(void)c;(void)d;return 8;}
int sceVideoOutClose(int v){assert(v==8);return 0;}
void sceVideoOutSetBufferAttribute(OrbisVideoOutBufferAttribute*a,int b,int c,int d,int e,int f,int g){
 (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;}
int sceVideoOutRegisterBuffers(int v,int a,void**p,int n,OrbisVideoOutBufferAttribute*b){
 (void)v;(void)a;(void)b;assert(n==2&&p[0]&&p[1]);return 0;}
int sceVideoOutSubmitFlip(int v,int b,int mode,int id){(void)v;(void)b;(void)mode;flip=id;return 0;}
int sceVideoOutGetFlipStatus(int v,OrbisVideoOutFlipStatus*s){(void)v;s->flipArg=flip;return 0;}
int sceSystemServiceHideSplashScreen(void){return 0;}
int main(void){
 assert(installer_ui_init()==0);assert(allocations==1);
 for(int i=0;i<4;i++)assert(slide_fds[i]>=0);
 /* Existing descriptors keep rendering after filesystem visibility changes. */
 assert(rename(ATV_ARTWORK_ROOT,ATV_ARTWORK_ROOT ".hidden")==0);
 installer_ui_progress(10,100);assert(buffers[buffer_index^1][0]==0xff030201);
 installer_ui_boot_status("Preparing Linux","Checking memory");
 for(int i=0;i<4;i++)assert(slide_fds[i]==-1);
 for(int i=0;i<5;i++)installer_ui_boot_status("Preparing Linux","Checking memory");
 assert(buffers[0][0]==0xff030201&&buffers[1][0]==0xff030201);
 assert(allocations==1&&installer_ui_close()==0&&frees==1);
 /* Failure reporting can reopen the display; missing artwork is harmless. */
 assert(installer_ui_init()==0);assert(!boot_mode&&buffers[buffer_index^1][0]==0xff071327);
 installer_ui_boot_status("Startup stopped","Your installation is preserved");
 assert(installer_ui_close()==0&&allocations==frees);
 char path[512];snprintf(path,sizeof(path),ATV_ARTWORK_ROOT ".hidden/slide-0.rgba");
 int fd=open(path,O_RDWR);assert(fd>=0);unsigned char pixel[4];
 assert(atv_read_slide(fd,pixel,sizeof(pixel))==-1);assert(ftruncate(fd,4)==0);
 assert(atv_read_slide(fd,pixel,sizeof(pixel))==0&&pixel[0]==1);
 assert(atv_read_slide(-1,pixel,sizeof(pixel))==-1);close(fd);
 puts("PASS: artwork uses existing display buffers; descriptors survive installer elevation and close before PREP; no further image reads or allocations; display reopens on failure; invalid image sizes rejected");
}
''')
 subprocess.run(['cc','-O2','-DEDITION_GIB=32','-DATV_ARTWORK_ROOT="'+str(d/'images')+'"',
 '-I'+str(d),'-I'+str(root/'source'),str(d/'test.c'),'-o',str(d/'test')],check=True)
 subprocess.run([str(d/'test')],check=True,timeout=10)
