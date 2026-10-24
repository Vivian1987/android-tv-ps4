"""Run the real launcher coordination with an emulated receiver and real files.
No PS4 or network is touched. Check the release is condition-based and errors
never authorize handoff or return the user to the PS4 home screen.
"""
from pathlib import Path
import shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp);shutil.copytree(root/'tests/stubs',d/'stubs');(d/'install').mkdir()
 (d/'stubs/orbis/libkernel.h').write_text('int sceKernelDebugOutText(int,const char*);\nint sceKernelUsleep(unsigned);\nunsigned long long sceKernelGetProcessTime(void);\n')
 (d/'bundled-payload.h').write_text('#define ATV_PAYLOAD_SHA256 "fixture"\nstatic const unsigned char atv_bundled_payload[]={1,2,3};\n')
 (d/'test.c').write_text(r'''
#include "boot-stage.c"
#include <assert.h>
#include <setjmp.h>
static jmp_buf transferred;
static int active,restored,delivery,scenario,closed,phase,draws;
static unsigned long long now;
int ps4_as_root(void(*fn)(void*),void*a){
 if(scenario==2){errno=EACCES;return -1;}
 active=1;fn(a);active=0;restored=1;return 0;
}
int sceKernelDebugOutText(int x,const char*s){(void)x;(void)s;return 0;}
unsigned long long sceKernelGetProcessTime(void){return now+=100000;}
void installer_ui_boot_status(const char*m,const char*d){assert(m&&d);draws++;}
int installer_ui_init(void){return 0;}
static struct atv_launch_control disk_control(void){
 struct atv_launch_control c;int f=open(ATV_CONTROL_PATH,O_RDONLY);assert(f>=0);
 assert(read(f,&c,sizeof(c))==sizeof(c));close(f);return c;
}
int installer_ui_close(void){
 struct atv_launch_control c=disk_control();assert(!c.released&&phase==7);
 if(scenario==6)return -7;
 closed=1;return 0;
}
static void publish(int stage,int rc,int stale,int truncated){
 struct atv_launch_status s={.magic=ATV_LAUNCH_MAGIC,.stage=stage,.rc=rc,.nonce=control.nonce+(stale?1:0)};
 int f=open(ATV_RESULT_PATH,O_WRONLY|O_TRUNC);assert(f>=0);
 int len=truncated?12:sizeof(s);assert(write(f,&s,len)==len);close(f);
}
int atv_send_payload(const unsigned char*p,size_t n,size_t*sent){
 assert(!active&&restored);assert(n==3&&!memcmp(p,atv_bundled_payload,3));delivery++;
 *sent=scenario==1?0:3;if(scenario==1){errno=ECONNREFUSED;return -1;}
 phase=1;publish(1,0,0,0);return 0;
}
int sceKernelUsleep(unsigned n){
 (void)n;
 struct atv_launch_control c=disk_control();
 if(closed){assert(c.released==1&&!c.cancelled&&phase==7);longjmp(transferred,1);}
 assert(!c.released);
 if(scenario==7){now+=100000000;return 0;}
 if(scenario==4&&phase==1){publish(7,0,1,0);phase=2;return 0;}
 if(scenario==5&&phase==1){publish(7,0,0,1);phase=2;return 0;}
 phase++;publish(phase,scenario==3&&phase==4?12:0,0,0);return 0;
}
int main(void){
 for(scenario=0;scenario<8;scenario++){
  active=restored=delivery=closed=phase=draws=0;now=1;
  if(!setjmp(transferred)){
   assert(atv_launch_with_progress()==-1);
   assert(scenario==1||scenario==2||scenario==3||scenario==6||scenario==7);
   assert(!closed);
   if(scenario!=2){struct atv_launch_control c=disk_control();assert(!c.released&&c.cancelled);}
  }else{
   assert(scenario==0||scenario==4||scenario==5);assert(closed&&draws>2);close_channels();
  }
  assert(delivery==(scenario==2?0:1));
 }
 puts("PASS: visible app; credentials restored; release only after ready and display close; stale/partial reports ignored; refusal/root/payload/close/timeout failures never release");
}
''')
 subprocess.run(['cc','-O2','-DROOT="'+str(d/'install')+'"','-DATV_CONTROL_PATH="'+str(d/'control')+'"','-DATV_RESULT_PATH="'+str(d/'result')+'"','-I'+str(d/'stubs'),'-I'+str(root/'source'),'-I'+str(d),str(d/'test.c'),'-o',str(d/'test')],check=True)
 subprocess.run([str(d/'test')],check=True,timeout=10)
