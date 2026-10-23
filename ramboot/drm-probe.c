#include <amdgpu_drm.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>
int main(void) {
    int fd = open("/dev/dri/renderD128", O_RDWR | O_CLOEXEC);
    if (fd < 0) { perror("render device"); return 1; }
    struct drm_amdgpu_info_device dev = {0};
    struct drm_amdgpu_info query = {0};
    query.return_pointer = (uint64_t)(uintptr_t)&dev;
    query.return_size = sizeof(dev);
    query.query = AMDGPU_INFO_DEV_INFO;
    if (ioctl(fd, DRM_IOCTL_AMDGPU_INFO, &query)) { perror("AMDGPU_INFO_DEV_INFO"); return 1; }
    printf("{\"device_id\":%u,\"chip_rev\":%u,\"external_rev\":%u,\"pci_rev\":%u,\"family\":%u,\"shader_engines\":%u}\n",
           dev.device_id, dev.chip_rev, dev.external_rev, dev.pci_rev, dev.family, dev.num_shader_engines);
    close(fd);
    return 0;
}
