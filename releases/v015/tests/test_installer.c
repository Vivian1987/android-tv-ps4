#define main installer_entry
#include "install-prebuilt.c"
#undef main
#include <assert.h>
int ps4_as_root(void(*f)(void*),void*a){f(a);return 0;}
int installer_ui_init(void){return 0;}
void installer_ui_status(const char*s){(void)s;}
void installer_ui_progress(uint64_t a,uint64_t b){assert(a<=b);}
void installer_ui_close(void){}
static void put(const char*p,const char*s){int fd=open(p,O_CREAT|O_TRUNC|O_WRONLY,0600);assert(fd>=0);assert(write(fd,s,strlen(s))==(ssize_t)strlen(s));close(fd);}
static void expect(const char*p,const char*s){char b[256]={0};int fd=open(p,O_RDONLY);assert(fd>=0);assert(read(fd,b,sizeof(b)-1)>=0);close(fd);assert(!strcmp(b,s));}
int main(void){
 assert(!mkdir(ROOT,0700));assert(compatible_installation());
 put(ROOT "/data-gib.txt","64\n");assert(!compatible_installation());expect(ROOT "/data-gib.txt","64\n");
 put(ROOT "/data-gib.txt","32\n");put(READY,"PS4ANDROID13-SPARSE-V014\nedition=32\n");assert(compatible_installation());
 put(READY,"unknown\n");assert(!compatible_installation());unlink(READY);
 for(int i=0;i<8;i++){char path[256];snprintf(path,sizeof(path),ROOT "/asset%d",i);put(path,"package-bytes");files[i]=open(path,O_RDONLY);assert(files[i]>=0);}
 assert(!install_boot());assert(!install_boot());expect(BOOT_ROOT "/bzImage","package-bytes");
 put(BOOT_ROOT "/bzImage","prior-kernel");put(BOOT_ROOT "/bzImage.ps4android-next","package-");assert(!install_boot());expect(BOOT_ROOT "/bzImage.before-sparse-v015","prior-kernel");assert(!install_boot());
 put(BOOT_ROOT "/bzImage","foreign-kernel");assert(install_boot()!=0);expect(BOOT_ROOT "/bzImage","foreign-kernel");
 put(ROOT "/system.sfs.part","package-");assert(!component(6,"system.sfs",13,0));expect(ROOT "/system.sfs","package-bytes");completed_bytes=0;assert(!component(6,"system.sfs",13,0));
 put(ROOT "/system.sfs","bad-contents!");assert(component(6,"system.sfs",13,0)!=0);expect(ROOT "/system.sfs","bad-contents!");
 for(int i=0;i<8;i++)close(files[i]);puts("PASS: edition guard, v014 state recognition, fresh/repeat boot setup, interrupted boot commit, backup preservation, foreign boot conflict, system-copy resume, mismatch preservation");return 0;
}
