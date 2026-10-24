/* LLVM also emits these calls for aggregate initialization. The legacy SDK
 * declares them as data (function pointers), which cannot satisfy libcalls. */
#include "types.h"
void *memset(void *dst,int value,size_t size) {
 volatile unsigned char *p=dst;for(size_t i=0;i<size;i++)p[i]=(unsigned char)value;return dst;
}
void *memcpy(void *dst,const void *src,size_t size) {
 volatile unsigned char *d=dst;const volatile unsigned char *s=src;
 for(size_t i=0;i<size;i++)d[i]=s[i];return dst;
}
void *memmove(void *dst,const void *src,size_t size) {
 volatile unsigned char *d=dst;const volatile unsigned char *s=src;
 if((uintptr_t)d<(uintptr_t)s){for(size_t i=0;i<size;i++)d[i]=s[i];}
 else {while(size){size--;d[size]=s[size];}}return dst;
}
