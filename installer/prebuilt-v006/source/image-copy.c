#include "image-copy.h"
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/stat.h>
#define COPY_BUFFER (4*1024*1024)
/* Copy the complete preformatted image packaged as assets/android.img.
 * No image construction, filesystem formatting, sparse expansion, or CRC loop.
 * Package validation protects the bundled source; writes reserve real space.
 */
int ps4_copy_image(int source,int target,uint64_t expected,
                   void (*progress)(uint64_t,uint64_t)){
 struct stat src,dst;
 if(!expected||fstat(source,&src)||fstat(target,&dst))return -1;
 if(!S_ISREG(src.st_mode)||!S_ISREG(dst.st_mode)||
    src.st_size<0||(uint64_t)src.st_size!=expected||dst.st_size!=0){errno=EINVAL;return -1;}
 if(lseek(source,0,SEEK_SET)<0||lseek(target,0,SEEK_SET)<0)return -1;
 char *buffer=malloc(COPY_BUFFER);if(!buffer)return -1;
 uint64_t done=0;int result=-1;
 if(progress)progress(0,expected);
 while(done<expected){
  size_t want=expected-done>COPY_BUFFER?COPY_BUFFER:(size_t)(expected-done);
  ssize_t got;
  do{got=read(source,buffer,want);}while(got<0&&errno==EINTR);
  if(got<=0){if(!got)errno=EIO;goto end;}
  ssize_t offset=0;
  while(offset<got){
   ssize_t written=write(target,buffer+offset,(size_t)(got-offset));
   if(written<0&&errno==EINTR)continue;
   if(written<=0){if(!written)errno=EIO;goto end;}
   offset+=written;
  }
  done+=(uint64_t)got;if(progress)progress(done,expected);
 }
 if(fsync(target)||fstat(target,&dst))goto end;
 if((uint64_t)dst.st_size!=expected||(uint64_t)dst.st_blocks*512<expected){errno=EIO;goto end;}
 result=0;
end:free(buffer);return result;
}
