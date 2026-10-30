"""
Third-party props for build_city.py: cloth-simulated laundry and potted plants.

Sources (git-ignored, unpacked by hand into tools/blender/assets/):
  assets/tshirt/t shirt.fbx                              Marvelous Designer T-shirt
  assets/banjo/PlantBanjoFig001_Blender_Cycles.blend     potted banjo fig
  assets/zz/PlantZZ001_Blender_Cycles.blend              potted ZZ plant
Fabric textures come from Poly Haven via fetch_textures.mjs.

Laundry is simulated once per variant (Blender cloth, pinned where a hanger or
pegs would hold it, a little wind) and frozen into plain meshes; build_city
then places many objects that share those meshes, each with its own fabric.
"""
import bpy, bmesh, math, os, random, time
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
TEX = os.path.join(HERE, "textures")
PROGRESS = os.path.join(HERE, "out", "props_progress.log")   # one line per simulated frame: tail it to watch


def log(*a):
    line = "[props] " + " ".join(str(x) for x in a)
    print(line, flush=True)
    os.makedirs(os.path.dirname(PROGRESS), exist_ok=True)
    with open(PROGRESS, "a", encoding="utf8") as fp: fp.write(time.strftime("%H:%M:%S ") + line + "\n")


def _need(path):
    if not os.path.exists(path):
        raise SystemExit(f"missing {path}: unpack the model zips into tools/blender/assets/ (see README)")
    return path


def _sock(sockets, ident):
    return next(s for s in sockets if s.identifier == ident)


def _new_obj(name, me, scene):
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def _activate(obs):
    for o in bpy.context.view_layer.objects:
        if o: o.select_set(False)
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]


# ---------------------------------------------------------------- cloth simulation
def _wind(scene, strength, yaw):
    """A wind effector blowing horizontally towards `yaw` (radians)."""
    try:
        w = bpy.data.objects.new("wind", None)
        scene.collection.objects.link(w)
        w.field.type = "WIND"
    except (AttributeError, TypeError):
        bpy.ops.object.effector_add(type="WIND")
        w = bpy.context.object
    w.field.strength = strength; w.field.noise = 1.2; w.field.flow = 0.0
    w.rotation_euler = (math.radians(90), 0, yaw)            # field axis = local Z, laid horizontal
    return w


def _simulate(ob, pin, frames, scene, wind=0.0, yaw=0.0, mass=0.15, bend=0.05, self_collide=True, gather=1.0):
    """Run Blender cloth on `ob` with vertices where pin(co) is true held fixed; returns the final mesh.

    gather < 1 slides the pinned vertices towards x = 0 over the first third of
    the run (a shape key; the rest shape stays the flat original), so a sheet
    bunches on its pole or sags between pegs the way real cloth does.
    """
    pinned = [v.index for v in ob.data.vertices if pin(v.co)]
    vg = ob.vertex_groups.new(name="pin")
    vg.add(pinned, 1.0, "REPLACE")
    if gather < 1.0:
        ob.shape_key_add(name="Basis")
        k = ob.shape_key_add(name="gather")
        for i in pinned: k.data[i].co.x *= gather
        k.value = 0.0; k.keyframe_insert("value", frame=1)
        k.value = 1.0; k.keyframe_insert("value", frame=max(2, frames // 3))
    md = ob.modifiers.new("cloth", "CLOTH")
    s = md.settings
    s.quality = 8; s.mass = mass; s.air_damping = 1.5
    s.tension_stiffness = s.compression_stiffness = 12.0
    s.shear_stiffness = 6.0; s.bending_stiffness = bend
    s.vertex_group_mass = "pin"; s.pin_stiffness = 1.0
    c = md.collision_settings
    c.collision_quality = 3; c.distance_min = 0.004
    c.use_self_collision = self_collide; c.self_distance_min = 0.004
    md.point_cache.frame_start = 1; md.point_cache.frame_end = frames
    w = _wind(scene, wind, yaw) if wind > 0 else None
    log(f"sim {ob.name}: {len(ob.data.vertices)} verts, {frames} frames")
    t0 = time.time()
    for f in range(1, frames + 1):
        t = time.time()
        scene.frame_set(f)
        log(f"  {ob.name} frame {f}/{frames} {time.time() - t:.2f}s")
    log(f"sim {ob.name} done in {time.time() - t0:.0f}s")
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    log(f"  {ob.name}: pinned {len(pinned)} verts")
    if w: bpy.data.objects.remove(w)
    scene.frame_set(1)
    return me


def _shirt_base(scene):
    """The T-shirt as one cloth surface, decimated to sim resolution; origin at the hanger hook.

    Marvelous Designer exports every pattern piece as a thin shell (front, back and
    rim, one material slot each). Only the front surfaces are kept; they meet at the
    seams and weld into a single connected garment.
    """
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=_need(os.path.join(ASSETS, "tshirt", "t shirt.fbx")))
    new = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    bm = bmesh.new()
    for o in new:
        if any(m and "Knit" in m.name for m in o.data.materials):
            t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
            bmesh.ops.delete(t, geom=[f for f in t.faces if f.material_index != 0], context="FACES")
            tmp = bpy.data.meshes.new("panel"); t.to_mesh(tmp); t.free()
            bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
        bpy.data.objects.remove(o)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.003)
    me = bpy.data.meshes.new("shirt"); bm.to_mesh(me); bm.free()
    ob = _new_obj("shirt_dec", me, scene)
    dec = ob.modifiers.new("dec", "DECIMATE"); dec.ratio = min(1.0, 6000 / max(1, len(me.polygons)))
    _activate([ob]); bpy.ops.object.modifier_apply(modifier=dec.name)
    me = ob.data; bpy.data.objects.remove(ob)
    me.materials.clear()
    for p in me.polygons: p.material_index = 0; p.use_smooth = True
    # origin: centre of the shoulder line (top of the shirt)
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zt = max(v.co.z for v in me.vertices)
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, zt))
    for v in me.vertices: v.co -= off
    log("shirt base", len(me.polygons), "faces,", len(me.vertices), "verts, width", round(max(xs) - min(xs), 2), "height", round(zt - min(v.co.z + off.z for v in me.vertices), 2))
    return me


