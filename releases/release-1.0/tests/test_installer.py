from pathlib import Path
import tempfile,subprocess
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as t:
 d=Path(t);(d/'image-metadata.h').write_text('#define SYSTEM_BYTES 13ULL\n#define DATA_BYTES 34359738368ULL\n#define YOUTUBE_BYTES 13ULL\n')
 subprocess.run(['cc','-O2','-DRAW_IMAGES','-DEDITION_GIB=32','-DROOT="'+str(d/'install')+'"','-DBOOT_PARENT="'+str(d/'linux')+'"','-I'+str(root/'tests/stubs'),'-I'+str(root/'source'),'-I'+str(d),str(root/'tests/test_installer.c'),str(root/'source/image-copy.c'),'-o',str(d/'test')],check=True)
 subprocess.run([str(d/'test')],check=True)
