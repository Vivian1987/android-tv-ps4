#include "image-stream.h"
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/stat.h>
#define CHUNK (4*1024*1024)
static int read_exact(int fd,void *buf,size_t n){
 char *p=buf;while(n){ssize_t r=read(fd,p,n);if(r<0&&errno==EINTR)continue;if(r<=0)return -1;p+=r;n-=r;}return 0;
}
static int write_exact(int fd,const void *buf,size_t n){
 const char *p=buf;while(n){ssize_t r=write(fd,p,n);if(r<0&&errno==EINTR)continue;if(r<=0)return -1;p+=r;n-=r;}return 0;
}
static uint32_t le32(const unsigned char*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t le64(const unsigned char*p){return le32(p)|((uint64_t)le32(p+4)<<32);}
int ps4_unpack_image(int in,int out,uint64_t expected,void(*progress)(uint64_t,uint64_t)){
 unsigned char h[28],r[12];uint32_t table[256];
 if(read_exact(in,h,sizeof(h))||memcmp(h,"PS4ATVIMG0000001",16)||le64(h+16)!=expected||le32(h+24)!=CHUNK)return -1;
 struct stat st;if(fstat(out,&st)||!S_ISREG(st.st_mode)||st.st_size!=0)return -1;
 unsigned char *buf=malloc(CHUNK);if(!buf)return -1;
 for(uint32_t i=0;i<256;i++){uint32_t c=i;for(int j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320U:0);table[i]=c;}
 uint64_t done=0;int status=-1;
 while(done<expected){
  if(read_exact(in,r,12))goto end;
  uint32_t kind=le32(r),len=le32(r+4),crc=le32(r+8);
  if(kind>1||len==0||len>CHUNK||len>expected-done)goto end;
  if(kind==0)memset(buf,0,len);else if(read_exact(in,buf,len))goto end;
  uint32_t c=~0U;for(uint32_t i=0;i<len;i++)c=table[(c^buf[i])&255]^(c>>8);
  if((c^~0U)!=crc)goto end;
  /* Write zero records as well: lseek/ftruncate would only promise space. */
  if(write_exact(out,buf,len))goto end;
  done+=len;if(progress)progress(done,expected);
 }
 {unsigned char extra;ssize_t n;do{n=read(in,&extra,1);}while(n<0&&errno==EINTR);if(n!=0)goto end;}
 if(fsync(out)||fstat(out,&st)||st.st_size!=(off_t)expected||(uint64_t)st.st_blocks*512<expected)goto end;
 status=0;
end:free(buf);return status;
}
