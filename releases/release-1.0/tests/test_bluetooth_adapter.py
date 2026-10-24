#!/usr/bin/env python3
"""Exercise the actual HAL adapter with vectored HCI and unrelated writes."""
from pathlib import Path
import subprocess, tempfile

root = Path(__file__).resolve().parents[1]
test = r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define dlsym fake_dlsym
#define write atv_write
#define writev atv_writev
#include "bluetooth-sd8797.c"
#undef write
#undef writev
#undef dlsym
static unsigned char captured[256];
static size_t captured_n;
static int family=31, channel=1;
static int fake_name(int fd,void *p,unsigned *n){
 if(fd!=7)return -1;
 unsigned char *b=p;for(unsigned i=0;i<*n;i++)b[i]=0;
 b[0]=family;b[4]=channel;*n=6;return 0;
}
static ssize_t fake_write(int fd,const void *p,size_t n){
 (void)fd;assert(n<=sizeof(captured));memcpy(captured,p,n);captured_n=n;return n;
}
static ssize_t fake_writev(int fd,const struct iovec *v,int n){
 (void)fd;captured_n=0;
 for(int i=0;i<n;i++){assert(captured_n+v[i].iov_len<=sizeof(captured));
 memcpy(captured+captured_n,v[i].iov_base,v[i].iov_len);captured_n+=v[i].iov_len;}
 return captured_n;
}
void *fake_dlsym(void *h,const char *n){
 (void)h;if(!strcmp(n,"write"))return fake_write;
 if(!strcmp(n,"writev"))return fake_writev;
 if(!strcmp(n,"getsockname"))return fake_name;
 assert(0);return 0;
}
int main(void){
 unsigned char command[12]={1,1,0x20,8,0x7f,0xfe,2,0x4d,0,0,0,0};
 unsigned char expected[12]={1,1,0x20,8,0x1f,0,0,0,0,0,0,0};
 struct iovec parts[2]={{command,1},{command+1,11}};
 assert(atv_writev(7,parts,2)==12);assert(!memcmp(captured,expected,12));
 assert(command[4]==0x7f); /* Caller-owned buffers remain unchanged. */
 assert(atv_write(7,command,12)==12);assert(!memcmp(captured,expected,12));
 struct iovec bytes[12];for(int i=0;i<12;i++){bytes[i].iov_base=command+i;bytes[i].iov_len=1;}
 assert(atv_writev(7,bytes,12)==12);assert(!memcmp(captured,expected,12));
 assert(atv_writev(8,parts,2)==12);assert(!memcmp(captured,command,12));
 family=1;assert(atv_writev(7,parts,2)==12);assert(!memcmp(captured,command,12));family=31;
 channel=0;assert(atv_write(7,command,12)==12);assert(!memcmp(captured,command,12));channel=1;
 command[1]=2;assert(atv_writev(7,parts,2)==12);assert(!memcmp(captured,command,12));command[1]=1;
 command[0]=2;assert(atv_write(7,command,12)==12);assert(!memcmp(captured,command,12));command[0]=1;
 command[3]=7;assert(atv_write(7,command,12)==12);assert(!memcmp(captured,command,12));command[3]=8;
 assert(atv_write(7,command,11)==11);assert(!memcmp(captured,command,11));
 unsigned char small[12]={1,1,0x20,8,0x05};
 assert(atv_write(7,small,12)==12);assert(!memcmp(captured,small,12));
 puts("Bluetooth adapter: HCI mask correction and unaffected traffic passed");
}
'''
with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp)/'test.c'
    exe = Path(tmp)/'test'
    src.write_text(test)
    subprocess.run(['gcc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-I'+str(root/'source'), str(src), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
