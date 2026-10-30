"""
Render a short muted flythrough of the canyon as an MP4 (Blender's bundled FFmpeg).
Used as demo footage on the "Graphics & 3D" dossier.

  blender -b tools/blender/out/city.blend -P tools/blender/render_clip.py -- [--out public/video/dossier-graphics.mp4] [--frames 96] [--samples 24]

city.blend is written by build_city.py.
"""
import bpy, math, os, sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default, cast=str):
    return cast(argv[argv.index(name) + 1]) if name in argv else default

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, arg("--out", "public/video/dossier-graphics.mp4"))
FRAMES = arg("--frames", 96, int)
SAMPLES = arg("--samples", 24, int)

scene = bpy.context.scene
center_y = lambda x: float(scene["dive_y"])   # stay on the crack's centre line
# GPU choice is a user preference, not stored in the .blend
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for dev_type in ("OPTIX", "CUDA"):
        prefs.compute_device_type = dev_type
        prefs.refresh_devices() if hasattr(prefs, "refresh_devices") else prefs.get_devices()
        if any(d.type == dev_type for d in prefs.devices):
            for d in prefs.devices: d.use = d.type == dev_type
            scene.cycles.device = "GPU"
            print("[clip] device", dev_type, flush=True)
            break
except Exception as ex:
    print("[clip] GPU unavailable:", ex, flush=True)
scene.cycles.denoiser = "OPTIX" if scene.cycles.device == "GPU" else "OPENIMAGEDENOISE"
cam_data = bpy.data.cameras.new("clipcam")
cam_data.lens = 18
cam = bpy.data.objects.new("clipcam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
# glide along the canyon while sinking, looking down and ahead
dx = float(scene["dive_x"])
for f, (x, z) in ((1, (dx - 4.5, -2.0)), (FRAMES, (dx + 4.5, -22.0))):
    cam.location = (x, center_y(x), z)
    cam.rotation_euler = (math.radians(38), 0, math.radians(-90))
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
if cam.animation_data and cam.animation_data.action:
    try:
        for fc in cam.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    except AttributeError:
        pass   # layered actions in newer Blender: default easing is fine

scene.frame_start, scene.frame_end = 1, FRAMES
scene.render.fps = 24
scene.render.resolution_x, scene.render.resolution_y = 960, 540
scene.render.film_transparent = False
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
ims = scene.render.image_settings
if hasattr(ims, "media_type"):
    ims.media_type = "VIDEO"
ims.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.ffmpeg.audio_codec = "NONE"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
scene.render.filepath = OUT
bpy.ops.render.render(animation=True)
print("[clip] wrote", OUT, flush=True)
