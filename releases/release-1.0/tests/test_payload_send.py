"""Real localhost transfer, refused connection and injected short/interrupted sends.
No console connection or payload execution: receiver only records bytes.
"""
from pathlib import Path
import ctypes,errno,os,socket,subprocess,tempfile,threading
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)
 subprocess.run(['cc','-shared','-fPIC','-Wall','-Wextra','-Werror',str(root/'source/payload-send.c'),'-o',str(d/'send.so')],check=True)
 lib=ctypes.CDLL(str(d/'send.so'),use_errno=True)
 lib.atv_send_payload.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
 data=os.urandom(335153);buffer=ctypes.create_string_buffer(data);sent=ctypes.c_size_t()
 server=socket.socket();server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);server.bind(('127.0.0.1',9090));server.listen(1)
 received=[]
 def collect():
  c,_=server.accept()
  with c:
   while True:
    b=c.recv(8192)
    if not b:break
    received.append(b)
 thread=threading.Thread(target=collect);thread.start()
 assert lib.atv_send_payload(buffer,len(data),ctypes.byref(sent))==0
 thread.join(5);assert not thread.is_alive();server.close()
 assert sent.value==len(data) and b''.join(received)==data
 assert lib.atv_send_payload(buffer,len(data),ctypes.byref(sent))==-1
 assert ctypes.get_errno()==errno.ECONNREFUSED and sent.value==0
 assert lib.atv_send_payload(buffer,0,ctypes.byref(sent))==-1
 (d/'faults.c').write_text(r'''
#include <assert.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>
#include <string.h>
#include <unistd.h>
static int attempts,closed,writes,eof,mode;
static unsigned char received[80];static size_t count;
static int mock_socket(int a,int b,int c){assert(a==AF_INET&&b==SOCK_STREAM&&c==0);attempts++;return 91;}
static int mock_options(int s,int l,int n,const void*v,socklen_t z){assert(s==91&&l==SOL_SOCKET&&n==SO_SNDTIMEO);assert(z==sizeof(struct timeval)&&((const struct timeval*)v)->tv_sec==10);return 0;}
static int mock_connect(int s,const struct sockaddr*a,socklen_t n){const struct sockaddr_in*p=(const void*)a;assert(s==91&&n==sizeof(*p));assert(p->sin_addr.s_addr==htonl(0x7f000001)&&p->sin_port==htons(9090));return 0;}
static ssize_t mock_send(int s,const void*b,size_t n,int f){assert(s==91&&f==MSG_NOSIGNAL);writes++;if(writes==1){errno=EINTR;return -1;}if(mode&&writes==3){errno=EPIPE;return -1;}if(n>7)n=7;memcpy(received+count,b,n);count+=n;return n;}
static int mock_shutdown(int s,int n){assert(s==91&&n==SHUT_WR);eof++;return 0;}
static int mock_close(int s){assert(s==91);closed++;return 0;}
#define socket mock_socket
#define setsockopt mock_options
#define connect mock_connect
#define send mock_send
#define shutdown mock_shutdown
#define close mock_close
#include "payload-send.c"
int main(void){unsigned char b[80];for(int i=0;i<80;i++)b[i]=i;size_t sent;
assert(atv_send_payload(b,80,&sent)==0&&sent==80&&count==80&&!memcmp(b,received,80));assert(attempts==1&&closed==1&&eof==1);
mode=1;count=0;writes=0;assert(atv_send_payload(b,80,&sent)==-1&&errno==EPIPE&&sent==7);assert(attempts==2&&closed==2&&eof==1);
}
''')
 subprocess.run(['cc','-Wall','-Wextra','-Werror','-I'+str(root/'source'),str(d/'faults.c'),'-o',str(d/'faults')],check=True)
 subprocess.run([str(d/'faults')],check=True)
 print('PASS: actual loopback delivery is byte-exact; refusal/empty payload safe; short sends/EINTR handled; partial failure never retries or executes locally')
