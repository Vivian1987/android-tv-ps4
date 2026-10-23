/* Read-only hardware/firmware queries. No kernel patching or boot changes. */
#include "kernel.h"
#include "module.h"
#include "file.h"
static int fd;
static void text(const char*s){size_t n=0;while(s[n])n++;write(fd,s,n);}
static void hex(unsigned long long n){char b[17];char *a="0123456789abcdef";for(int i=0;i<16;i++)b[i]=a[(n>>(60-i*4))&15];b[16]=0;text(b);}
int _main(void){
 fd=open("/data/cole-hardware-probe.txt",O_WRONLY|O_CREAT|O_TRUNC,0600);if(fd<0)return 1;
 text("Cole read-only hardware probe: entry and file IO OK\n");
 initKernel();text("libkernel initialisation returned\n");
 SceFwInfo fw={0};fw.unk1=sizeof(fw);int r=sceKernelGetSystemSwVersion?sceKernelGetSystemSwVersion(&fw):-1;
 text("firmware_result=0x");hex((unsigned)r);text(" firmware=0x");hex(fw.version);text(" ");fw.version_string[27]=0;text(fw.version_string);text("\n");
 extern int libKernelHandle;
 int (*getModel)(char*)=0;
 int symbol=getFunctionAddressByName(libKernelHandle,"sceKernelGetHwModelName",&getModel);
 char model[256]={0};
 text("model_symbol_result=0x");hex((unsigned)symbol);
 if(!symbol && getModel){int rc=getModel(model);model[255]=0;text(" model_result=0x");hex((unsigned)rc);if(!rc){text(" model=");text(model);}}
 text("\n");
 char names[][32]={"hw.model","hw.machine","hw.ncpu","hw.physmem","hw.sce.console_model","machdep.console_model","machdep.southbridge","hw.sce.model","kern.osrelease"};
 for(unsigned i=0;i<sizeof(names)/sizeof(names[0]);i++){
  char b[256]={0};size_t len=sizeof(b)-1;int rc=sysctlbyname?sysctlbyname(names[i],b,&len,0,0):-1;
  text(names[i]);text(" result=0x");hex((unsigned)rc);text(" bytes=0x");hex(len);text(" data=");
  if(!rc){if(len>255)len=255;for(size_t j=0;j<len;j++){unsigned char c=b[j];char pair[3]={"0123456789abcdef"[c>>4],"0123456789abcdef"[c&15],0};text(pair);}}
  text("\n");
 }
 close(fd);return 0;
}