def _sheet_mesh(w, h, nx, ny):
    """Flat cloth rectangle in XY (x along the pole), UV 0..1."""
    me = bpy.data.meshes.new("sheet")
    bm = bmesh.new()
    bm.loops.layers.uv.new("UVMap")                 # create_grid only fills an existing UV layer
    bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=0.5, calc_uvs=True)
    for v in bm.verts: v.co.x *= w; v.co.y *= h
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me


def laundry_meshes(scene):
    """Simulated variants: {'shirt': [...], 'sheet_over': [...], 'sheet_pegged': [...], 'towel': [...]}."""
    out = {"shirt": [], "sheet_over": [], "sheet_pegged": [], "towel": []}
    base = _shirt_base(scene)
    for i, (wind, yaw) in enumerate(((0.0, 0.0), (6.0, 0.4), (14.0, -0.3))):
        ob = _new_obj(f"shirt_sim{i}", base.copy(), scene)
        # a hanger holds both shoulder seams: the top 2 cm of each side, clear of the collar
        top = {sd: max(v.co.z for v in ob.data.vertices if v.co.x * sd > 0.06) for sd in (1, -1)}
        pin = lambda co, top=top: abs(co.x) > 0.06 and co.z > top[1 if co.x > 0 else -1] - 0.02
        out["shirt"].append(_simulate(ob, pin, 70, scene, wind, yaw))
        bpy.data.objects.remove(ob)
    # a bed sheet thrown over the pole: starts flat across it, pinned along the fold
    for i, (wind, yaw) in enumerate(((3.0, 0.0), (10.0, 1.2))):
        me = _sheet_mesh(1.5, 2.1, 30, 42)
        ob = _new_obj(f"sheet_over{i}", me, scene)
        out["sheet_over"].append(_simulate(ob, lambda co: abs(co.y) < 0.03, 90, scene, wind, yaw, mass=0.35, bend=0.2, gather=0.78 + 0.06 * i))
        bpy.data.objects.remove(ob)
    # a sheet hung by four pegs along its top edge, sagging between them
    for i, (wind, yaw) in enumerate(((4.0, 0.2), (12.0, -0.5))):
        me = _sheet_mesh(1.5, 1.9, 30, 38)
        for v in me.vertices: v.co.z, v.co.y = v.co.y - 0.95, 0.0            # hang it vertical, top edge at z = 0
        ob = _new_obj(f"sheet_peg{i}", me, scene)
        pegs = (-0.74, -0.25, 0.25, 0.74)
        pin = lambda co: co.z > -0.02 and any(abs(co.x - p) < 0.04 for p in pegs)
        out["sheet_pegged"].append(_simulate(ob, pin, 90, scene, wind, yaw, mass=0.35, bend=0.2, self_collide=False, gather=0.86))
        bpy.data.objects.remove(ob)
    me = _sheet_mesh(0.5, 0.95, 12, 24)
    ob = _new_obj("towel", me, scene)
    out["towel"].append(_simulate(ob, lambda co: abs(co.y) < 0.03, 70, scene, 5.0, 0.6, mass=0.25, bend=0.3, gather=0.85))
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(base)
    log("laundry simulated:", {k: len(v) for k, v in out.items()})
    return out


