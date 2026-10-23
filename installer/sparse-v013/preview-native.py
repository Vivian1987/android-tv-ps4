from pathlib import Path
p=Path('/mnt/nas/apps/ps4-android/installer/sparse-v013');s=(p/'source/installer-ui.c').read_text()
s='\n'.join(l for l in s.splitlines() if not l.startswith('#include <orbis/'))
s=s[:s.index('int installer_ui_init(void)')]
stubs='''#include <stdlib.h>
#include <sys/types.h>
#define ORBIS_VIDEO_OUT_FLIP_VSYNC 1
typedef struct { int flipArg; } OrbisVideoOutFlipStatus;
static int lastid;
static int sceVideoOutSubmitFlip(int a,int b,int c,int d){lastid=d;return 0;}
static int sceVideoOutGetFlipStatus(int a,OrbisVideoOutFlipStatus *b){b->flipArg=lastid;return 0;}
static void sceKernelDebugOutText(int a,const char*b){}
static void sceKernelUsleep(int a){}
static int sceSystemServiceHideSplashScreen(void){return 0;}
'''
s=stubs+s+'''
int main(void){video=1;buffers[0]=calloc(1280*720,4);buffers[1]=calloc(1280*720,4);
strcpy(status,"Installing compressed Android system");total_bytes=2292254896ULL;done_bytes=1430257664ULL;started=seconds()-180;render();
FILE *f=fopen("/tmp/installer-preview.ppm","wb");fprintf(f,"P6\\n1280 720\\n255\\n");
for(int i=0;i<1280*720;i++){uint32_t c=buffers[0][i];fputc(c>>16,f);fputc(c>>8,f);fputc(c,f);}fclose(f);return 0;}
'''
Path('/tmp/preview-native.c').write_text(s)
