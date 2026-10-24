#ifndef ATV_INSTALLER_SLIDE_H
#define ATV_INSTALLER_SLIDE_H
#include <unistd.h>
#include <errno.h>
/* Decode-free BGRA pixels read straight into the next display buffer. */
static int atv_read_slide(int fd,void *target,size_t bytes){
 if(fd<0||lseek(fd,0,SEEK_END)!=(off_t)bytes||lseek(fd,0,SEEK_SET)!=0)return -1;
 size_t offset=0;
 while(offset<bytes){
  ssize_t n=read(fd,(char*)target+offset,bytes-offset);
  if(n<0&&errno==EINTR)continue;
  if(n<=0)return -1;
  offset+=(size_t)n;
 }
 return 0;
}
#endif
