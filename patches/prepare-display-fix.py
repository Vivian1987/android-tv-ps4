"""Generate a reviewed, PS4-only primary-plane format fix; do not touch live build."""
from pathlib import Path
import difflib
root=Path('/home/amber/projects/ps4-android/kernel-6.15.4')
rel='drivers/gpu/drm/amd/amdgpu/dce_v8_0.c'
a=(root/rel).read_text()
b=a.replace('#include <drm/drm_vblank.h>', '#include <drm/drm_vblank.h>\n#include <drm/drm_plane_helper.h>')
needle='static int dce_v8_0_crtc_init(struct amdgpu_device *adev, int index)'
helper='''/* Liverpool supports both channel orders in dce_v8_0_crtc_do_set_base().
 * drm_crtc_init() advertises only XRGB/ARGB, which makes the modern framebuffer
 * verifier reject Android's XBGR buffers before reaching that hardware code.
 * Give this PS4 its own accurate primary-plane formats; retain validation.
 */
static const uint32_t liverpool_primary_formats[] = {
	DRM_FORMAT_XRGB8888, DRM_FORMAT_ARGB8888,
	DRM_FORMAT_XBGR8888, DRM_FORMAT_ABGR8888,
};

static const struct drm_plane_funcs liverpool_primary_funcs = {
	DRM_PLANE_NON_ATOMIC_FUNCS,
};

static int liverpool_crtc_init(struct drm_device *dev, struct drm_crtc *crtc,
			       const struct drm_crtc_funcs *funcs)
{
	struct drm_plane *primary;
	int ret;

	primary = __drm_universal_plane_alloc(dev, sizeof(*primary), 0, 0,
					      &liverpool_primary_funcs,
					      liverpool_primary_formats,
					      ARRAY_SIZE(liverpool_primary_formats),
					      NULL, DRM_PLANE_TYPE_PRIMARY, NULL);
	if (IS_ERR(primary))
		return PTR_ERR(primary);
	ret = drm_crtc_init_with_planes(dev, crtc, primary, NULL, funcs, NULL);
	if (ret) {
		drm_plane_cleanup(primary);
		kfree(primary);
	}
	return ret;
}

'''
b=b.replace(needle,helper+needle)
b=b.replace('static int dce_v8_0_crtc_init(struct amdgpu_device *adev, int index)\n{\n\tstruct amdgpu_crtc *amdgpu_crtc;', 'static int dce_v8_0_crtc_init(struct amdgpu_device *adev, int index)\n{\n\tstruct amdgpu_crtc *amdgpu_crtc;\n\tint ret;')
old='\tdrm_crtc_init(adev_to_drm(adev), &amdgpu_crtc->base, &dce_v8_0_crtc_funcs);'
new='''	if (adev->asic_type == CHIP_LIVERPOOL)
		ret = liverpool_crtc_init(adev_to_drm(adev), &amdgpu_crtc->base,
					 &dce_v8_0_crtc_funcs);
	else
		ret = drm_crtc_init(adev_to_drm(adev), &amdgpu_crtc->base,
				    &dce_v8_0_crtc_funcs);
	if (ret) {
		kfree(amdgpu_crtc);
		return ret;
	}'''
assert old in b
b=b.replace(old,new)
out=Path(__file__).parent/'liverpool-primary-formats.patch'
out.write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)))
print(out)
