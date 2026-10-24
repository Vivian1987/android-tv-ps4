#define main installer_entry
#include "install-prebuilt.c"
#undef main
#include <assert.h>
int ps4_launch_local_payload(int log){(void)log;return 0;}
int ps4_as_root(void(*f)(void*),void*a){f(a);return 0;}
int installer_ui_init(void){return 0;}
void installer_ui_status(const char*s){(void)s;}
void installer_ui_progress(uint64_t a,uint64_t b){assert(a<=b);}
int installer_ui_close(void){return 0;}
int atv_launch_with_progress(void){return -1;}
static void put(const char*p,const char*s){int fd=open(p,O_CREAT|O_TRUNC|O_WRONLY,0600);assert(fd>=0);assert(write(fd,s,strlen(s))==(ssize_t)strlen(s));close(fd);}
static void expect(const char*p,const char*s){char b[256]={0};int fd=open(p,O_RDONLY);assert(fd>=0);assert(read(fd,b,sizeof(b)-1)>=0);close(fd);assert(!strcmp(b,s));}
int main(void){
 assert(!mkdir(ROOT,0700));assert(compatible_installation());
 put(ROOT "/data-gib.txt","64\n");assert(!compatible_installation());expect(ROOT "/data-gib.txt","64\n");
 put(ROOT "/data-gib.txt","32\n");put(READY,"PS4ANDROID13-SPARSE-V014\nedition=32\n");assert(compatible_installation());
 put(READY,"unknown\n");assert(!compatible_installation());unlink(READY);
 for(int i=0;i<ASSET_COUNT;i++){char path[256];snprintf(path,sizeof(path),ROOT "/asset%d",i);put(path,"package-bytes");files[i]=open(path,O_RDONLY);assert(files[i]>=0);}
 assert(!install_translation());assert(!install_translation());expect(ROOT "/ndk-translation.tar.gz","package-bytes");
 put(ROOT "/ndk-translation.tar.gz","foreign-archive");assert(install_translation()!=0);expect(ROOT "/ndk-translation.tar.gz","foreign-archive");
 assert(!install_graphics());assert(!install_graphics());expect(ROOT "/libgallium-baseline.so","package-bytes");
 put(ROOT "/libgallium-baseline.so","prior-graphics");assert(!install_graphics());expect(ROOT "/libgallium-baseline.so.before-release-100","prior-graphics");
 assert(!install_graphics());put(ROOT "/libgallium-baseline.so","foreign-graphics");assert(install_graphics()!=0);expect(ROOT "/libgallium-baseline.so","foreign-graphics");
 assert(!install_boot());assert(!install_boot());expect(BOOT_ROOT "/bzImage","package-bytes");
 put(BOOT_ROOT "/bzImage","prior-kernel");put(BOOT_ROOT "/bzImage.ps4android-next","package-");assert(!install_boot());expect(BOOT_ROOT "/bzImage.before-sparse-v015","prior-kernel");assert(!install_boot());
 put(BOOT_ROOT "/bzImage","foreign-kernel");assert(install_boot()!=0);expect(BOOT_ROOT "/bzImage","foreign-kernel");
 put(ROOT "/system.sfs.part","package-");assert(!component(6,"system.sfs",13,0));expect(ROOT "/system.sfs","package-bytes");completed_bytes=0;assert(!component(6,"system.sfs",13,0));
 put(ROOT "/system.sfs","bad-contents!");assert(component(6,"system.sfs",13,0)!=0);expect(ROOT "/system.sfs","bad-contents!");
 completed_bytes=0;put(ROOT "/app-youtube-base.apk.part","package-");assert(!install_bundled_apps());
 for(int i=0;i<BUNDLED_APP_COUNT;i++){
  char app[256];snprintf(app,sizeof(app),ROOT "/%s",bundled_apps[i].file);expect(app,"package-bytes");
  struct stat apkstat;assert(!stat(app,&apkstat));assert((apkstat.st_mode&0777)==0644);
 }
 completed_bytes=0;assert(!install_bundled_apps());
 put(ROOT "/app-youtube-base.apk","foreign-app!!");completed_bytes=0;assert(install_bundled_apps()!=0);expect(ROOT "/app-youtube-base.apk","foreign-app!!");
 for(int i=0;i<ASSET_COUNT;i++)close(files[i]);puts("PASS: edition guard, v014 state recognition, fresh/repeat boot setup, interrupted boot commit, backup preservation, foreign boot conflict, system-copy resume, mismatch preservation");return 0;
}
