#include "ps4-stat-abi.h"
#include "image-extract.h"
#include <zlib.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
static char extraction_error[256];
const char *ps4_extract_error(void){return extraction_error;}
#include <sys/stat.h>
#define BUFFER (1024*1024)
int ps4_extract_image(int source,int target,uint64_t offset,uint64_t compressed,
 uint64_t expected,int window_bits,uint32_t checksum,int check_checksum,
 void (*progress)(uint64_t,uint64_t)){
 extraction_error[0]=0;
 const char *phase="input/output stat";
 struct stat input,output;
 if(fstat(source,&input)||fstat(target,&output))return -1;
 if(!compressed||!expected||!S_ISREG(output.st_mode)||output.st_size!=0||
    offset>(uint64_t)input.st_size||compressed>(uint64_t)input.st_size-offset){errno=EINVAL;return -1;}
 if(lseek(source,(off_t)offset,SEEK_SET)<0)return -1;
 unsigned char *in=malloc(BUFFER),*out=malloc(BUFFER);
 if(!in||!out){free(in);free(out);errno=ENOMEM;return -1;}
 z_stream stream;memset(&stream,0,sizeof(stream));
 uint64_t left=compressed,done=0;
 phase="inflate init";
 int status=-1,initialized=0,code=inflateInit2(&stream,window_bits);
 if(code!=Z_OK){errno=EIO;goto end;}initialized=1;
 uint32_t crc=crc32(0L,Z_NULL,0);
 if(progress)progress(0,expected);
 for(;;){
  if(!stream.avail_in&&left){
   size_t want=left>BUFFER?BUFFER:(size_t)left;ssize_t got;
   phase="source read";
   do{got=read(source,in,want);}while(got<0&&errno==EINTR);
   if(got<=0){if(!got)errno=EIO;goto end;}
   left-=(uint64_t)got;stream.next_in=in;stream.avail_in=(uInt)got;
  }
  stream.next_out=out;stream.avail_out=BUFFER;
  phase="inflate";
  uInt before=stream.avail_in;code=inflate(&stream,Z_NO_FLUSH);
  size_t produced=BUFFER-stream.avail_out;
  if(produced>expected-done){errno=EFBIG;goto end;}
  if(check_checksum)crc=crc32(crc,out,(uInt)produced);
  size_t at=0;
  phase="target write";
  while(at<produced){ssize_t n=write(target,out+at,produced-at);
   if(n<0&&errno==EINTR)continue;
   if(n<=0){if(!n)errno=EIO;goto end;}at+=(size_t)n;}
  done+=produced;if(progress&&produced)progress(done,expected);
  if(code==Z_STREAM_END)break;
  phase="inflate result";
  if(code!=Z_OK||(!produced&&before==stream.avail_in&&!left)){errno=EIO;goto end;}
 }
 phase="length/checksum verification";
 if(done!=expected||left||stream.avail_in||(check_checksum&&crc!=checksum)){errno=EIO;goto end;}
 phase="target fsync";if(fsync(target))goto end;
 phase="target final stat";if(fstat(target,&output))goto end;
 if((uint64_t)output.st_size!=expected){errno=EIO;goto end;}
 /* Every output byte was written; do not depend on SDK st_blocks accounting. */
 status=0;
end:{int saved=errno;
 if(status)snprintf(extraction_error,sizeof(extraction_error),"%s: errno=%d zlib=%d in=%llu out=%llu remaining=%u message=%s",phase,saved,code,(unsigned long long)(compressed-left),(unsigned long long)done,stream.avail_in,stream.msg?stream.msg:"none");
 if(initialized)inflateEnd(&stream);free(in);free(out);errno=saved;}return status;
}
