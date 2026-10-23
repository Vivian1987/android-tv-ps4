#define _GNU_SOURCE
#include <sys/ptrace.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
static uint64_t rd(pid_t p,uint64_t a){errno=0;long v=ptrace(PTRACE_PEEKDATA,p,(void*)a,0);if(errno){perror("peek");exit(2);}return v;}
int main(int c,char**v){pid_t p=atoi(v[1]);char path[80],line[512];snprintf(path,sizeof(path),"/proc/%d/maps",p);FILE*f=fopen(path,"r");uint64_t base=0;while(fgets(line,sizeof(line),f)){if(strstr(line,"composer@2.1-drmfb-service")&&strstr(line,"00000000")){sscanf(line,"%lx",&base);break;}}fclose(f);if(!base)return 3;if(ptrace(PTRACE_ATTACH,p,0,0)){perror("attach");return 4;}int st;waitpid(p,&st,0);uint64_t a=base+0x16e50,word=rd(p,a);ptrace(PTRACE_POKETEXT,p,(void*)a,(void*)((word&~255ULL)|0xcc));ptrace(PTRACE_CONT,p,0,0);for(int n=0;n<18;n++){waitpid(p,&st,0);struct user_regs_struct r;ptrace(PTRACE_GETREGS,p,0,&r);if(r.rip!=a+1){printf("other stop %d rip=%llx\n",st,r.rip);break;}uint64_t h=r.rsi,d=r.rdi,id=rd(p,h+0x50),fd=rd(p,h+0xc)&0xffffffff;snprintf(path,sizeof(path),"/proc/%d/fd/%u",p,(unsigned)fd);struct stat sb;stat(path,&sb);printf("handle=%lx id=%u width=%u fd=%u inode=%lu display=%lx\n",h,(unsigned)id,(unsigned)(id>>32),(unsigned)fd,sb.st_ino,d);ptrace(PTRACE_POKETEXT,p,(void*)a,(void*)word);r.rip=a;ptrace(PTRACE_SETREGS,p,0,&r);ptrace(PTRACE_SINGLESTEP,p,0,0);waitpid(p,&st,0);ptrace(PTRACE_POKETEXT,p,(void*)a,(void*)((word&~255ULL)|0xcc));ptrace(PTRACE_CONT,p,0,0);}ptrace(PTRACE_INTERRUPT,p,0,0);kill(p,SIGSTOP);waitpid(p,&st,0);ptrace(PTRACE_POKETEXT,p,(void*)a,(void*)word);struct user_regs_struct r;ptrace(PTRACE_GETREGS,p,0,&r);if(r.rip==a+1){r.rip=a;ptrace(PTRACE_SETREGS,p,0,&r);}ptrace(PTRACE_DETACH,p,0,0);return 0;}
