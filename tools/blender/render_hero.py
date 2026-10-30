"""
Offline renders for the hero (run after build_city.py):

  blender -b tools/blender/out/city.blend -P tools/blender/render_hero.py -- [--stills-only | --fall-only | --rain-only]
          [--samples 256] [--fall-samples 48] [--width 2560]

public/hero/
  slab.jpg     beauty frame from the hero camera (the slab layer)
  canyon.jpg   same view with the slab invisible to the camera but still shading the scene
               (what lies under the slab edge, revealed by parallax)
  depth.png    R: canyon depth (camera distance, 17..85 m -> 0..1), G: slab mask
  fall/f_####.webp + fall.json   free fall frames for scroll scrubbing, ending at impact
               (RGBA: the alley floor is a holdout, so the page shows through it)
  rain.mp4     seamless 4 s rain loop over black (additive overlay)
"""
import bpy, json, math, os, sys
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default, cast=str):
    return cast(argv[argv.index(name) + 1]) if name in argv else default
SAMPLES = arg("--samples", 256, int)
FALL_SAMPLES = arg("--fall-samples", 48, int)
WIDTH = arg("--width", 2560, int)
ONLY = next((a[2:-5] for a in argv if a.startswith("--") and a.endswith("-only")), None)   # stills | fall | rain
DO_STILLS = ONLY in (None, "stills")
DO_FALL = ONLY in (None, "fall")
DO_RAIN = ONLY in (None, "rain")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "public", "hero")
TMP = os.path.join(ROOT, "tools", "blender", "out")
os.makedirs(OUT, exist_ok=True)
NEAR, FAR = 17.0, 85.0

scene = bpy.context.scene
cam = scene.camera
slab = bpy.data.objects["Slab"]
D = float(scene["city_depth"])
log = lambda *a: print("[hero]", *a, flush=True)

try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for dev_type in ("OPTIX", "CUDA"):
        prefs.compute_device_type = dev_type
        prefs.refresh_devices() if hasattr(prefs, "refresh_devices") else prefs.get_devices()
        if any(d.type == dev_type for d in prefs.devices):
            for d in prefs.devices: d.use = d.type == dev_type
            scene.cycles.device = "GPU"; log("device", dev_type); break
except Exception as ex:
    log("GPU unavailable:", ex)

def floor_holdout():
    """The alley floor renders as nothing: black in the stills, a transparent hole in the fall."""
    nt = bpy.data.materials["alley"].node_tree
    if any(n.type == "HOLDOUT" for n in nt.nodes): return
    mo = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(nt.nodes.new("ShaderNodeHoldout").outputs[0], mo.inputs["Surface"])
floor_holdout()

def hero_pose():
    cam.animation_data_clear(); cam.data.animation_data_clear()
    cam.location = (0, 0, 18); cam.rotation_euler = (0, 0, 0)
    cam.data.sensor_fit = "VERTICAL"; cam.data.angle_y = math.radians(40)

def still_settings(samples):
    scene.render.resolution_x = WIDTH; scene.render.resolution_y = WIDTH * 9 // 16
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples; scene.cycles.use_denoising = True
    scene.render.use_motion_blur = False
    scene.render.film_transparent = False
    ims = scene.render.image_settings
    if hasattr(ims, "media_type"): ims.media_type = "IMAGE"
    ims.file_format = "JPEG"; ims.quality = 90; ims.color_mode = "RGB"

