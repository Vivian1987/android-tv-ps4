#include <stddef.h>
#include <unistd.h>
typedef struct {int type,targetId;char message[1024];} OrbisNotificationRequest;
#define NotificationRequest 0
static int sceKernelDebugOutText(int x,const char*y){(void)x;(void)y;return 0;}
static int sceKernelSendNotificationRequest(int a,const void*b,size_t c,int d){(void)a;(void)b;(void)c;(void)d;return 0;}
static int sceKernelUsleep(unsigned x){(void)x;return 0;}
