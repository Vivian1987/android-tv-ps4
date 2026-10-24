#include "payload-send.h"
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

/* OpenOrbis 0.5.4's header uses Linux's 0x4000 for MSG_NOSIGNAL.
 * Orbis uses the FreeBSD socket ABI: 0x4000 is MSG_NBIO, 0x20000
 * suppresses SIGPIPE. See FreeBSD releng/9.0 sys/sys/socket.h. */
#ifdef __FreeBSD__
#define ATV_SEND_FLAGS 0x20000
#else
#define ATV_SEND_FLAGS MSG_NOSIGNAL
#endif
int atv_send_payload(const unsigned char *data,size_t bytes,size_t *sent){
 *sent=0;
 if(!data||!bytes){errno=EINVAL;return -1;}
 int sock=socket(AF_INET,SOCK_STREAM,0);if(sock<0)return -1;
 struct timeval timeout={10,0};
 if(setsockopt(sock,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout)))goto failed;
 struct sockaddr_in addr;memset(&addr,0,sizeof(addr));
#ifdef __FreeBSD__
 addr.sin_len=sizeof(addr);
#endif
 addr.sin_family=AF_INET;addr.sin_port=htons(9090);
 addr.sin_addr.s_addr=htonl(0x7f000001);
 if(connect(sock,(struct sockaddr*)&addr,sizeof(addr)))goto failed;
 while(*sent<bytes){
  ssize_t n=send(sock,data+*sent,bytes-*sent,ATV_SEND_FLAGS);
  if(n<0&&errno==EINTR)continue;
  if(n<=0){if(!n)errno=EIO;goto failed;}
  *sent+=(size_t)n;
 }
 if(shutdown(sock,SHUT_WR))goto failed;
 close(sock);return 0;
failed:
 {int saved=errno;close(sock);errno=saved;return -1;}
}
