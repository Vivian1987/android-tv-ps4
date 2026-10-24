#include "ps4-stat-abi.h"
#include "image-copy.h"
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
#define COPY_BUFFER (1024*1024)
static int read_exact(int fd,char *buffer,size_t count){
 size_t done=0;while(done<count){ssize_t n=read(fd,buffer+done,count-done);
  if(n<0&&errno==EINTR)continue;if(n<=0){if(!n)errno=EIO;return -1;}done+=(size_t)n;}
 return 0;
}
/* An interrupted output is resumed only after its entire existing prefix is
 * compared against the immutable package source. A mismatch never changes it. */
int ps4_copy_image(int source,int target,uint64_t expected,
                   void (*progress)(uint64_t,uint64_t)){
 struct stat src,dst;
 if(!expected||fstat(source,&src)||fstat(target,&dst))return -1;
 if(!S_ISREG(src.st_mode)||!S_ISREG(dst.st_mode)||src.st_size<0||dst.st_size<0||
    (uint64_t)src.st_size!=expected||(uint64_t)dst.st_size>expected){errno=EINVAL;return -1;}
 if(lseek(source,0,SEEK_SET)<0||lseek(target,0,SEEK_SET)<0)return -1;
 char *buffer=malloc(COPY_BUFFER),*compare=malloc(COPY_BUFFER);
 if(!buffer||!compare){free(buffer);free(compare);errno=ENOMEM;return -1;}
 uint64_t done=0,prefix=(uint64_t)dst.st_size;int result=-1;
 while(done<prefix){size_t want=prefix-done>COPY_BUFFER?COPY_BUFFER:(size_t)(prefix-done);
  if(read_exact(source,buffer,want)||read_exact(target,compare,want))goto end;
  if(memcmp(buffer,compare,want)){errno=EIO;goto end;}
  done+=want;if(progress)progress(done,expected);
 }
 if(progress)progress(done,expected);
 while(done<expected){
  size_t want=expected-done>COPY_BUFFER?COPY_BUFFER:(size_t)(expected-done);
  if(read_exact(source,buffer,want))goto end;
  size_t offset=0;while(offset<want){ssize_t n=write(target,buffer+offset,want-offset);
   if(n<0&&errno==EINTR)continue;if(n<=0){if(!n)errno=EIO;goto end;}offset+=(size_t)n;}
  done+=want;if(progress)progress(done,expected);
 }
 if(fsync(target)||fstat(target,&dst))goto end;
 if((uint64_t)dst.st_size!=expected){errno=EIO;goto end;}
 result=0;
end:{int saved=errno;free(buffer);free(compare);errno=saved;}return result;
}
