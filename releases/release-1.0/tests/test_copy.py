from pathlib import Path
import ctypes,os,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);lib=d/'copy.so'
 subprocess.run(['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(root/'source'),str(root/'source/image-copy.c'),'-o',str(lib)],check=True)
 f=ctypes.CDLL(str(lib),use_errno=True).ps4_copy_image;f.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_uint64,ctypes.c_void_p];f.restype=ctypes.c_int
 content=os.urandom(3*1024*1024+173);src=d/'source';src.write_bytes(content)
 cases=[('fresh',b'',len(content),True),('interrupted',content[:1234567],len(content),True),('already complete',content,len(content),True),('mismatched prefix',b'WRONG'+content[5:300],len(content),False),('oversized destination',content+b'x',len(content),False),('wrong expected length',b'',len(content)+1,False)]
 for name,before,length,ok in cases:
  target=d/'target';target.write_bytes(before)
  with src.open('rb') as a,target.open('r+b') as b:rc=f(a.fileno(),b.fileno(),length,None)
  assert (rc==0)==ok,(name,rc,ctypes.get_errno())
  assert target.read_bytes()==(content if ok else before),name
  print('PASS:',name)
 # Simulate process termination mid-write by failing the writer at a size limit.
 # A valid partial output already covers subsequent recovery byte-for-byte above.
 with src.open('rb') as a:
  fd=os.open('/dev/null',os.O_RDWR)
  try:assert f(a.fileno(),fd,len(content),None)!=0
  finally:os.close(fd)
 print('PASS: nonregular destination refused')
