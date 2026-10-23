#include "ps4-stat-abi.h"
/* Development self-contained installer. App assets opened before elevation. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <orbis/SystemService.h>
#include <orbis/Sysmodule.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <orbis/libkernel.h>
#ifdef RAW_IMAGES
#include "image-copy.h"
#else
#include "image-extract.h"
#endif
#include "image-metadata.h"
#include "installer-ui.h"
#ifndef EDITION_GIB
#error Edition required
#endif
#define ROOT "/user/app/ps4-android"
#define READY ROOT "/ready"
#define GIB (1024ULL*1024*1024)
extern int ps4_as_root(void(*fn)(void*),void*arg);
/* Avoid SDK lstat/fstatat/link/statvfs stubs. */
static int path_stat(const char *path,struct stat *st){
 int fd=open(path,O_RDONLY|O_NOFOLLOW);if(fd<0)return -1;
 int result=fstat(fd,st),saved=errno;close(fd);errno=saved;return result;
}
static int commit_file(const char *from,const char *to){
 struct stat st;
 if(path_stat(to,&st)==0){errno=EEXIST;return -1;}
 if(errno!=ENOENT)return -1;
 /* Exclusive staging file serializes this installer's writers. */
 return rename(from,to);
}
static int files[8];
#ifdef RAW_IMAGES
#define DATA_ASSET "data-gib.txt"
#define SYSTEM_ASSET "system.sfs"
#define SYSTEM_OPERATION "Installing compressed Android system"
#define DATA_OPERATION "Copying your prepared data disk"
#else
#define DATA_ASSET "data.zip"
#define SYSTEM_ASSET "system.img.gz"
#define SYSTEM_OPERATION "Extracting the bundled Android system image"
#define DATA_OPERATION "Extracting your preformatted data.img from its supplied ZIP"
#endif
static const char *names[8]={DATA_ASSET,"bzImage","initramfs.cpio.gz","bootargs.txt","vram.txt","linux.elf",SYSTEM_ASSET,"libgallium-baseline.so"};
static void notice(const char *s){char log[320];snprintf(log,sizeof(log),"[PS4ATV] %s\n",s);sceKernelDebugOutText(0,log);installer_ui_status(s);OrbisNotificationRequest n;memset(&n,0,sizeof(n));n.type=NotificationRequest;n.targetId=-1;snprintf(n.message,sizeof(n.message),"PS4 Android TV: %s",s);sceKernelSendNotificationRequest(0,&n,sizeof(n),0);}
static void failure(const char *s){int saved=errno;char message[256];snprintf(message,sizeof(message),"%s (errno %d)",s,saved);notice(message);}
static uint64_t completed_bytes;
static const uint64_t install_bytes=SYSTEM_BYTES;
static void progress(uint64_t done,uint64_t total){
 (void)total;installer_ui_progress(completed_bytes+done,install_bytes);
}
static int copy_file(int from,const char *target){
 int to=open(target,O_WRONLY|O_CREAT|O_EXCL,0600);if(to<0)return -1;
 char *buf=malloc(1024*1024);int status=-1;if(!buf){close(to);return -1;}
 if(lseek(from,0,SEEK_SET)<0)goto end;
 for(;;){ssize_t n=read(from,buf,1024*1024);if(n<0&&errno==EINTR)continue;if(n<0)goto end;if(!n)break;
  ssize_t at=0;while(at<n){ssize_t w=write(to,buf+at,n-at);if(w<0&&errno==EINTR)continue;if(w<=0)goto end;at+=w;}}
 if(fsync(to)==0)status=0;
end:free(buf);if(close(to))status=-1;return status;
}
static int install_boot(void){
 char targets[4][128],stages[4][160],backups[4][160];int existed[4]={0},committed=0;
 if(mkdir("/data/linux",0755)&&errno!=EEXIST)return -1;
 if(mkdir("/data/linux/boot",0755)&&errno!=EEXIST)return -1;
 /* Refuse ambiguous prior staging/backup files before touching anything. */
 for(int i=0;i<4;i++){
  snprintf(targets[i],sizeof(targets[i]),"/data/linux/boot/%s",names[i+1]);
  snprintf(stages[i],sizeof(stages[i]),"%s.ps4android-next",targets[i]);
  snprintf(backups[i],sizeof(backups[i]),"%s.before-sparse-v008",targets[i]);
  struct stat st;if(path_stat(stages[i],&st)==0||path_stat(backups[i],&st)==0)return -1;
  existed[i]=path_stat(targets[i],&st)==0;
 }
 for(int i=0;i<4;i++)if(copy_file(files[i+1],stages[i]))return -1;
 for(int i=0;i<4;i++){
  if(existed[i]&&rename(targets[i],backups[i]))goto rollback;
  if(rename(stages[i],targets[i])){if(existed[i])rename(backups[i],targets[i]);goto rollback;}
  committed++;
 }
 {int d=open("/data/linux/boot",O_RDONLY);if(d<0)return -1;int r=fsync(d);close(d);return r;}
rollback:
 for(int i=committed-1;i>=0;i--){unlink(targets[i]);if(existed[i])rename(backups[i],targets[i]);}
 return -1;
}
static int installation_ready(void){
 char actual[128]={0},expected[128];
 int fd=open(READY,O_RDONLY);if(fd<0)return 0;
 ssize_t n=read(fd,actual,sizeof(actual)-1);close(fd);
 int length=snprintf(expected,sizeof(expected),"PS4ANDROID13-SPARSE-V008\nedition=%d\n",EDITION_GIB);
 return n==length && memcmp(actual,expected,(size_t)length)==0;
}
static int send_loader(void){
 int sock=socket(AF_INET,SOCK_STREAM,0);if(sock<0)return -1;
 struct sockaddr_in addr;memset(&addr,0,sizeof(addr));addr.sin_family=AF_INET;addr.sin_port=htons(9090);addr.sin_addr.s_addr=htonl(0x7f000001);
 if(connect(sock,(struct sockaddr*)&addr,sizeof(addr))){close(sock);return -1;}
 char buf[65536];if(lseek(files[5],0,SEEK_SET)<0){close(sock);return -1;}
 for(;;){ssize_t n=read(files[5],buf,sizeof(buf));if(n<0&&errno==EINTR)continue;if(n<0){close(sock);return -1;}if(!n)break;
  ssize_t at=0;while(at<n){ssize_t w=send(sock,buf+at,n-at,0);if(w<0&&errno==EINTR)continue;if(w<=0){close(sock);return -1;}at+=w;}}
 shutdown(sock,SHUT_WR);close(sock);return 0;
}
static int component(int index,const char *name,uint64_t expected,int zipped){
 char target[192],stage[192];snprintf(target,sizeof(target),ROOT "/%s",name);
 snprintf(stage,sizeof(stage),ROOT "/%s.part",name);
 struct stat st;
 if(path_stat(target,&st)==0){failure("Existing component preserved; finish or recover prior setup first");return -1;}
 if(errno!=ENOENT)return -1;
 /* Preserve abandoned output under a new name; never truncate it. */
 if(path_stat(stage,&st)==0){
  if(!S_ISREG(st.st_mode)){errno=EINVAL;return -1;}
  char archived[224];int found=0;
  for(int n=1;n<=100;n++){
   snprintf(archived,sizeof(archived),"%s.failed-%d",stage,n);
   if(path_stat(archived,&st)<0){if(errno!=ENOENT)return -1;found=1;break;}
  }
  if(!found){errno=EEXIST;return -1;}
  if(rename(stage,archived))return -1;
  notice("Previous partial image preserved; restarting extraction");
 }else if(errno!=ENOENT)return -1;
 int out=open(stage,O_RDWR|O_CREAT|O_EXCL,0600);if(out<0)return -1;
 struct stat in;int result=-1;
 if(fstat(files[index],&in)==0){
  char log[192];snprintf(log,sizeof(log),"[PS4ATV] %s source bytes=%llu output bytes=%llu\n",name,(unsigned long long)in.st_size,(unsigned long long)expected);sceKernelDebugOutText(0,log);
#ifdef RAW_IMAGES
  (void)zipped;
  result=ps4_copy_image(files[index],out,expected,progress);
#else
  result=ps4_extract_image(files[index],out,zipped?DATA_ZIP_OFFSET:0,
    zipped?DATA_ZIP_COMPRESSED:(uint64_t)in.st_size,expected,zipped?-15:31,
    zipped?DATA_ZIP_CRC:0,zipped,progress);
#endif
 }
 int saved=errno;if(close(out)&&result==0){result=-1;saved=errno;}errno=saved;
 if(result){int e=errno;
#ifndef RAW_IMAGES
 char log[320];snprintf(log,sizeof(log),"[PS4ATV] Extract detail: %s\n",ps4_extract_error());sceKernelDebugOutText(0,log);
#endif
 errno=e;return -1;}
 if(commit_file(stage,target))return -1;
 completed_bytes+=expected;return 0;
}
static void install_or_boot(void *unused){
 (void)unused;struct stat st;
 if(installation_ready()){
  if(path_stat(ROOT "/system.sfs",&st)||!S_ISREG(st.st_mode)||(uint64_t)st.st_size!=SYSTEM_BYTES){
   failure("Installed image is missing or has the wrong size");return;}
  notice("Booting Android TV from the internal HDD");
  if(send_loader())failure("Enable GoldHEN BinLoader on port 9090, then launch again");
  return;
 }
 struct statfs space;int disk=open("/user",O_RDONLY|O_DIRECTORY);
 if(disk<0){failure("Cannot open internal storage");return;}
 int result=fstatfs(disk,&space),saved=errno;close(disk);errno=saved;
 if(result){failure("Cannot check internal free space");return;}
 uint64_t available=space.f_bavail>0?(uint64_t)space.f_bavail*space.f_bsize:0;
 if(available<install_bytes+2*GIB){notice("Not enough internal HDD space for the system and data disk");return;}
 if(mkdir(ROOT,0755)&&errno!=EEXIST){failure("Cannot create installation directory");return;}
 notice(SYSTEM_OPERATION);
 if(component(6,"system.sfs",SYSTEM_BYTES,0)){failure("System image installation failed; partial preserved");return;}
 notice("Preparing first-boot storage setup");
 if(copy_file(files[0],ROOT "/data-gib.txt")){failure("Cannot write storage selection");return;}
 notice("Installing graphics support and boot files");
 if(copy_file(files[7],ROOT "/libgallium-baseline.so")){failure("Cannot install graphics library");return;}
 if(install_boot()){failure("Cannot finish boot setup; image files preserved");return;}
 int ready=open(READY ".next",O_WRONLY|O_CREAT|O_EXCL,0600);
 if(ready<0){failure("Cannot record completion");return;}
 char state[128];int n=snprintf(state,sizeof(state),"PS4ANDROID13-SPARSE-V008\nedition=%d\n",EDITION_GIB);
 int ok=write(ready,state,n)==n&&fsync(ready)==0;close(ready);
 if(!ok||commit_file(READY ".next",READY)){failure("Cannot commit completion marker");return;}
 notice("System installed. Booting Android to create fresh storage");
 sceKernelUsleep(3000000);
 if(send_loader())failure("Enable GoldHEN BinLoader, then launch again");
}
int main(void){
 sceSysmoduleLoadModuleInternal(ORBIS_SYSMODULE_INTERNAL_SYSTEM_SERVICE);
 installer_ui_init();notice("Checking installation and free space");
 for(int i=0;i<8;i++)files[i]=-1;
 for(int i=0;i<8;i++){char path[128];snprintf(path,sizeof(path),"/app0/assets/%s",names[i]);files[i]=open(path,O_RDONLY);if(files[i]<0){notice("Package content missing. Nothing installed.");goto end;}}
 if(ps4_as_root(install_or_boot,NULL))notice("Could not obtain or restore required console filesystem access.");
end:for(int i=0;i<8;i++)if(files[i]>=0)close(files[i]);sceKernelUsleep(10000000);installer_ui_close();sceSystemServiceLoadExec("exit",NULL);
 /* Never return through the SDK _exit path: it raises SIGSYS here. */
 for(;;)sceKernelUsleep(1000000);
}