def render_to(path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    log("wrote", path)

def data_pass(path, hide_slab):
    """Emission override writing (camera distance, slab mask) as raw values."""
    m = bpy.data.materials.new("data_pass")
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    camd = N.new("ShaderNodeCameraData"); info = N.new("ShaderNodeObjectInfo")
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = NEAR; mr.inputs["From Max"].default_value = FAR
    L.new(camd.outputs["View Distance"], mr.inputs["Value"])
    cmp = N.new("ShaderNodeMath"); cmp.operation = "COMPARE"; cmp.inputs[1].default_value = 1.0; cmp.inputs[2].default_value = 0.5
    L.new(info.outputs["Object Index"], cmp.inputs[0])
    cc = N.new("ShaderNodeCombineColor")
    L.new(mr.outputs["Result"], cc.inputs["Red"]); L.new(cmp.outputs[0], cc.inputs["Green"])
    L.new(cc.outputs["Color"], em.inputs["Color"]); L.new(em.outputs["Emission"], out.inputs["Surface"])
    vl = bpy.context.view_layer
    vl.material_override = m
    slab.hide_render = hide_slab
    world_strength = scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    vt, look = scene.view_settings.view_transform, scene.view_settings.look
    try: scene.view_settings.view_transform = "Raw"
    except TypeError: scene.view_settings.view_transform = "Standard"
    scene.cycles.samples = 16; scene.cycles.use_denoising = False
    ims = scene.render.image_settings
    ims.file_format = "PNG"; ims.color_mode = "RGB"; ims.color_depth = "16"
    render_to(path)
    vl.material_override = None
    slab.hide_render = False
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = world_strength
    scene.view_settings.view_transform = vt
    try: scene.view_settings.look = look
    except TypeError: pass
    ims.color_depth = "8"

def load_raw(path):
    im = bpy.data.images.load(path)
    im.colorspace_settings.name = "Non-Color"
    a = np.array(im.pixels[:], np.float32).reshape(im.size[1], im.size[0], 4)
    return a

if DO_STILLS:
    hero_pose()
    still_settings(SAMPLES)
    render_to(os.path.join(OUT, "slab.jpg"))
    slab.visible_camera = False
    render_to(os.path.join(OUT, "canyon.jpg"))
    slab.visible_camera = True
    # passes at half resolution are plenty for parallax
    scene.render.resolution_percentage = 50
    data_pass(os.path.join(TMP, "pass_canyon.png"), hide_slab=True)
    data_pass(os.path.join(TMP, "pass_slab.png"), hide_slab=False)
    scene.render.resolution_percentage = 100
    canyon = load_raw(os.path.join(TMP, "pass_canyon.png"))
    slabp = load_raw(os.path.join(TMP, "pass_slab.png"))
    rgba = np.ones_like(canyon)
    rgba[..., 0] = np.clip(canyon[..., 0], 0, 1)
    rgba[..., 0][canyon[..., 0] <= 0] = 1.0          # background (nothing hit) = far
    rgba[..., 1] = np.clip(slabp[..., 1], 0, 1)
    rgba[..., 2] = 0
    h, w = rgba.shape[:2]
    out = bpy.data.images.new("depth_out", w, h, alpha=False)
    out.colorspace_settings.name = "Non-Color"
    out.pixels.foreach_set(rgba.ravel())
    out.filepath_raw = os.path.join(OUT, "depth.png"); out.file_format = "PNG"; out.save()
    log("wrote depth.png", w, h)

if DO_FALL:
    # A frame sequence the page scrubs with the scroll position. Frame 1 is the
    # hero still; the last frame is the instant of impact (top speed) — the page
    # then cuts to the archive on its own.
    #
    # The camera rides a simulated falling body rather than hand-set keys: it is
    # let go at rest above the slab with a small push towards the crack, and
    # gravity, air drag and the drag's restoring torque do the rest, so speed,
    # drift and sway all come out continuous.
    hero_pose()
    fps = 60                        # scrubbed frame by frame, so render at display rate
    scene.render.fps = fps
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
    scene.render.resolution_percentage = 100
    scene.cycles.samples = FALL_SAMPLES; scene.cycles.use_denoising = True
    scene.render.use_motion_blur = False          # the page blends frames; blur only softened them
    scene.render.film_transparent = True
    dx, dy = float(scene["dive_x"]), float(scene["dive_y"])
    lens0 = cam.data.lens
    z0, z_lip, z_floor = 18.0, 1.8, -D + 0.5

    G, VT = 9.81, 55.0                      # gravity, terminal speed of a falling body
    K_H = 1.6                               # horizontal drag (1/s)
    K_ROT, DAMP = 0.06, 0.9                 # aerodynamic restoring torque ~ v^2, angular damping
    SUB = 8                                 # integration substeps per frame
    def simulate(push):
        """Integrate the body; returns per-frame (pos, pitch, roll, yaw, speed) until impact."""
        dt = 1 / (fps * SUB)
        px, py, pz = 0.0, 0.0, z0
        vx, vy, vz = push[0], push[1], 0.0
        pitch, roll, yaw = 0.0, 0.0, 0.0
        wp, wr, wy = math.radians(2.5), math.radians(-1.8), math.radians(7.0)   # spin from letting go
        out = [((px, py, pz), pitch, roll, yaw, 0.0)]
        while pz > z_floor:
            for _ in range(SUB):
                vz += (-G + G * (vz / VT) ** 2) * dt
                vx -= K_H * vx * dt; vy -= K_H * vy * dt
                v2 = vx * vx + vy * vy + vz * vz
                wp += (-K_ROT * v2 * pitch - DAMP * wp) * dt
                wr += (-K_ROT * v2 * roll - DAMP * wr) * dt
                px += vx * dt; py += vy * dt; pz += vz * dt
                pitch += wp * dt; roll += wr * dt; yaw += wy * dt
                if pz <= z_floor: pz = z_floor; break
            out.append(((px, py, pz), pitch, roll, yaw, math.sqrt(v2)))
        return out
    # aim the push so the drag brings the body to rest over the widest part of the crack
    push = (dx * K_H, dy * K_H)
    path = simulate(push)
    total = len(path) - 1
    v_max = path[-1][4]
    for f, ((x, y, z), pitch, roll, yaw, v) in enumerate(path):
        k = v / v_max
        cam.location = (x, y, z); cam.rotation_euler = (pitch, roll, yaw)
        cam.data.lens = lens0 * (1 - 0.3 * k * k * (3 - 2 * k))      # wider as the speed builds
        cam.keyframe_insert("location", frame=f + 1)
        cam.keyframe_insert("rotation_euler", frame=f + 1)
        cam.data.keyframe_insert("lens", frame=f + 1)
    scene.frame_start, scene.frame_end = 1, total + 1

    ims = scene.render.image_settings
    if hasattr(ims, "media_type"): ims.media_type = "IMAGE"
    ims.file_format = "WEBP"; ims.quality = 80; ims.color_mode = "RGBA"
    seq_dir = os.path.join(OUT, "fall")
    os.makedirs(seq_dir, exist_ok=True)
    for old in os.listdir(seq_dir): os.remove(os.path.join(seq_dir, old))
    scene.render.filepath = os.path.join(seq_dir, "f_")
    with open(os.path.join(OUT, "fall.json"), "w") as fp:
        json.dump({"frames": total + 1, "fps": fps, "zStart": z0, "zLip": z_lip, "zFloor": z_floor,
                   "slab": float(scene["city_slab"]), "depth": D,
                   "z": [round(p[0][2], 3) for p in path],
                   "lip": next(i for i, p in enumerate(path) if p[0][2] <= z_lip),
                   "pattern": "fall/f_{n:04}.webp", "first": 1}, fp)
    log(f"fall: {total + 1} frames, impact at {v_max:.1f} m/s")
    bpy.ops.render.render(animation=True)
    scene.render.film_transparent = False
    log("wrote fall sequence")

if DO_RAIN:
    # Seamless rain loop seen from the hero camera, rendered over black and
    # composited additively in the page. Slab and buildings are holdouts, so
    # drops behind them disappear exactly where real rain would.
    # Looking down, rain is mostly faint slanted streaks (each one the distance
    # a drop covers while a 1/60 s shutter is open, tapered at both ends), near
    # drops melt into soft bokeh. Drops stop where they hit the slab; the page's
    # ripple simulation draws the splashes.
    import bmesh, random
    from mathutils import Vector
    hero_pose()
    rr = random.Random(11)
    fps, LOOP = 60, 4.0
    frames = int(fps * LOOP)
    scene.render.fps = fps
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
    scene.render.resolution_percentage = 100
    scene.render.use_motion_blur = False          # handler-driven meshes don't blur; streaks are modelled
    scene.cycles.samples = 64; scene.cycles.use_denoising = False
    scene.render.use_persistent_data = False
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 18.0; cam.data.dof.aperture_fstop = 2.0
    for ob in list(bpy.data.objects):            # includes the meshes inside instanced plant collections
        if ob.type in ("MESH", "EMPTY"): ob.is_holdout = True
        if ob.type == "LIGHT": ob.hide_render = True
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    scene.view_settings.view_transform = "Standard"
    Z_TOP, Z_BOT = 16.5, -18.0
    H = Z_TOP - Z_BOT
    WIND = Vector((0.16, 0.05, -1.0)).normalized()   # slight slant, so streaks don't all point at the centre
    V = H / LOOP                                     # base speed; each drop wraps 2 or 3 times per loop: seamless
    deps = bpy.context.evaluated_depsgraph_get()
    drops, stops = [], []
    for _ in range(3400):
        x, y = rr.uniform(-13, 13), rr.uniform(-7.5, 7.5)
        # (x, y, phase, brightness, wraps per loop, streak length factor): most drops are barely
        # there, a few catch the light; mixed speeds and streak lengths read as depth
        drops.append((x, y, rr.uniform(0, H), 0.12 + 0.88 * rr.random() ** 2.2,
                      3 if rr.random() < 0.3 else 2, rr.uniform(0.6, 1.4)))
        # where this drop's path meets the slab top (none over the crack)
        hit, loc, *_ = scene.ray_cast(deps, Vector((x, y, Z_TOP)), WIND)
        stops.append(loc.z if hit and loc.z > -0.05 else None)

    me = bpy.data.meshes.new("rain")
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    R = 0.0011                                       # streak half-width
    STREAK = 2 * V * 0.5 / fps                       # 180-degree shutter at 60 fps, ~14 cm at 2 wraps
    def quad(cs, mat):
        f = bm.faces.new([bm.verts.new(c) for c in cs])
        f.material_index = mat
        for loop, c in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): loop[uv].uv = c
    for _ in drops:
        for ax, ay in ((R, 0), (0, R)):
            quad(((-ax, -ay, 0), (ax, ay, 0), (ax, ay, 1), (-ax, -ay, 1)), 0)   # z = 0 head .. 1 tail
    bm.to_mesh(me); bm.free()
    rain = bpy.data.objects.new("rain", me); scene.collection.objects.link(rain)

    def emit_mat(name, strength):
        m = bpy.data.materials.new(name)
        try: m.use_nodes = True
        except Exception: pass
        N = m.node_tree.nodes; Lk = m.node_tree.links
        for n in list(N): N.remove(n)
        out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (0.55, 0.62, 0.66, 1)   # grey-blue: water picks up the overcast sky
        att = N.new("ShaderNodeAttribute"); att.attribute_name = "drop_b"; att.attribute_type = "GEOMETRY"
        Lk.new(strength(N, Lk, att.outputs["Fac"]), em.inputs["Strength"])
        Lk.new(em.outputs["Emission"], out.inputs["Surface"])
        return m
    def node_op(N, Lk, op, a, b):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, float): n.inputs[i].default_value = v
            else: Lk.new(v, n.inputs[i])
        return n.outputs[0]
    def drop_strength(N, Lk, b):
        tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ")
        Lk.new(tc.outputs["UV"], sep.inputs["Vector"])
        taper = node_op(N, Lk, "SINE", node_op(N, Lk, "MULTIPLY", sep.outputs["Y"], 3.14159), 0.0)
        # a sharp highlight near the head over a faint smear (drops glint, they aren't lines)
        y = node_op(N, Lk, "MULTIPLY", taper, 0.35)
        head = node_op(N, Lk, "POWER", node_op(N, Lk, "SUBTRACT", 1.0, sep.outputs["Y"]), 5.0)
        y = node_op(N, Lk, "ADD", y, node_op(N, Lk, "MULTIPLY", node_op(N, Lk, "MULTIPLY", head, taper), 1.6))
        return node_op(N, Lk, "MULTIPLY", node_op(N, Lk, "MULTIPLY", y, b), 2.2)
    me.materials.append(emit_mat("rain_drop", drop_strength))
    attr = me.attributes.new("drop_b", "FLOAT", "POINT")
    base = [v.co.copy() for v in me.vertices]
    PARK = (0.0, 0.0, -500.0)

    def place(scn, *_):
        t = (scn.frame_current - 1) / fps
        co, br = [], []
        for i, (x, y, z0, b, k, ln) in enumerate(drops):
            s = (z0 + k * V * t) % H                  # height fallen this wrap
            p = Vector((x, y, Z_TOP)) + WIND * (s / -WIND.z)
            gone = stops[i] is not None and p.z < stops[i]   # landed on the slab: hidden until it wraps
            for j in range(8):
                q = base[i * 8 + j]
                e = p - WIND * (STREAK * k / 2 * ln * q.z)   # tail trails up the path
                co.extend(PARK if gone else (e.x + q.x, e.y + q.y, e.z))
                br.append(b)
        me.vertices.foreach_set("co", co)
        attr.data.foreach_set("value", br)
        me.update()
    bpy.app.handlers.frame_change_pre.append(place)
    scene.frame_start, scene.frame_end = 1, frames
    ims = scene.render.image_settings
    if hasattr(ims, "media_type"): ims.media_type = "VIDEO"
    ims.file_format = "FFMPEG"
    ff = scene.render.ffmpeg
    ff.format = "MPEG4"; ff.codec = "H264"; ff.constant_rate_factor = "HIGH"; ff.gopsize = 15; ff.audio_codec = "NONE"
    scene.render.filepath = os.path.join(OUT, "rain.mp4")
    bpy.ops.render.render(animation=True)
    log("wrote rain.mp4")
