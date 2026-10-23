"""Configure and build the CUH-1102A Android kernel on Ember's SSD."""
from pathlib import Path
import hashlib, json, subprocess

project = Path(__file__).resolve().parent
root = Path('/home/amber/projects/ps4-android/kernel-6.15.4')
# A PS4-only correction: advertise the channel orders DCE already handles.
patch = project/'patches/liverpool-primary-formats.patch'
probe = subprocess.run(['patch', '--dry-run', '-R', '-p1', '-i', str(patch)],
                       cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if probe.returncode:
    subprocess.run(['patch', '-p1', '-i', str(patch)], cwd=root, check=True)
config = root/'scripts/config'
required = ['CPUSETS', 'CPUSETS_V1', 'PROC_PID_CPUSET', 'MEMCG', 'MEMCG_V1', 'SECURITY', 'SECURITY_NETWORK', 'SECURITYFS',
    'SECURITY_SELINUX', 'SECURITY_SELINUX_DEVELOP', 'SECURITY_SELINUX_BOOTPARAM',
    'SQUASHFS', 'SQUASHFS_XZ', 'SQUASHFS_ZSTD', 'ANDROID_BINDER_IPC',
    'ANDROID_BINDERFS', 'PSI', 'TMPFS_XATTR', 'TMPFS_POSIX_ACL',
    'NET_NS', 'PID_NS', 'IPC_NS', 'UTS_NS', 'MACVLAN', 'VETH', 'MWIFIEX',
    'MWIFIEX_SDIO', 'BT_MRVL', 'BT_MRVL_SDIO', 'CGROUP_BPF', 'BPF_SYSCALL',
    'BPF_JIT', 'NET_ACT_BPF', 'NET_ACT_POLICE', 'NET_CLS_MATCHALL',
    'NET_EMATCH', 'NET_EMATCH_U32', 'NET_SCH_INGRESS', 'NET_SCH_TBF', 'DUMMY',
    'IP_NF_IPTABLES_LEGACY', 'IP6_NF_IPTABLES_LEGACY',
    'IP_NF_FILTER', 'IP_NF_MANGLE', 'IP_NF_RAW', 'IP_NF_SECURITY', 'IP_NF_NAT',
    'IP6_NF_FILTER', 'IP6_NF_MANGLE', 'IP6_NF_RAW', 'IP6_NF_NAT',
    'DMABUF_HEAPS', 'DMABUF_HEAPS_SYSTEM', 'DEBUG_INFO_NONE']
args = [str(config), '--file', str(root/'.config')]
for name in required:
    args += ['--enable', name]
for name in ['DEBUG_INFO_BTF', 'DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT',
             'DEBUG_INFO_DWARF4', 'DEBUG_INFO_DWARF5', 'MODULE_SIG',
             'SYSTEM_TRUSTED_KEYRING', 'SYSTEM_REVOCATION_LIST', 'WERROR', 'MT76X8']:
    args += ['--disable', name]
for name, value in [('LOCALVERSION', '-cole-android-aeolia-v1'), ('EXTRA_FIRMWARE', ''),
                    ('SYSTEM_TRUSTED_KEYS', ''), ('SYSTEM_REVOCATION_KEYS', ''),
                    ('LSM', 'selinux')]:
    args += ['--set-str', name, value]
subprocess.run(args, check=True)
subprocess.run(['make', 'olddefconfig'], cwd=root, check=True, stdout=subprocess.DEVNULL)
settings = (root/'.config').read_text().splitlines()
missing = [name for name in required if f'CONFIG_{name}=y' not in settings]
assert not missing, f'Kernel dependencies disabled required settings: {missing}'
assert 'CONFIG_X86_PS4=y' in settings
assert 'CONFIG_SKY2=y' in settings
assert 'CONFIG_DRM_AMDGPU=y' in settings
assert 'CONFIG_DEBUG_INFO=y' not in settings
commit = subprocess.check_output(['git', '-C', str(project/'reference/ps4-kernel-6.15.4'), 'rev-parse', 'HEAD'], text=True).strip()
evidence = {'source_commit': commit, 'display_patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'config_sha256': hashlib.sha256((root/'.config').read_bytes()).hexdigest(),
    'required_features_verified': required, 'target': 'CUH-1102A B01 Android TV', 'runtime': str(root)}
(project/'evidence/android-kernel-config').write_bytes((root/'.config').read_bytes())
(project/'evidence/android-kernel-build-start.json').write_text(json.dumps(evidence, indent=2)+'\n')
print('All required kernel features verified; compiling.', flush=True)
log = root.parent/'android-kernel-build.log'
with log.open('w') as f:
    result = subprocess.run(['make', '-j6', 'bzImage'], cwd=root, stdout=f, stderr=subprocess.STDOUT)
print('Kernel build exit:', result.returncode, flush=True)
print('\n'.join(log.read_text(errors='replace').splitlines()[-18:]), flush=True)
if result.returncode:
    raise SystemExit(result.returncode)
image = root/'arch/x86/boot/bzImage'
evidence.update(bytes=image.stat().st_size, sha256=hashlib.sha256(image.read_bytes()).hexdigest(), build_exit=0)
(project/'evidence/android-kernel-build.json').write_text(json.dumps(evidence, indent=2)+'\n')
print(json.dumps(evidence, indent=2), flush=True)
