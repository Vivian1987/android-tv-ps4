/* Marvell SD8797 Bluetooth 4.0: reserved LE event bits are rejected
 * with HCI Invalid Command Parameters. Keep supported event bits only.
 * Loaded only into the SD8797 HCI HAL; no response/status rewriting. */
typedef unsigned long size_t;
typedef long ssize_t;
struct iovec { void *iov_base; size_t iov_len; };
extern void *dlsym(void *, const char *);
#define EXPORT __attribute__((visibility("default")))
static void *next(const char *s){return dlsym((void*)-1L,s);}
static int hci_socket(int fd){
 int (*name)(int,void*,unsigned*)=next("getsockname");
 unsigned char addr[128];unsigned n=sizeof(addr);
 return name && !name(fd,addr,&n) && n>=6 && addr[0]==31 && addr[1]==0 && addr[4]==1 && addr[5]==0;
}
static int trim(unsigned char *p,size_t n){
 if(n!=12 || p[0]!=1 || p[1]!=1 || p[2]!=0x20 || p[3]!=8)return 0;
 p[4]&=0x1f;for(int i=5;i<12;i++)p[i]=0;return 1;
}
EXPORT ssize_t writev(int fd,const struct iovec *iov,int count){
 ssize_t (*fn)(int,const struct iovec*,int)=next("writev");
 if(count>0 && count<=12){
  size_t n=0;for(int i=0;i<count;i++){if(iov[i].iov_len>12-n)return fn(fd,iov,count);n+=iov[i].iov_len;}
  if(n==12 && hci_socket(fd)){
   unsigned char p[12];size_t off=0;
   for(int i=0;i<count;i++)for(size_t j=0;j<iov[i].iov_len;j++)p[off++]=((unsigned char*)iov[i].iov_base)[j];
   if(trim(p,n)){struct iovec single={p,n};return fn(fd,&single,1);}
  }
 }
 return fn(fd,iov,count);
}
EXPORT ssize_t write(int fd,const void *buf,size_t n){
 ssize_t (*fn)(int,const void*,size_t)=next("write");
 if(n==12 && hci_socket(fd)){
  unsigned char p[12];for(size_t i=0;i<n;i++)p[i]=((const unsigned char*)buf)[i];
  if(trim(p,n))return fn(fd,p,n);
 }
 return fn(fd,buf,n);
}
