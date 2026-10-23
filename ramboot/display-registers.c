#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
int main(void){int f=open("/sys/kernel/debug/dri/0/amdgpu_regs",O_RDONLY);if(f<0){perror("open");return 1;}struct {char*n;unsigned r;} regs[]={{"GRPH_ENABLE",0x1a00},{"GRPH_CONTROL",0x1a01},{"GRPH_SWAP_CNTL",0x1a03},{"GRPH_PRIMARY_SURFACE_ADDRESS",0x1a04},{"GRPH_SECONDARY_SURFACE_ADDRESS",0x1a05},{"GRPH_PITCH",0x1a06},{"GRPH_PRIMARY_SURFACE_ADDRESS_HIGH",0x1a07},{"GRPH_SECONDARY_SURFACE_ADDRESS_HIGH",0x1a08},{"GRPH_UPDATE",0x1a11},{"GRPH_FLIP_CONTROL",0x1a12},{"GRPH_SURFACE_ADDRESS_INUSE",0x1a13},{"GRPH_SURFACE_ADDRESS_HIGH_INUSE",0x1a18},{"GRPH_STEREOSYNC_FLIP",0x1a97},{"CRTC_STEREO_CONTROL",0x1bae},{"CRTC_STEREO_STATUS",0x1bad}};for(unsigned i=0;i<sizeof(regs)/sizeof(regs[0]);i++){uint32_t v;if(pread(f,&v,4,(off_t)regs[i].r*4)!=4){perror("pread");return 1;}printf("%s 0x%04x=0x%08x\n",regs[i].n,regs[i].r,v);}return 0;}
