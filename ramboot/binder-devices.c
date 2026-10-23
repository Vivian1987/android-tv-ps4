#include <fcntl.h>
#include <errno.h>
#include <linux/android/binderfs.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    int fd = open(argv[1], O_RDONLY | O_CLOEXEC);
    if (fd < 0) { perror("binder-control"); return 1; }
    const char *names[] = {"binder", "hwbinder", "vndbinder"};
    for (unsigned i = 0; i < 3; ++i) {
        struct binderfs_device dev = {0};
        snprintf(dev.name, sizeof(dev.name), "%s", names[i]);
        if (ioctl(fd, BINDER_CTL_ADD, &dev)) {
            if (errno == EEXIST) continue;
            perror(names[i]); return 1;
        }
        printf("%s %u:%u\n", names[i], dev.major, dev.minor);
    }
    close(fd);
    return 0;
}
