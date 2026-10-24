"""Check connector filtering through real dynamic-symbol interposition."""
from pathlib import Path
import tempfile,subprocess,os
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)
 (d/'fake.c').write_text(r'''
#define drmModeGetConnector hidden_get
#define drmModeGetConnectorCurrent hidden_current
#include "display-modes.c"
#undef drmModeGetConnector
#undef drmModeGetConnectorCurrent
static struct atv_mode modes[4];static struct atv_connector c;
struct atv_connector *drmModeGetConnector(int fd,uint32_t id){
 (void)id;if(fd<0)return 0;
 modes[0]=(struct atv_mode){.vrefresh=120,.type=8};
 modes[1]=(struct atv_mode){.vrefresh=60,.hdisplay=1920,.vdisplay=1080};
 modes[2]=(struct atv_mode){.vrefresh=60,.flags=1<<4};
 modes[3]=(struct atv_mode){.vrefresh=50,.hdisplay=1280,.vdisplay=720};
 c=(struct atv_connector){.count_modes=4,.modes=modes};return &c;
}
struct atv_connector *drmModeGetConnectorCurrent(int fd,uint32_t id){return drmModeGetConnector(fd,id);}
''')
 (d/'probe.c').write_text(r'''
#define drmModeGetConnector hidden_get
#define drmModeGetConnectorCurrent hidden_current
#include "display-modes.c"
#undef drmModeGetConnector
#undef drmModeGetConnectorCurrent
#include <assert.h>
#include <stdio.h>
extern struct atv_connector *drmModeGetConnector(int,uint32_t);
extern struct atv_connector *drmModeGetConnectorCurrent(int,uint32_t);
int main(void){
 assert(!drmModeGetConnector(-1,0));
 for(int i=0;i<2;i++){
 struct atv_connector*c=i?drmModeGetConnectorCurrent(1,0):drmModeGetConnector(1,0);
 assert(c&&c->count_modes==2&&c->modes[0].vrefresh==60&&c->modes[0].hdisplay==1920&&c->modes[1].vrefresh==50);
 }
 struct atv_mode m={.vrefresh=120};struct atv_connector c={.count_modes=1,.modes=&m};
 assert(atv_filter_modes(&c)==0&&c.count_modes==0);assert(!atv_filter_modes(0));
 puts("PASS: real preload filters 120 Hz and interlaced modes before caller sees them; keeps 60/50 Hz; null/unsupported connectors safe");
}
''')
 common=['cc','-O2','-I'+str(root/'source')]
 subprocess.run(common+['-shared','-fPIC',str(root/'source/display-modes.c'),'-ldl','-o',str(d/'filter.so')],check=True)
 subprocess.run(common+['-shared','-fPIC',str(d/'fake.c'),'-ldl','-o',str(d/'libfake.so')],check=True)
 subprocess.run(common+[str(d/'probe.c'),'-L'+str(d),'-lfake','-ldl','-Wl,-rpath,'+str(d),'-o',str(d/'probe')],check=True)
 subprocess.run([str(d/'probe')],env=dict(os.environ,LD_PRELOAD=str(d/'filter.so')),check=True)
