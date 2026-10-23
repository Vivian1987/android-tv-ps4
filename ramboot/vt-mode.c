#include <fcntl.h>
#include <linux/kd.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>
int main(int argc, char **argv) {
 int fd=open("/dev/tty0",O_RDWR|O_CLOEXEC), mode=-1, keyboard=-1;
 if(fd<0){perror("open tty0");return 1;}
 if(ioctl(fd,KDGETMODE,&mode)||ioctl(fd,KDGKBMODE,&keyboard)){perror("get VT mode");return 1;}
 printf("VT mode=%d (%s), keyboard mode=%d\n",mode,mode==KD_TEXT?"text":"graphics",keyboard);
 if(argc>1 && !strcmp(argv[1],"--graphics")) {
  if(ioctl(fd,KDSETMODE,KD_GRAPHICS)||ioctl(fd,KDSKBMODE,K_OFF)){perror("graphics handoff");return 1;}
  puts("VT released to graphics; console keyboard disabled, evdev input retained.");
 } else if(argc>1 && !strcmp(argv[1],"--text")) {
  if(ioctl(fd,KDSKBMODE,K_XLATE)||ioctl(fd,KDSETMODE,KD_TEXT)){perror("text restore");return 1;}
 }
 close(fd);return 0;
}