# ---------------------------------------------------------------- fabric materials
def _img(name, non_color=False):
    im = bpy.data.images.load(_need(os.path.join(TEX, name)), check_existing=True)
    if non_color: im.colorspace_settings.name = "Non-Color"
    return im


def _fabric(name, tex, color=None, uv=True, scale=1.0, hue=0.5, translucent=0.3):
    """Cotton: Poly Haven weave (normal + roughness), sheen, light through thin cloth."""
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    N = m.node_tree.nodes; L = m.node_tree.links
    bsdf = N["Principled BSDF"]; out = N["Material Output"]
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["UV" if uv else "Object"], mp.inputs["Vector"])
    def im(file, nc=False):
        t = N.new("ShaderNodeTexImage"); t.image = _img(file, nc)
        if not uv: t.projection = "BOX"; t.projection_blend = 0.3
        L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    col = im(f"{tex}_diff.jpg").outputs["Color"]
    hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Hue"].default_value = hue
    hs.inputs["Saturation"].default_value = 0.8; hs.inputs["Value"].default_value = 0.9
    L.new(col, hs.inputs["Color"]); col = hs.outputs["Color"]
    if color:                                     # dyed plain cotton: weave luminance times the dye
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
        mx.inputs["Factor"].default_value = 1.0
        bw = N.new("ShaderNodeRGBToBW"); L.new(col, bw.inputs["Color"])
        ramp = N.new("ShaderNodeMapRange"); ramp.inputs["From Min"].default_value = 0.2; ramp.inputs["To Min"].default_value = 0.75
        L.new(bw.outputs["Val"], ramp.inputs["Value"])
        cc = N.new("ShaderNodeCombineColor")
        for ch in ("Red", "Green", "Blue"): L.new(ramp.outputs["Result"], cc.inputs[ch])
        L.new(cc.outputs["Color"], _sock(mx.inputs, "A_Color")); _sock(mx.inputs, "B_Color").default_value = (*color, 1)
        col = _sock(mx.outputs, "Result_Color")
    L.new(col, bsdf.inputs["Base Color"])
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.5
    L.new(im(f"{tex}_nor.jpg", True).outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    L.new(im(f"{tex}_rough.jpg", True).outputs["Color"], bsdf.inputs["Roughness"])
    bsdf.inputs["Sheen Weight"].default_value = 0.6
    bsdf.inputs["Sheen Roughness"].default_value = 0.5
    # thin cotton lets daylight through: mix in a translucent lobe of the same colour
    tr = N.new("ShaderNodeBsdfTranslucent"); L.new(col, tr.inputs["Color"]); L.new(nm.outputs["Normal"], tr.inputs["Normal"])
    mix = N.new("ShaderNodeMixShader"); mix.inputs["Fac"].default_value = translucent
    L.new(bsdf.outputs["BSDF"], mix.inputs[1]); L.new(tr.outputs["BSDF"], mix.inputs[2])
    L.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


# sun-faded laundry colours of the Walled City: whites, reds, navies, mint, mustard, pinks
SHIRT_DYES = [(0.78, 0.78, 0.75), (0.72, 0.73, 0.74), (0.5, 0.12, 0.1), (0.08, 0.11, 0.22), (0.3, 0.45, 0.62),
              (0.38, 0.56, 0.46), (0.66, 0.5, 0.14), (0.72, 0.42, 0.48), (0.3, 0.3, 0.31), (0.04, 0.04, 0.045),
              (0.72, 0.3, 0.1), (0.55, 0.62, 0.7)]


def fabric_materials():
    shirts = [_fabric(f"shirt_{i}", "cotton_jersey", c, uv=False, scale=6.0) for i, c in enumerate(SHIRT_DYES)]
    sheets = [
        _fabric("sheet_gingham_blue", "gingham_check", scale=3.0, hue=0.5),
        _fabric("sheet_gingham_red", "gingham_check", scale=3.0, hue=0.0),
        _fabric("sheet_gingham_green", "gingham_check", scale=3.0, hue=0.33),
        _fabric("sheet_floral", "floral_jacquard", scale=2.0),
        _fabric("sheet_pattern05", "fabric_pattern_05", scale=2.5),
        _fabric("sheet_pattern07", "fabric_pattern_07", scale=2.5),
        _fabric("sheet_pattern07_rose", "fabric_pattern_07", scale=2.5, hue=0.9),
    ]
    return shirts, sheets


# ---------------------------------------------------------------- potted plants
def _pot_material():
    """One pot material, coloured per instance: terracotta, plastic basins, glazed ceramic."""
    m = bpy.data.materials.new("pot")
    try: m.use_nodes = True
    except Exception: pass
    N = m.node_tree.nodes; L = m.node_tree.links; bsdf = N["Principled BSDF"]
    info = N.new("ShaderNodeObjectInfo")
    ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    cols = [(0.42, 0.17, 0.08), (0.16, 0.3, 0.18), (0.46, 0.06, 0.05), (0.7, 0.69, 0.64), (0.12, 0.2, 0.34), (0.34, 0.14, 0.07)]
    els = ramp.color_ramp.elements
    els[0].position = 0.0; els[0].color = (*cols[0], 1)
    els[1].position = 1 / len(cols); els[1].color = (*cols[1], 1)
    for i, c in enumerate(cols[2:], 2):
        e = els.new(i / len(cols)); e.color = (*c, 1)
    L.new(info.outputs["Random"], ramp.inputs["Fac"])
    # grime and rain streaks, as everything else up there
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14.0; nz.inputs["Detail"].default_value = 8.0
    dirt = N.new("ShaderNodeMapRange"); dirt.inputs["From Min"].default_value = 0.4; dirt.inputs["From Max"].default_value = 0.75
    dirt.inputs["To Min"].default_value = 1.0; dirt.inputs["To Max"].default_value = 0.55
    L.new(nz.outputs["Fac"], dirt.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
    L.new(ramp.outputs["Color"], _sock(mx.inputs, "A_Color"))
    cc = N.new("ShaderNodeCombineColor")
    for ch in ("Red", "Green", "Blue"): L.new(dirt.outputs["Result"], cc.inputs[ch])
    L.new(cc.outputs["Color"], _sock(mx.inputs, "B_Color"))
    L.new(_sock(mx.outputs, "Result_Color"), bsdf.inputs["Base Color"])
    # glazed pots are glossy, terracotta and old plastic are not
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.75; rr.inputs["To Max"].default_value = 0.2
    L.new(info.outputs["Random"], rr.inputs["Value"]); L.new(rr.outputs["Result"], bsdf.inputs["Roughness"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.2
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def plant_collections():
    """Each plant (leaves untouched, pot re-materialed) as a collection to instance, origin at the pot's base."""
    pot = _pot_material()
    out = []
    for folder, blend in (("banjo", "PlantBanjoFig001_Blender_Cycles.blend"), ("zz", "PlantZZ001_Blender_Cycles.blend")):
        path = _need(os.path.join(ASSETS, folder, blend))
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = [n for n in src.objects]
        meshes = [o for o in dst.objects if o and o.type == "MESH"]
        col = bpy.data.collections.new(f"plant_{folder}")
        dg = None
        for o in meshes:
            col.objects.link(o)
            mw = o.matrix_world.copy()
            o.parent = None; o.matrix_world = mw
            if "Vase" in o.name:
                o.data.materials.clear(); o.data.materials.append(pot)
        for o in dst.objects:
            if o and o.type != "MESH": bpy.data.objects.remove(o)
        zmin = min((o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box)
        xs = [(o.matrix_world @ Vector(c)) for o in meshes for c in o.bound_box]
        cx = (min(p.x for p in xs) + max(p.x for p in xs)) / 2; cy = (min(p.y for p in xs) + max(p.y for p in xs)) / 2
        col.instance_offset = (cx, cy, zmin)
        h = max(p.z for p in xs) - zmin
        out.append((col, h))
    # appended images keep paths relative to the source .blend: make them absolute
    for im in bpy.data.images:
        if im.filepath.startswith("//"):
            for folder in ("banjo", "zz"):
                cand = os.path.join(ASSETS, folder, os.path.basename(im.filepath))
                if os.path.exists(cand): im.filepath = cand; break
    log("plants:", [(c.name, round(h, 2)) for c, h in out])
    return out


def place_plant(scene, col, loc, yaw, scale):
    e = bpy.data.objects.new(col.name, None)
    e.instance_type = "COLLECTION"; e.instance_collection = col
    e.location = loc; e.rotation_euler = (0, 0, yaw); e.scale = (scale, scale, scale)
    scene.collection.objects.link(e)
    return e


def place_cloth(scene, me, mat, loc, x_axis, scale, sway=0.0):
    """One piece of laundry sharing `me`; local X along `x_axis`, hung from its origin."""
    ob = bpy.data.objects.new("laundry", me)
    if not me.materials: me.materials.append(mat)
    ob.material_slots[0].link = "OBJECT"; ob.material_slots[0].material = mat
    x = Vector(x_axis).normalized()
    ob.location = loc
    ob.rotation_euler = (0, sway, math.atan2(x.y, x.x))
    ob.scale = (scale, scale, scale)
    scene.collection.objects.link(ob)
    return ob
