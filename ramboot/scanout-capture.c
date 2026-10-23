#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
int main(int argc,char**argv){int r=open("/sys/kernel/debug/dri/0/amdgpu_regs",O_RDONLY),f=open("/sys/kernel/debug/dri/0/amdgpu_vram",O_RDONLY);uint32_t lo,hi;unsigned reg=argc>1?0x1a05:0x1a04;if(r<0||f<0)return 1;if(pread(r,&lo,4,reg*4)!=4||pread(r,&hi,4,(reg+3)*4)!=4)return 2;uint64_t addr=((uint64_t)hi<<32)|lo;if(addr<0xf00000000ULL||addr+8294400>0xf80000000ULL)return 3;unsigned char *b=malloc(8294400);if(pread(f,b,8294400,addr-0xf00000000ULL)!=8294400){perror("VRAM read");return 4;}fprintf(stderr,"captured GPU surface %llx\n",(unsigned long long)addr);printf("P6\n1920 1080\n255\n");for(unsigned i=0;i<1920*1080;i++)fwrite(b+i*4,1,3,stdout);return 0;}
