# Android-to-console power control

Android init is PID 1 in a child PID namespace. Linux handles `reboot()` from that namespace by terminating its init and reporting SIGHUP for restart or SIGINT for halt/power-off to the parent. It does not reboot the initial namespace. See `kernel/pid_namespace.c:reboot_pid_ns` in the shipped kernel source.

`android-supervisor` remains in the host namespace and creates Android's PID/mount/network/UTS/IPC namespaces with `clone`. It publishes the actual child PID for network-interface attachment and waits for init to exit.

- SIGHUP termination: restart the physical console.
- SIGINT termination: power off the physical console.
- Normal exit or other signal: report failure, do not power-cycle the console.

Before issuing a host power syscall, the helper requires PS4 boot markers, asks the bootstrap log monitor to finish, synchronizes storage, and unmounts userdata/system/UFS mounts in order. It refuses to proceed if unmounting fails. The PS4 kernel routes restart/power-off to its ICC hooks; these already exist in the kernel and are unchanged by this patch.

Build on Linux x86-64 with static libc:

```
cc -static -O2 -Wall -Wextra -Werror android-supervisor.c -o android-supervisor
```

Safe namespace tests (root or equivalent namespace privileges required):

```
sudo ./android-supervisor --test restart
sudo ./android-supervisor --test poweroff
sudo ./android-supervisor --test crash
```

Test mode creates only child PID/mount namespaces, deliberately calls reboot inside the child namespace, and prints the mapped action. **It never calls host reboot or unmounts host filesystems.** Production also creates network, UTS and IPC namespaces, enabled in the PS4 kernel. The development host lacks UTS/IPC namespace support, so those flags cannot be exercised there.

Tests passed for restart → SIGHUP, power-off → SIGINT, and unexpected exit → no action. They do not prove the PS4's physical power behaviour or full shutdown unmount sequence. Those require the console acceptance test.
