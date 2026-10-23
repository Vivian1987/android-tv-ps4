#include <stdint.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
static uint32_t rd(int f,unsigned r){uint32_t v;if(pread(f,&v,4,(off_t)r*4)!=4){perror("read register");exit(1);}return v;}
static void wr(int f,unsigned r,uint32_t v){if(pwrite(f,&v,4,(off_t)r*4)!=4){perror("write register");exit(1);}}
int main(void){int f=open("/sys/kernel/debug/dri/0/amdgpu_regs",O_RDWR);if(f<0){perror("open");return 1;}uint32_t p=rd(f,0x1a04),ph=rd(f,0x1a07),s=rd(f,0x1a05),sh=rd(f,0x1a08);printf("primary=%08x:%08x previous-secondary=%08x:%08x\n",ph,p,sh,s);wr(f,0x1a08,ph);wr(f,0x1a05,p);printf("secondary now=%08x:%08x\n",rd(f,0x1a08),rd(f,0x1a05));return 0;}
