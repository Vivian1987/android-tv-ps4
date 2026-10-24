from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)
 (p/'test.c').write_text(r'''
#include "display-release.h"
#include <assert.h>
#include <stdio.h>
static unsigned long long now;static int reads,scenario;
static unsigned long long clock_us(void){return now+=1000000;}
static int sleep_us(unsigned delay){assert(delay==10000);return 0;}
static int read_control(struct atv_launch_control*c){
 reads++;*c=(struct atv_launch_control){.magic=ATV_LAUNCH_MAGIC,.version=ATV_LAUNCH_VERSION,.nonce=42,.launcher_pid=100};
 if(scenario==0)c->released=reads==5;
 if(scenario==1){c->nonce=41;c->released=1;}
 if(scenario==2){c->cancelled=1;c->released=1;}
 if(scenario==3)return -1;
 if(scenario==5){c->version=0;c->released=1;}
 return 0;
}
int main(void){
 const int expected[]={0,-111,-112,-111,-113,-111};
 for(scenario=0;scenario<6;scenario++){
  now=reads=0;assert(atv_wait_display_release(42,read_control,clock_us,sleep_us)==expected[scenario]);
  if(scenario==0)assert(reads==5);if(scenario==4)assert(reads>1);
 }
 puts("PASS: receiver requires matching release; stale/cancelled/failed/version-mismatched controls and timeout never authorize ARM");
}
''')
 subprocess.run(['cc','-O2','-I'+str(root/'source'),str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
