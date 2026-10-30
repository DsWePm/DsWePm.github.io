"""
Photoreal "urban canyon" for the hero, rendered offline with Cycles.

A white concrete slab with an irregular crack; below it, two rows of dense
Kowloon-Walled-City-style facades (cages, AC units, pipes, cable bundles,
cloth-simulated laundry, potted plants) form a deep canyon that ends in a
dark alley. The slab break shows
fractured concrete and two layers of rebar mesh.

  node tools/blender/fetch_textures.mjs          # once; also unpack the model zips (see props.py)
  blender -b --factory-startup -P tools/blender/build_city.py -- [--seed 7] [--preview-samples 48]

Writes tools/blender/out/city.blend (input for render_hero.py) and two
review renders: tools/blender/out/preview_top.jpg, preview_inside.jpg.
"""
import bpy, bmesh, math, random, os, sys, time
import numpy as np
from mathutils import Vector, geometry
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import props

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default, cast=str):
    return cast(argv[argv.index(name) + 1]) if name in argv else default
SEED = arg("--seed", 7, int)
PREVIEW_SAMPLES = arg("--preview-samples", 48, int)
NO_PREVIEW = "--no-preview" in argv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TMP = os.path.join(ROOT, "tools", "blender", "out")
TEX = os.path.join(ROOT, "tools", "blender", "textures")
os.makedirs(TMP, exist_ok=True)

# ---------------------------------------------------------------- dimensions (metres, Z up)
GW, GH = 40.0, 24.0          # slab size
T = 0.5                      # slab thickness
FLOOR_H = 2.8
FLOORS = 22
D = T + FLOORS * FLOOR_H     # canyon depth
X0, X1 = -12.0, 12.0         # crack extent
STEP = 0.05

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
rng = random.Random(SEED)
np_rng = np.random.default_rng(SEED)
t_start = time.time()
def log(*a): print(f"[city {time.time() - t_start:6.1f}s]", *a, flush=True)

# laundry is simulated first, on the empty scene
LAUNDRY = props.laundry_meshes(bpy.context.scene)
SHIRT_MATS, SHEET_MATS = props.fabric_materials()
PLANTS = props.plant_collections()
log("props ready")

# ---------------------------------------------------------------- crack outline
def value_noise_1d(freq, amp, r):
    n = int((X1 - X0) * freq) + 3
    vals = [r.uniform(-1, 1) for _ in range(n)]
    def f(x):
        t = (x - X0) * freq
        i = int(math.floor(t)); fr = t - i
        fr = fr * fr * (3 - 2 * fr)
        return amp * (vals[i] * (1 - fr) + vals[i + 1] * fr)
    return f

def center_y(x):
    return 0.9 * math.sin(0.23 * x + 0.4) + 0.45 * math.sin(0.61 * x + 2.1) + 0.2 * math.sin(1.3 * x)

def half_width(x):
    # exponent > 1 tapers the ends into sharp, acute points
    t = max(0.0, 1 - (x / X1) ** 2)
    return 2.6 * t ** 1.2 * (0.72 + 0.38 * (0.5 + 0.5 * math.sin(0.5 * x + 1.0)))

jag = {s: [value_noise_1d(f, a, rng) for f, a in ((3, 0.20), (9, 0.08), (26, 0.035))] for s in (1, -1)}
def edge_y(x, side, jagged=True):
    w = half_width(x)
    j = 0.0
    if jagged:
        j = sum(n(x) for n in jag[side]) * min(1.0, w / 0.4)
        j = max(j, -0.6 * w)
    return center_y(x) + side * (w + j)

xs = [X0 + i * STEP for i in range(int((X1 - X0) / STEP) + 1)]
north = [(x, edge_y(x, 1)) for x in xs]
south = [(x, edge_y(x, -1)) for x in xs]
hole = south + list(reversed(north[1:-1]))
edge_all = [(p, 1) for p in north[5:-5]] + [(p, -1) for p in south[5:-5]]

def inside_hole(x, y):
    c = False
    n = len(hole)
    for i in range(n):
        ax, ay = hole[i]; bx, by = hole[(i + 1) % n]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            c = not c
    return c

# ---------------------------------------------------------------- mesh building
class Builder:
    """Collects polygons into one bmesh with per-face material and a metric 'facade' UV."""
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("facade")

    def poly(self, pts, normal, mat, uvs):
        pts = [Vector(p) for p in pts]
        n = (pts[1] - pts[0]).cross(pts[2] - pts[0])
        if n.dot(Vector(normal)) < 0:
            pts.reverse(); uvs = list(reversed(uvs))
        f = self.bm.faces.new([self.bm.verts.new(p) for p in pts])
        f.material_index = mat
        for loop, uv in zip(f.loops, uvs): loop[self.uv].uv = uv
        return f
    quad = poly

    def finish(self, materials, smooth=False):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=0.0005)
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me); self.bm.free()
        for m in materials: me.materials.append(m)
        if smooth:
            for p in me.polygons: p.use_smooth = True
        ob = bpy.data.objects.new(self.name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob

def tube(b, pts, r, mat, sides=6):
    """Round tube along a polyline (pipes, cables, rebar, poles)."""
    pts = [Vector(p) for p in pts]
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(a).normalized(); v = t.cross(u)
        rings.append([p + (u * math.cos(2 * math.pi * k / sides) + v * math.sin(2 * math.pi * k / sides)) * r for k in range(sides)])
    L = 0.0
    circ = 2 * math.pi * r
    for i in range(len(pts) - 1):
        seg = (pts[i + 1] - pts[i]).length
        for k in range(sides):
            k2 = (k + 1) % sides
            c = (rings[i][k] + rings[i][k2]) / 2 - pts[i]
            b.poly([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]], c, mat,
                   [(circ * k / sides, L), (circ * (k + 1) / sides, L), (circ * (k + 1) / sides, L + seg), (circ * k / sides, L + seg)])
        L += seg

class Frame:
    """Local frame on a facade: u along the wall, n out into the canyon, z up."""
    def __init__(self, origin, U, N, uv_off=(0, 0)):
        self.O, self.U, self.N, self.Z = Vector(origin), Vector(U), Vector(N), Vector((0, 0, 1))
        self.off = uv_off
    def p(self, u, n, z): return self.O + self.U * u + self.N * n + self.Z * z

    def box(self, b, mat, u0, u1, n0, n1, z0, z1, back=False):
        P = self.p; o = self.off; U, N, Z = self.U, self.N, self.Z
        b.poly([P(u0, n1, z0), P(u1, n1, z0), P(u1, n1, z1), P(u0, n1, z1)], N, mat,
               [(o[0] + u0, o[1] + z0), (o[0] + u1, o[1] + z0), (o[0] + u1, o[1] + z1), (o[0] + u0, o[1] + z1)])
        if back:
            b.poly([P(u0, n0, z0), P(u1, n0, z0), P(u1, n0, z1), P(u0, n0, z1)], -N, mat, [(u0, z0), (u1, z0), (u1, z1), (u0, z1)])
        for u, s in ((u0, -1), (u1, 1)):
            b.poly([P(u, n0, z0), P(u, n1, z0), P(u, n1, z1), P(u, n0, z1)], U * s, mat,
                   [(o[0] + n0, o[1] + z0), (o[0] + n1, o[1] + z0), (o[0] + n1, o[1] + z1), (o[0] + n0, o[1] + z1)])
        for z, s in ((z0, -1), (z1, 1)):
            b.poly([P(u0, n0, z), P(u1, n0, z), P(u1, n1, z), P(u0, n1, z)], Z * s, mat,
                   [(o[0] + u0, o[1] + n0), (o[0] + u1, o[1] + n0), (o[0] + u1, o[1] + n1), (o[0] + u0, o[1] + n1)])

    def wall(self, b, mat, u0, u1, z0, z1, n=0.0):
        o = self.off; P = self.p
        b.poly([P(u0, n, z0), P(u1, n, z0), P(u1, n, z1), P(u0, n, z1)], self.N, mat,
               [(o[0] + u0, o[1] + z0), (o[0] + u1, o[1] + z0), (o[0] + u1, o[1] + z1), (o[0] + u0, o[1] + z1)])

    def face(self, b, mat, pts_local, normal, uvs):
        b.poly([self.p(*q) for q in pts_local], normal, mat, uvs)

# material slots on the City mesh
(M_WALL_GREY, M_WALL_BEIGE, M_WALL_GREEN, M_WALL_TILE, M_WALL_CONC, M_DARK, M_METAL, M_FRAME,
 M_GLASS, M_GLASS_LIT, M_CABLE, M_PVC, M_CLOTH_A, M_CLOTH_B, M_CLOTH_C, M_JUNK, M_TUBE_LIGHT, M_ALLEY,
 M_TIN, M_ENAMEL, M_SHEET, M_AC, M_WALL_BLUE, M_WALL_PINK,
 M_LIT_TUNGSTEN, M_LIT_COOL, M_LIT_GREEN, M_LIT_ROSE, M_LIT_RED) = range(29)
# M_METAL = painted, rusting iron; M_FRAME = aluminium; M_PVC = dirty plastic pipe
WALLS = [M_WALL_GREY, M_WALL_BEIGE, M_WALL_GREEN, M_WALL_TILE, M_WALL_CONC, M_WALL_BLUE, M_WALL_PINK]
# window light by what is behind it: bare bulbs, tubes, curtains of every colour (weights)
LIGHTS = [(M_GLASS_LIT, 3), (M_LIT_TUNGSTEN, 4), (M_LIT_COOL, 5), (M_LIT_GREEN, 3), (M_LIT_ROSE, 2), (M_LIT_RED, 1)]
CLOTHS = [M_CLOTH_A, M_CLOTH_B, M_CLOTH_C]

city = Builder("City")

# ---------------------------------------------------------------- facade elements
def window(fr, u0, u1, z0, z1, cell, wall_mat, r):
    cu0, cu1, cz0, cz1 = cell
    o = fr.off
    fr.wall(city, wall_mat, cu0, u0, cz0, cz1)
    fr.wall(city, wall_mat, u1, cu1, cz0, cz1)
    fr.wall(city, wall_mat, u0, u1, cz0, z0)
    fr.wall(city, wall_mat, u0, u1, z1, cz1)
    for (pts, nrm) in (([(u0, 0, z0), (u0, -r, z0), (u0, -r, z1), (u0, 0, z1)], fr.U),
                       ([(u1, 0, z0), (u1, -r, z0), (u1, -r, z1), (u1, 0, z1)], -fr.U),
                       ([(u0, 0, z0), (u1, 0, z0), (u1, -r, z0), (u0, -r, z0)], fr.Z),
                       ([(u0, 0, z1), (u1, 0, z1), (u1, -r, z1), (u0, -r, z1)], -fr.Z)):
        fr.face(city, wall_mat, pts, nrm, [(o[0] + q[0] + q[1], o[1] + q[2]) for q in pts])
    depth_k = min(1.0, max(0.0, -z0 / D))           # interiors read brighter where the canyon is darker
    lit = rng.random() < 0.07 + 0.2 * depth_k
    glass = rng.choices([m for m, _ in LIGHTS], [w for _, w in LIGHTS])[0] if lit else M_GLASS
    fr.face(city, glass, [(u0, -r, z0), (u1, -r, z0), (u1, -r, z1), (u0, -r, z1)], fr.N,
            [(0, 0), (1, 0), (1, 1), (0, 1)])
    # aluminium frame and mullions
    a = 0.035
    for uu in (u0 + a, (u0 + u1) / 2, u1 - a):
        fr.box(city, M_FRAME, uu - a / 2, uu + a / 2, -r, -r + 0.04, z0, z1)
    zt = z1 - (z1 - z0) * 0.3
    fr.box(city, M_FRAME, u0, u1, -r, -r + 0.04, zt - a / 2, zt + a / 2)
    fr.box(city, M_DARK, u0 - 0.05, u1 + 0.05, 0, 0.06, z0 - 0.06, z0)
    # half-drawn curtain behind some panes
    if rng.random() < 0.4:
        cw = (u1 - u0) * rng.uniform(0.3, 0.6)
        side = rng.random() < 0.5
        cu = (u0, u0 + cw) if side else (u1 - cw, u1)
        fr.face(city, rng.choice(CLOTHS), [(cu[0], -r - 0.05, z0), (cu[1], -r - 0.05, z0), (cu[1], -r - 0.05, z1), (cu[0], -r - 0.05, z1)],
                fr.N, [(0, 0), (1, 0), (1, 1), (0, 1)])

def cage(fr, u0, u1, z0, z1, depth, unit_u):
    """Welded iron cage over a window, the signature of the Walled City. Returns its extents."""
    a = 0.014
    bz0, bz1 = z0 - rng.uniform(0.15, 0.6), z1 + rng.uniform(0.1, 0.3)
    ua = max(unit_u[0] + 0.03, u0 - rng.uniform(0.05, 0.3)); ub = min(unit_u[1] - 0.03, u1 + rng.uniform(0.05, 0.3))
    fr.box(city, M_METAL, ua, ub, 0, depth, bz0 - 0.04, bz0)
    fr.box(city, M_TIN, ua - 0.05, ub + 0.05, 0, depth + 0.08, bz1, bz1 + 0.025)         # corrugated tin canopy
    n = max(4, int((ub - ua) / 0.11))
    for i in range(n + 1):
        u = ua + (ub - ua) * i / n
        fr.box(city, M_METAL, u - a, u + a, depth - 2 * a, depth, bz0, bz1)
    for k in range(max(2, int(depth / 0.12))):
        nn = depth * (k + 1) / (max(2, int(depth / 0.12)) + 1)
        for u in (ua, ub):
            fr.box(city, M_METAL, u - a, u + a, nn - a, nn + a, bz0, bz1)
    for z in (bz0 + 0.06, (bz0 + bz1) / 2, bz1 - 0.08):
        fr.box(city, M_METAL, ua, ub, depth - 3 * a, depth - a, z - a, z + a)
    # potted plants on the cage floor, then whatever else people keep out there
    slots = []
    if depth > 0.3 and rng.random() < 0.55:
        for _ in range(rng.randint(1, 3)):
            col, h = rng.choice(PLANTS)
            s = rng.uniform(0.55, 1.0) * min(1.0, (bz1 - bz0 - 0.15) / h, (depth - 0.05) / 0.5)
            uu = rng.uniform(ua + 0.2, max(ua + 0.21, ub - 0.2))
            if any(abs(uu - q) < 0.35 for q in slots): continue
            slots.append(uu)
            props.place_plant(bpy.context.scene, col, fr.p(uu, rng.uniform(0.12, max(0.13, depth - 0.2)), bz0), rng.uniform(0, 6.3), s)
    for _ in range(rng.randint(0, 3)):
        w = rng.uniform(0.15, 0.45); h = rng.uniform(0.1, 0.5); dd = rng.uniform(0.1, min(0.35, depth - 0.05))
        uu = rng.uniform(ua + 0.05, max(ua + 0.06, ub - w - 0.05))
        if any(uu - 0.25 < q < uu + w + 0.25 for q in slots): continue
        fr.box(city, rng.choice([M_JUNK, M_PVC]), uu, uu + w, 0.02, 0.02 + dd, bz0, bz0 + h)
    if rng.random() < 0.3:   # a plastic sheet tied over part of the cage
        sw = (ub - ua) * rng.uniform(0.3, 0.8)
        fr.face(city, M_SHEET, [(ua, depth + 0.005, bz0 + 0.3), (ua + sw, depth + 0.005, bz0 + 0.3), (ua + sw, depth + 0.005, bz1), (ua, depth + 0.005, bz1)],
                fr.N, [(0, 0), (sw, 0), (sw, 1), (0, 1)])
    if rng.random() < 0.35 and ub - ua > 0.5:   # shirts hung off the cage front
        for _ in range(rng.randint(1, 3)):
            hang_shirt(fr.p(rng.uniform(ua + 0.2, ub - 0.2), depth + 0.04, bz1 - 0.04), fr.U)
    return ua, ub, bz0, bz1

def ac_unit(fr, uc, ztop, w, h, d):
    """Window-type AC box on two brackets: casing with grille, drain hose."""
    fr.box(city, M_AC, uc - w / 2, uc + w / 2, 0.03, d, ztop - h, ztop)
    for s in (-1, 1):
        fr.box(city, M_METAL, uc + s * (w / 2 - 0.06) - 0.015, uc + s * (w / 2 - 0.06) + 0.015, 0, d * 0.95, ztop - h - 0.1, ztop - h)
    p0 = fr.p(uc + w * 0.3, d * 0.5, ztop - h)
    tube(city, [p0, p0 + Vector((0, 0, -rng.uniform(0.3, 1.5)))], 0.008, M_CABLE, 4)

def place_ac(fr, u0, u1, wu0, wu1, wz0, wz1, cage_ext):
    """An AC where it fits without cutting into the window, the cage or the unit next door."""
    w, h, d = rng.uniform(0.6, 0.85), rng.uniform(0.4, 0.55), rng.uniform(0.35, 0.55)
    lo, hi = (cage_ext[0], cage_ext[1]) if cage_ext else (wu0 - 0.06, wu1 + 0.06)
    spots = []
    if lo - (u0 + 0.05) > w + 0.05: spots.append(((u0 + lo) / 2, (wz0 + wz1) / 2 + h / 2))       # beside, left
    if (u1 - 0.05) - hi > w + 0.05: spots.append(((hi + u1) / 2, (wz0 + wz1) / 2 + h / 2))       # beside, right
    if not cage_ext and wu1 - wu0 > w + 0.1: spots.append(((wu0 + wu1) / 2, wz0 - 0.1))           # under the sill
    if spots:
        uc, zt = rng.choice(spots)
        ac_unit(fr, uc, zt, w, h, d)
        fr.busy.append((uc - w / 2 - 0.03, uc + w / 2 + 0.03))

def hang_shirt(at, along):
    """One shirt on a hanger at `at`, the hanger across `along`."""
    props.place_cloth(bpy.context.scene, rng.choice(LAUNDRY["shirt"]), rng.choice(SHIRT_MATS), at, along,
                      rng.uniform(0.62, 1.15), rng.uniform(-0.06, 0.06))

def laundry(fr, u, z):
    """A pole out from the window with shirts on hangers, or a sheet or towel over it."""
    L = rng.uniform(1.0, 1.7)
    p0 = fr.p(u, 0.05, z)
    p1 = p0 + fr.N * L + Vector((0, 0, rng.uniform(0.05, 0.3)))
    tube(city, [p0, p1], 0.012, M_FRAME, 6)
    sc = bpy.context.scene
    up = Vector((0, 0, 0.012))
    r = rng.random()
    if r < 0.25:          # a bed sheet thrown over the pole
        props.place_cloth(sc, rng.choice(LAUNDRY["sheet_over"]), rng.choice(SHEET_MATS), p0.lerp(p1, rng.uniform(0.45, 0.6)) + up,
                          fr.N, rng.uniform(0.85, 1.0) * min(1.0, L / 1.55))
    elif r < 0.4:         # pegged along the pole
        props.place_cloth(sc, rng.choice(LAUNDRY["sheet_pegged"]), rng.choice(SHEET_MATS), p0.lerp(p1, 0.55),
                          fr.N, min(1.0, L / 1.6) * rng.uniform(0.8, 1.0))
    else:
        n = rng.randint(1, 4)
        for k in range(n):
            c = p0.lerp(p1, (k + 0.6) / (n + 0.4)) + up
            if rng.random() < 0.2:
                props.place_cloth(sc, LAUNDRY["towel"][0], rng.choice(SHEET_MATS + SHIRT_MATS), c, fr.N, rng.uniform(0.8, 1.1))
            else:
                hang_shirt(c, fr.U)

def facade_cables(fr, L):
    """Cable bundles clipped along the wall, sagging between brackets, plus vertical drops."""
    for _ in range(rng.randint(2, 5)):
        z = -T - rng.uniform(0.4, D - 3)
        anchors = [0.0]
        while anchors[-1] < L:
            anchors.append(min(L, anchors[-1] + rng.uniform(1.4, 3.0)))
        for w in range(rng.randint(1, 4)):
            n = 0.05 + w * 0.03 + rng.uniform(0, 0.03)
            pts = []
            for a, b in zip(anchors, anchors[1:]):
                sag = rng.uniform(0.04, 0.25)
                for k in range(6):
                    t = k / 6
                    pts.append(fr.p(a + (b - a) * t, n, z - w * 0.025 - sag * 4 * t * (1 - t)))
            pts.append(fr.p(anchors[-1], n, z - w * 0.025))
            tube(city, pts, rng.uniform(0.006, 0.014), M_CABLE, 5)
        for a in anchors[1:-1]:
            fr.box(city, M_METAL, a - 0.02, a + 0.02, 0, 0.12, z - 0.03, z + 0.03)
    for _ in range(rng.randint(1, 4)):
        u = rng.uniform(0.2, L - 0.2)
        z0 = -T - rng.uniform(0, D * 0.4); z1 = z0 - rng.uniform(3, 14)
        pts = [fr.p(u + 0.04 * math.sin(k * 1.7), 0.06, z0 + (z1 - z0) * k / 10) for k in range(11)]
        tube(city, pts, 0.01, M_CABLE, 5)

def free_u(fr, L, tries=8):
    """A spot along the wall clear of AC units and cages (fr.busy)."""
    for _ in range(tries):
        u = rng.uniform(0.15, L - 0.15)
        if not any(a - 0.06 < u < b + 0.06 for a, b in fr.busy): return u
    return None

def pipes(fr, L):
    for _ in range(rng.randint(2, 6)):
        u = free_u(fr, L)
        if u is None: continue
        r = rng.uniform(0.03, 0.075)
        mat = rng.choice([M_PVC, M_PVC, M_METAL])
        z_top = -T - rng.uniform(0, 4)
        tube(city, [fr.p(u, 0.06 + r, z_top), fr.p(u, 0.06 + r, -D)], r, mat, 8)
        z = z_top
        while z > -D:
            fr.box(city, M_METAL, u - r - 0.02, u + r + 0.02, 0, 0.06 + 2 * r, z - 0.03, z)
            z -= FLOOR_H
        if rng.random() < 0.5:   # dog-leg to a neighbour
            zj = -T - rng.uniform(2, D - 4)
            u2 = min(L - 0.1, max(0.1, u + rng.uniform(-1.5, 1.5)))
            if any(min(u, u2) - 0.1 < b and a < max(u, u2) + 0.1 for a, b in fr.busy): continue
            tube(city, [fr.p(u, 0.06 + r, zj), fr.p(u2, 0.06 + r, zj), fr.p(u2, 0.06 + r, zj - 2.5)], r * 0.7, mat, 8)

def unit(fr, u0, u1, zb, zt, base_mat, prm):
    mat = base_mat if rng.random() > prm["patch"] else rng.choice(WALLS)
    w = u1 - u0
    ww = min(w - 0.35, rng.uniform(0.7, 1.5))
    wh = rng.uniform(1.0, 1.5)
    sill = rng.uniform(0.75, 1.0)
    uc = (u0 + u1) / 2 + rng.uniform(-1, 1) * max(0, (w - ww) / 2 - 0.2)
    wu0, wu1 = uc - ww / 2, uc + ww / 2
    wz0 = zb + sill; wz1 = min(zt - 0.25, wz0 + wh)
    window(fr, wu0, wu1, wz0, wz1, (u0, u1, zb, zt), mat, rng.uniform(0.1, 0.2))
    ext = None
    if rng.random() < prm["cage"]:
        ext = cage(fr, wu0, wu1, wz0, wz1, rng.uniform(0.25, 0.75), (u0, u1))
        fr.busy.append((ext[0], ext[1]))
    elif rng.random() < 0.35:
        fr.box(city, M_METAL, wu0 - 0.04, wu1 + 0.04, 0, 0.05, wz1 + 0.02, wz1 + 0.05)
    if rng.random() < prm["ac"]:
        place_ac(fr, u0, u1, wu0, wu1, wz0, wz1, ext)
    if not ext and rng.random() < prm["laundry"]:
        laundry(fr, rng.uniform(wu0, wu1), wz1 - 0.1)

def building(fr, L):
    base = rng.choice(WALLS)
    prm = {"cage": rng.uniform(0.35, 0.75), "ac": rng.uniform(0.3, 0.55), "patch": rng.uniform(0.15, 0.45), "laundry": rng.uniform(0.2, 0.45)}
    fr.busy = []
    for f in range(FLOORS):
        zt = -T - f * FLOOR_H; zb = zt - FLOOR_H
        u = 0.0
        while u < L - 0.05:
            w = rng.uniform(1.3, 2.6)
            if L - (u + w) < 0.9: w = L - u
            unit(fr, u, u + w, zb, zt, base, prm)
            u += w
        if rng.random() < 0.3:
            fr.box(city, M_DARK, 0, L, 0, 0.05, zb - 0.06, zb + 0.06)
    pipes(fr, L)
    facade_cables(fr, L)
    if rng.random() < 0.6:   # vertical shop sign
        u = rng.uniform(0.3, L - 0.3)
        zt = -T - rng.randint(2, FLOORS - 4) * FLOOR_H
        fr.box(city, M_ENAMEL, u - 0.06, u + 0.06, 0.2, rng.uniform(1.0, 1.7), zt - rng.uniform(2.5, 5), zt, back=True)
    # a rare fluorescent tube a few floors up; the bottom itself stays unlit
    if rng.random() < 0.25:
        u = rng.uniform(0.3, L - 0.8)
        z = -D + rng.uniform(9.0, 16.0)
        tube(city, [fr.p(u, 0.08, z), fr.p(u + 0.6, 0.08, z)], 0.016, M_TUBE_LIGHT, 6)

# ---------------------------------------------------------------- facades along both edges
def segments():
    out, x = [], X0
    while x < X1 - 0.5:
        xb = min(X1, x + rng.uniform(3.0, 6.5))
        if X1 - xb < 2.0: xb = X1
        out.append((x, xb)); x = xb
    return out

facade_lines = {}
for side in (1, -1):
    lines = []
    for (xa, xb) in segments():
        pts = [(x, edge_y(x, side)) for x in xs if xa - 1e-6 <= x <= xb + 1e-6]
        slope = (edge_y(xb, side, False) - edge_y(xa, side, False)) / (xb - xa)
        a = (max if side == 1 else min)(y - slope * x for x, y in pts) + side * 0.15
        lines.append((xa, xb, a, slope))
    facade_lines[side] = lines

for side, lines in facade_lines.items():
    for k, (xa, xb, a, slope) in enumerate(lines):
        pa = Vector((xa, a + slope * xa, 0)); pb = Vector((xb, a + slope * xb, 0))
        U = (pb - pa).normalized()
        N = Vector((U.y, -U.x, 0)) if side == 1 else Vector((-U.y, U.x, 0))
        building(Frame(pa, U, N, (rng.uniform(0, 50), rng.uniform(0, 50))), (pb - pa).length)
        if k + 1 < len(lines):
            _, _, an, sn = lines[k + 1]
            y_this, y_next = a + slope * xb, an + sn * xb
            normal = Vector((1, 0, 0)) if side * y_this < side * y_next else Vector((-1, 0, 0))
            y0, y1 = sorted((y_this, y_next))
            city.poly([(xb, y0, -D), (xb, y1, -D), (xb, y1, -T), (xb, y0, -T)], normal, M_WALL_CONC,
                      [(y0, -D), (y1, -D), (y1, -T), (y0, -T)])
for x, nx in ((X0, 1), (X1, -1)):
    ln = facade_lines[1][0 if nx == 1 else -1]; ls = facade_lines[-1][0 if nx == 1 else -1]
    y_n = ln[2] + ln[3] * x; y_s = ls[2] + ls[3] * x
    city.poly([(x, y_s, -D), (x, y_n, -D), (x, y_n, -T), (x, y_s, -T)], (nx, 0, 0), M_WALL_CONC,
              [(y_s, -D), (y_n, -D), (y_n, -T), (y_s, -T)])

# alley floor: rendered as a holdout in the fall, so the page shows through it at impact
city.poly([(X0 - 1, -8, -D), (X1 + 1, -8, -D), (X1 + 1, 8, -D), (X0 - 1, 8, -D)], (0, 0, 1), M_ALLEY,
          [(X0 - 1, -8), (X1 + 1, -8), (X1 + 1, 8), (X0 - 1, 8)])
log("city faces:", len(city.bm.faces))

# ---------------------------------------------------------------- slab: top, fractured break, underside, rebar
slab = Builder("Slab")
M_SLAB_TOP, M_FRACTURE, M_REBAR = range(3)

def ring_normals(poly):
    """Unit vectors pointing from the slab into the hole at each outline vertex."""
    n = len(poly); out = []
    for i in range(n):
        ax, ay = poly[i - 1]; bx, by = poly[(i + 1) % n]
        t = Vector((bx - ax, by - ay, 0)).normalized()
        nv = Vector((-t.y, t.x, 0))
        px, py = poly[i]
        if not inside_hole(px + nv.x * 0.02, py + nv.y * 0.02): nv = -nv
        out.append(nv)
    return out

def build_slab():
    outer = [Vector((-GW / 2, -GH / 2, 0)), Vector((GW / 2, -GH / 2, 0)), Vector((GW / 2, GH / 2, 0)), Vector((-GW / 2, GH / 2, 0))]
    inner = [Vector((x, y, 0)) for x, y in hole]
    tris = geometry.tessellate_polygon([[v.copy() for v in outer], [v.copy() for v in inner]])
    allv = outer + inner
    uvg = lambda v: (v.x, v.y)
    for a, b, c in tris:
        for z, up in ((0.0, True), (-T, False)):
            pts = [Vector((allv[i].x, allv[i].y, z)) for i in (a, b, c)]
            slab.poly(pts, (0, 0, 1 if up else -1), M_SLAB_TOP if up else M_FRACTURE, [uvg(p) for p in pts])
    # fracture: several displaced rows between top and bottom, chipped toward the hole
    nrm = ring_normals(hole)
    rows = 5
    ring_rows = []
    for r in range(rows + 1):
        t = r / rows
        z = -T * t
        row = []
        for (x, y), nv in zip(hole, nrm):
            jitter = 0.0 if r in (0, rows) else rng.uniform(-0.06, 0.08)
            row.append(Vector((x, y, z)) + nv * (jitter - 0.04 * math.sin(t * math.pi)))
        ring_rows.append(row)
    n = len(hole)
    for r in range(rows):
        for i in range(n):
            j = (i + 1) % n
            pts = [ring_rows[r][i], ring_rows[r][j], ring_rows[r + 1][j], ring_rows[r + 1][i]]
            slab.poly(pts, nrm[i], M_FRACTURE, [(p.x + p.y, p.z) for p in pts])
    log("slab faces:", len(slab.bm.faces))

def rebar():
    """Two layers of reinforcement mesh; bars that cross the break stick out and droop."""
    spacing = 0.2
    count = 0
    xs_min, xs_max = X0 - 0.5, X1 + 0.5
    ys_min = min(y for _, y in hole) - 0.5; ys_max = max(y for _, y in hole) + 0.5
    for z in (-0.11, -0.38):
        for axis in (0, 1):
            lines = np.arange(xs_min if axis == 0 else ys_min, (xs_max if axis == 0 else ys_max), spacing)
            for c in lines:
                c = float(c) + rng.uniform(-0.01, 0.01)
                # intersections of the grid line with the outline
                hits = []
                for i in range(len(hole)):
                    (ax, ay), (bx, by) = hole[i], hole[(i + 1) % len(hole)]
                    a0, b0 = (ax, bx) if axis == 0 else (ay, by)
                    if (a0 - c) * (b0 - c) < 0:
                        t = (c - a0) / (b0 - a0)
                        hits.append(ay + t * (by - ay) if axis == 0 else ax + t * (bx - ax))
                for h in hits:
                    if rng.random() < 0.7: continue           # most bars snapped flush with the break
                    # direction along the line that points into the hole
                    for s in (1, -1):
                        px, py = (c, h + s * 0.03) if axis == 0 else (h + s * 0.03, c)
                        if inside_hole(px, py): break
                    d = Vector((0, s, 0)) if axis == 0 else Vector((s, 0, 0))
                    start = Vector((c, h, z)) if axis == 0 else Vector((h, c, z))
                    start -= d * 0.12                          # emerges from inside the concrete
                    L = rng.uniform(0.05, 0.45) * (1.6 if rng.random() < 0.1 else 1.0)
                    droop = rng.uniform(0.2, 1.2)
                    side = Vector((-d.y, d.x, 0)) * rng.uniform(-0.25, 0.25)
                    pts = []
                    for k in range(7):
                        t = k / 6
                        ang = droop * t * t
                        pts.append(start + d * (0.12 + L * t) * math.cos(ang * 0.6) + side * L * t * t
                                   - Vector((0, 0, L * math.sin(ang) * t)))
                    tube(slab, pts, rng.uniform(0.006, 0.009), M_REBAR, 6)
                    count += 1
    log("rebar bars:", count)

def chunks():
    for _ in range(45):
        (x, y), side = rng.choice(edge_all)
        s = rng.uniform(0.015, 0.08)
        bm2 = bmesh.new()
        bmesh.ops.create_icosphere(bm2, subdivisions=2, radius=1.0)
        c = Vector((x + rng.uniform(-0.1, 0.1), y + side * rng.uniform(0.05, 0.7), s * 0.25))
        for v in bm2.verts:
            nz = 1 + 0.35 * math.sin(v.co.x * 5 + v.co.y * 3) * math.cos(v.co.z * 4)
            v.co = Vector((v.co.x * s * rng.uniform(0.8, 1.2), v.co.y * s * rng.uniform(0.8, 1.2), v.co.z * s * 0.45)) * nz + c
        bm2.normal_update()
        for f in bm2.faces:
            pts = [v.co.copy() for v in f.verts]
            slab.poly(pts, f.normal, M_FRACTURE, [(p.x * 3, p.y * 3) for p in pts])
        bm2.free()

build_slab(); rebar(); chunks()

# ---------------------------------------------------------------- ground detail texture (hairlines, stains, edge distance)
def upsample(grid, H, W):
    gh, gw = grid.shape
    ys = np.linspace(0, gh - 1, H); xs_ = np.linspace(0, gw - 1, W)
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs_).astype(int)
    y1 = np.minimum(y0 + 1, gh - 1); x1 = np.minimum(x0 + 1, gw - 1)
    fy = (ys - y0)[:, None]; fx = (xs_ - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = grid[y0][:, x0]; b = grid[y0][:, x1]; c = grid[y1][:, x0]; d = grid[y1][:, x1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def ground_texture():
    W = 4096; H = int(round(W * GH / GW)); ppm = W / GW
    st = np.zeros((H, W), np.float32)
    for k, amp in ((6, 0.5), (14, 0.25), (40, 0.15), (120, 0.1)):
        st += amp * upsample(np_rng.random((int(k * GH / GW) + 2, k + 2)).astype(np.float32), H, W)
    st = np.clip((st - st.min()) / (st.max() - st.min()), 0, 1)
    w4, h4 = W // 4, H // 4
    PX, PY = np.meshgrid((np.arange(w4) + 0.5) / w4 * GW - GW / 2, (np.arange(h4) + 0.5) / h4 * GH - GH / 2)
    poly = np.array(hole, np.float32); A = poly; B = np.roll(poly, -1, axis=0)
    dist = np.full(PX.shape, 1e9, np.float32)
    for (ax, ay), (bx, by) in zip(A, B):
        dx, dy = bx - ax, by - ay
        t = np.clip(((PX - ax) * dx + (PY - ay) * dy) / (dx * dx + dy * dy + 1e-12), 0, 1)
        np.minimum(dist, (ax + t * dx - PX) ** 2 + (ay + t * dy - PY) ** 2, out=dist)
    dist = upsample(np.sqrt(dist), H, W)
    hair = np.zeros((H, W), np.float32)
    kern = {r: np.clip(1.0 - np.sqrt(np.add.outer(np.arange(-r, r + 1) ** 2, np.arange(-r, r + 1) ** 2)) / (r + 0.5), 0, 1).astype(np.float32) for r in (1, 2)}
    def stamp(x, y, r, s):
        cx, cy = int((x + GW / 2) * ppm), int((y + GH / 2) * ppm)
        if cx - r < 0 or cy - r < 0 or cx + r >= W or cy + r >= H: return
        sl = hair[cy - r:cy + r + 1, cx - r:cx + r + 1]; np.maximum(sl, kern[r] * s, out=sl)
    def walk(x, y, ang, length, width, depth=0):
        n = int(length / 0.03); heading = ang
        for i in range(n):
            t = i / max(1, n)
            if rng.random() < 0.05: ang = heading + rng.uniform(-0.7, 0.7)
            ang += rng.gauss(0, 0.04)
            x += math.cos(ang) * 0.03; y += math.sin(ang) * 0.03
            stamp(x, y, 2 if width * (1 - t) > 1.8 else 1, 0.75 * (1 - 0.7 * t))
            if depth < 2 and rng.random() < 0.008:
                walk(x, y, ang + rng.choice((-1, 1)) * rng.uniform(0.5, 1.1), length * (1 - t) * 0.6, width * 0.6, depth + 1)
    for _ in range(26):
        (x, y), side = rng.choice(edge_all)
        walk(x, y, math.atan2(side, 0) + rng.uniform(-0.9, 0.9), rng.uniform(0.6, 4.5), rng.uniform(1.5, 3.2))
    for tip, ang in (((X0, center_y(X0)), math.pi), ((X1, center_y(X1)), 0.0)):
        for _ in range(3): walk(tip[0], tip[1], ang + rng.uniform(-0.5, 0.5), rng.uniform(2.5, 5.5), 3.0)
    img = bpy.data.images.new("ground_tex", W, H, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    rgba = np.ones((H, W, 4), np.float32)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = hair, st, np.clip(dist / 3.0, 0, 1)
    img.pixels.foreach_set(rgba.ravel()); img.pack()
    log("ground texture")
    return img
gtex = ground_texture()

# ---------------------------------------------------------------- materials
def sock(sockets, ident):
    for s in sockets:
        if s.identifier == ident: return s
    raise KeyError(ident)

def new_mat(name):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    return m

_img = {}
def tex_image(name, non_color=False):
    if (name, non_color) not in _img:
        path = os.path.join(TEX, name)
        if not os.path.exists(path): raise SystemExit(f"missing {path}: run `node tools/blender/fetch_textures.mjs`")
        im = bpy.data.images.load(path, check_existing=True)
        if non_color: im.colorspace_settings.name = "Non-Color"
        _img[(name, non_color)] = im
    return _img[(name, non_color)]

class NB:
    """Tiny node-building helper."""
    def __init__(self, m):
        self.m = m; self.N = m.node_tree.nodes; self.L = m.node_tree.links; self.bsdf = self.N["Principled BSDF"]
    def n(self, kind, **inputs):
        node = self.N.new(kind)
        for k, v in inputs.items():
            if k.startswith("_"): setattr(node, k[1:], v)
            else: node.inputs[k].default_value = v
        return node
    def link(self, a, b): self.L.new(a, b)
    def mix(self, a, b, fac=1.0, mode="MIX"):
        mx = self.n("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = mode
        if isinstance(fac, (int, float)): sock(mx.inputs, "Factor_Float").default_value = fac
        else: self.link(fac, sock(mx.inputs, "Factor_Float"))
        for ident, v in (("A_Color", a), ("B_Color", b)):
            if isinstance(v, tuple): sock(mx.inputs, ident).default_value = v
            else: self.link(v, sock(mx.inputs, ident))
        return sock(mx.outputs, "Result_Color")
    def coords(self, kind):
        if kind == "facade":
            u = self.n("ShaderNodeUVMap"); u.uv_map = "facade"; return u.outputs["UV"]
        return self.n("ShaderNodeTexCoord").outputs["Object"]
    def mapped(self, vec, size, rot=0.0):
        mp = self.n("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1 / size, 1 / size, 1 / size); mp.inputs["Rotation"].default_value = (0, 0, rot)
        self.link(vec, mp.inputs["Vector"]); return mp.outputs["Vector"]
    def img(self, file, vec, non_color=False, box=False):
        t = self.n("ShaderNodeTexImage"); t.image = tex_image(file, non_color); t.interpolation = "Cubic"
        if box: t.projection = "BOX"; t.projection_blend = 0.3
        self.link(vec, t.inputs["Vector"]); return t.outputs["Color"]
    def noise(self, vec, scale, detail=6.0):
        nz = self.n("ShaderNodeTexNoise", Scale=scale, Detail=detail); self.link(vec, nz.inputs["Vector"]); return nz.outputs["Fac"]
    def ramp(self, val, a, b, lo=0.0, hi=1.0):
        mr = self.n("ShaderNodeMapRange", **{"From Min": a, "From Max": b, "To Min": lo, "To Max": hi}); self.link(val, mr.inputs["Value"]); return mr.outputs["Result"]
    def hsv(self, col, sat, val):
        h = self.n("ShaderNodeHueSaturation", Saturation=sat, Value=val); self.link(col, h.inputs["Color"]); return h.outputs["Color"]
    def gray3(self, f):
        cc = self.n("ShaderNodeCombineColor")
        for c in ("Red", "Green", "Blue"): self.link(f, cc.inputs[c])
        return cc.outputs["Color"]
    def normal_map(self, col, strength=1.0, uv="facade"):
        nm = self.n("ShaderNodeNormalMap", Strength=strength); nm.uv_map = uv; self.link(col, nm.inputs["Color"]); return nm.outputs["Normal"]

def photo(name, asset, size, tint=(1, 1, 1), sat=0.4, val=1.0, dirt=0.35, streak=0.35, coords="facade", box=False, rough=1.0, nstr=1.0, contrast=0.0):
    """Poly Haven set in metres, desaturated, with grime and rain streaks (the Walled City is filthy)."""
    m = new_mat(name); b = NB(m)
    vec = b.coords(coords); v = b.mapped(vec, size)
    col = b.img(f"{asset}_diff.jpg", v, box=box)
    if dirt > 0:
        g = b.img("concrete_wall_003_diff.jpg", b.mapped(vec, 5.0, 0.7), box=box)
        g = b.hsv(g, 0.15, 0.75)
        mask = b.ramp(b.noise(vec, 0.3), 0.48, 0.62, 0.0, dirt)
        col = b.mix(col, g, mask, "MULTIPLY")
    col = b.mix(b.hsv(col, sat, val), (*tint, 1), 1.0, "MULTIPLY")
    if contrast:
        bc = b.n("ShaderNodeBrightContrast", Contrast=contrast); b.link(col, bc.inputs["Color"]); col = bc.outputs["Color"]
    if streak > 0:
        mp = b.n("ShaderNodeMapping", Scale=(10.0, 0.25, 1.0)); b.link(vec, mp.inputs["Vector"])
        s = b.ramp(b.noise(mp.outputs["Vector"], 1.0, 4.0), 0.4, 0.8, 1.0 - streak, 1.0)
        col = b.mix(col, b.gray3(s), 1.0, "MULTIPLY")
    b.link(col, b.bsdf.inputs["Base Color"])
    if box:
        bump = b.n("ShaderNodeBump", Strength=0.35 * nstr, Distance=0.01)
        b.link(b.img(f"{asset}_rough.jpg", v, True, box), bump.inputs["Height"]); b.link(bump.outputs["Normal"], b.bsdf.inputs["Normal"])
    else:
        b.link(b.normal_map(b.img(f"{asset}_nor.jpg", v, True), nstr), b.bsdf.inputs["Normal"])
    r = b.n("ShaderNodeMath", _operation="MULTIPLY", _use_clamp=True); r.inputs[1].default_value = rough
    b.link(b.img(f"{asset}_rough.jpg", v, True, box), r.inputs[0]); b.link(r.outputs[0], b.bsdf.inputs["Roughness"])
    return m

def flat(name, color, rough=0.6, metal=0.0, emit=None, strength=0.0):
    m = new_mat(name); bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1); bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1); bsdf.inputs["Emission Strength"].default_value = strength
    return m

def cloth(name, color):
    m = flat(name, color, rough=0.9)
    b = NB(m)
    s = b.ramp(b.noise(b.coords("facade"), 8.0, 3.0), 0.3, 0.7, 0.75, 1.0)
    b.link(b.mix((*color, 1), b.gray3(s), 1.0, "MULTIPLY"), b.bsdf.inputs["Base Color"])
    b.bsdf.inputs["Sheen Weight"].default_value = 0.4
    return m

def rust_mask(b, vec, scale=2.5, lo=0.5, hi=0.62):
    return b.ramp(b.noise(vec, scale, 10.0), lo, hi, 0.0, 1.0)

def grime(b, vec, col, amount=0.35):
    """Darken with blotchy dirt plus rain streaks running down (facade UV: x along wall, y up)."""
    g = b.ramp(b.noise(vec, 1.2, 6.0), 0.35, 0.7, 1.0 - amount, 1.0)
    mp = b.n("ShaderNodeMapping", Scale=(14.0, 0.3, 1.0)); b.link(vec, mp.inputs["Vector"])
    s = b.ramp(b.noise(mp.outputs["Vector"], 1.0, 3.0), 0.45, 0.8, 1.0 - amount * 0.8, 1.0)
    col = b.mix(col, b.gray3(g), 1.0, "MULTIPLY")
    return b.mix(col, b.gray3(s), 1.0, "MULTIPLY")

def painted_iron():
    """Welded cage bars and brackets: faded teal paint flaking off to orange rust."""
    m = new_mat("painted_iron"); b = NB(m)
    vec = b.coords("facade")
    rust = b.hsv(b.img("rusty_metal_02_diff.jpg", b.mapped(vec, 0.5)), 0.6, 0.85)
    paint = (0.2, 0.31, 0.3, 1)
    mask = rust_mask(b, vec, 3.0, 0.47, 0.57)
    col = grime(b, vec, b.mix(paint, rust, mask), 0.3)
    b.link(col, b.bsdf.inputs["Base Color"])
    b.link(b.ramp(mask, 0, 1, 0.42, 0.85), b.bsdf.inputs["Roughness"])
    b.link(b.ramp(mask, 0, 1, 0.15, 0.35), b.bsdf.inputs["Metallic"])
    return m

def aluminium():
    m = new_mat("aluminium"); b = NB(m)
    vec = b.coords("facade")
    col = grime(b, vec, (0.62, 0.64, 0.65, 1), 0.4)
    b.link(col, b.bsdf.inputs["Base Color"])
    b.bsdf.inputs["Metallic"].default_value = 0.9
    b.link(b.ramp(b.noise(vec, 4.0, 6.0), 0.3, 0.7, 0.3, 0.6), b.bsdf.inputs["Roughness"])
    return m

def dirty_plastic():
    """Drain pipes: off-white PVC gone yellow-grey, satin, streaked with grime."""
    m = new_mat("pvc"); b = NB(m)
    vec = b.coords("facade")
    col = grime(b, vec, (0.66, 0.65, 0.6, 1), 0.45)
    b.link(col, b.bsdf.inputs["Base Color"])
    b.link(b.ramp(b.noise(vec, 3.0, 4.0), 0.3, 0.7, 0.32, 0.55), b.bsdf.inputs["Roughness"])
    b.bsdf.inputs["Coat Weight"].default_value = 0.15
    return m

def enamel():
    """AC casings and sign boxes: baked enamel, chipped and rust-streaked."""
    m = new_mat("enamel"); b = NB(m)
    vec = b.coords("facade")
    rust = b.hsv(b.img("rusty_metal_02_diff.jpg", b.mapped(vec, 0.6)), 0.5, 0.8)
    mask = rust_mask(b, vec, 5.0, 0.6, 0.66)
    col = grime(b, vec, b.mix((0.74, 0.74, 0.7, 1), rust, mask), 0.4)
    b.link(col, b.bsdf.inputs["Base Color"])
    b.link(b.ramp(mask, 0, 1, 0.3, 0.8), b.bsdf.inputs["Roughness"])
    return m

def corrugated_tin():
    """Cage roofs: corrugated galvanised sheet, heavily rusted."""
    m = new_mat("tin"); b = NB(m)
    vec = b.coords("facade")
    wave = b.n("ShaderNodeTexWave", Scale=1.0, Distortion=0.0)
    wave.wave_type = "BANDS"; wave.bands_direction = "X"; wave.wave_profile = "SIN"
    mp = b.n("ShaderNodeMapping", Scale=(1 / 0.076, 1 / 0.076, 1)); b.link(vec, mp.inputs["Vector"])
    b.link(mp.outputs["Vector"], wave.inputs["Vector"])
    rust = b.hsv(b.img("rusty_metal_02_diff.jpg", b.mapped(vec, 0.8)), 0.55, 0.8)
    mask = rust_mask(b, vec, 2.0, 0.42, 0.58)
    col = grime(b, vec, b.mix((0.48, 0.5, 0.51, 1), rust, mask), 0.35)
    b.link(col, b.bsdf.inputs["Base Color"])
    b.link(b.ramp(mask, 0, 1, 0.4, 0.9), b.bsdf.inputs["Roughness"])
    b.link(b.ramp(mask, 0, 1, 0.75, 0.1), b.bsdf.inputs["Metallic"])
    bump = b.n("ShaderNodeBump", Strength=0.9, Distance=0.02)
    b.link(wave.outputs["Fac"], bump.inputs["Height"]); b.link(bump.outputs["Normal"], b.bsdf.inputs["Normal"])
    return m

def plastic_sheet():
    m = new_mat("plastic_sheet"); b = NB(m)
    vec = b.coords("facade")
    b.link(grime(b, vec, (0.72, 0.74, 0.72, 1), 0.4), b.bsdf.inputs["Base Color"])
    b.bsdf.inputs["Roughness"].default_value = 0.45
    b.bsdf.inputs["Transmission Weight"].default_value = 0.5
    return m

def ac_casing():
    """AC units: powder-coated steel gone yellow-grey, a louvred grille, rust running from the brackets."""
    m = new_mat("ac_casing"); b = NB(m)
    vec = b.coords("facade")
    louvre = b.n("ShaderNodeTexWave", Scale=1.0, Distortion=0.0)
    louvre.wave_type = "BANDS"; louvre.bands_direction = "Y"; louvre.wave_profile = "SAW"
    mp = b.n("ShaderNodeMapping", Scale=(1 / 0.018, 1 / 0.018, 1)); b.link(vec, mp.inputs["Vector"])
    b.link(mp.outputs["Vector"], louvre.inputs["Vector"])
    rust = b.hsv(b.img("rusty_metal_02_diff.jpg", b.mapped(vec, 0.4)), 0.7, 0.7)
    mask = rust_mask(b, vec, 7.0, 0.62, 0.7)
    base = b.mix((0.66, 0.64, 0.57, 1), (0.52, 0.5, 0.44, 1), b.noise(vec, 3.0, 4.0))
    col = grime(b, vec, b.mix(base, rust, mask), 0.55)
    col = b.mix(col, b.gray3(b.ramp(louvre.outputs["Fac"], 0.0, 1.0, 0.55, 1.0)), 1.0, "MULTIPLY")   # dark gaps
    b.link(col, b.bsdf.inputs["Base Color"])
    b.link(b.ramp(mask, 0, 1, 0.38, 0.85), b.bsdf.inputs["Roughness"])
    b.link(b.ramp(mask, 0, 1, 0.35, 0.1), b.bsdf.inputs["Metallic"])
    bump = b.n("ShaderNodeBump", Strength=0.7, Distance=0.006)
    b.link(louvre.outputs["Fac"], bump.inputs["Height"]); b.link(bump.outputs["Normal"], b.bsdf.inputs["Normal"])
    return m

def alley():
    m = photo("alley", "concrete_floor_02", 2.0, tint=(0.3, 0.31, 0.32), sat=0.1, val=0.4, dirt=0.6, streak=0.0)
    b = NB(m)
    wet = b.ramp(b.noise(b.coords("facade"), 0.6, 4.0), 0.45, 0.6, 0.6, 0.05)   # puddles
    b.link(wet, b.bsdf.inputs["Roughness"])
    return m

# walls: darker and more contrasty than the cages and laundry in front of them, deep relief,
# faded pastel paint over filthy concrete
WALL = dict(dirt=0.55, streak=0.5, nstr=2.6, contrast=0.22)
city_mats = [
    photo("wall_grey", "painted_plaster_wall", 2.0, sat=0.25, val=0.72, **WALL),
    photo("wall_beige", "painted_plaster_wall", 2.0, tint=(1.0, 0.86, 0.68), sat=0.55, val=0.74, **WALL),
    photo("wall_green", "painted_plaster_wall", 2.0, tint=(0.7, 0.9, 0.78), sat=0.55, val=0.7, **WALL),
    photo("wall_tile", "floor_tiles_02", 1.2, tint=(0.95, 0.96, 1.0), sat=0.25, val=0.82, dirt=0.45, streak=0.5, nstr=2.0, contrast=0.2),
    photo("wall_concrete", "concrete_wall_003", 3.0, sat=0.2, val=0.68, **WALL),
    photo("dark", "concrete_wall_003", 3.0, tint=(0.75, 0.77, 0.79), sat=0.12, val=0.75),
    painted_iron(),
    aluminium(),
    flat("glass", (0.02, 0.022, 0.025), rough=0.04, metal=0.0),
    flat("glass_lit", (0.05, 0.05, 0.05), rough=0.1, emit=(1.0, 0.8, 0.58), strength=1.6),
    flat("cable", (0.018, 0.019, 0.02), rough=0.45),
    dirty_plastic(),
    cloth("cloth_a", (0.42, 0.45, 0.48)),
    cloth("cloth_b", (0.62, 0.58, 0.5)),
    cloth("cloth_c", (0.48, 0.36, 0.33)),
    photo("junk", "rusty_metal_02", 0.6, tint=(0.7, 0.68, 0.64), sat=0.3, val=0.85, dirt=0.3),
    flat("tube_light", (0.9, 0.95, 1.0), rough=0.3, emit=(0.86, 0.94, 1.0), strength=9.0),
    alley(),
    corrugated_tin(),
    enamel(),
    plastic_sheet(),
    ac_casing(),
    photo("wall_blue", "painted_plaster_wall", 2.0, tint=(0.62, 0.8, 0.95), sat=0.55, val=0.72, **WALL),
    photo("wall_pink", "painted_plaster_wall", 2.0, tint=(0.95, 0.7, 0.68), sat=0.55, val=0.72, **WALL),
    # lit windows: tungsten bulbs, cool and green-tinged tubes, light through rose and red curtains
    flat("lit_tungsten", (0.05, 0.05, 0.05), rough=0.1, emit=(1.0, 0.52, 0.2), strength=1.5),
    flat("lit_cool", (0.05, 0.05, 0.05), rough=0.1, emit=(0.7, 0.86, 1.0), strength=1.6),
    flat("lit_green", (0.05, 0.05, 0.05), rough=0.1, emit=(0.5, 1.0, 0.62), strength=1.4),
    flat("lit_rose", (0.05, 0.05, 0.05), rough=0.1, emit=(1.0, 0.45, 0.52), strength=1.3),
    flat("lit_red", (0.05, 0.05, 0.05), rough=0.1, emit=(1.0, 0.22, 0.12), strength=1.2),
]

def slab_top():
    """White painted concrete; near the break the paint has spalled off to raw concrete."""
    m = new_mat("slab_top"); b = NB(m)
    obj = b.coords("object")
    uvn = b.n("ShaderNodeUVMap"); uvn.uv_map = "facade"
    # ground_tex is laid out over the slab in metres: u = (x + GW/2) / GW
    mp = b.n("ShaderNodeMapping", Location=(GW / 2, GH / 2, 0), Scale=(1, 1, 1))
    b.link(uvn.outputs["UV"], mp.inputs["Vector"])
    mp2 = b.n("ShaderNodeMapping", Scale=(1 / GW, 1 / GH, 1)); b.link(mp.outputs["Vector"], mp2.inputs["Vector"])
    gt = b.n("ShaderNodeTexImage"); gt.image = gtex; b.link(mp2.outputs["Vector"], gt.inputs["Vector"])
    sep = b.n("ShaderNodeSeparateColor"); b.link(gt.outputs["Color"], sep.inputs["Color"])
    paint = b.hsv(b.img("painted_plaster_wall_diff.jpg", b.mapped(obj, 2.5)), 0.05, 1.6)
    raw = b.hsv(b.img("concrete_floor_02_diff.jpg", b.mapped(obj, 1.5)), 0.1, 0.85)
    spall = b.ramp(sep.outputs["Blue"], 0.008, 0.04, 1.0, 0.0)
    spall_n = b.ramp(b.noise(obj, 6.0, 10.0), 0.47, 0.53, 0.0, 1.0)   # crisp chipped-paint boundary
    sp = b.n("ShaderNodeMath", _operation="MULTIPLY", _use_clamp=True); b.link(spall, sp.inputs[0]); b.link(spall_n, sp.inputs[1])
    sp2 = b.n("ShaderNodeMath", _operation="MULTIPLY", _use_clamp=True); sp2.inputs[1].default_value = 2.0; b.link(sp.outputs[0], sp2.inputs[0])
    col = b.mix(paint, raw, sp2.outputs[0])
    col = b.mix(col, b.gray3(b.ramp(sep.outputs["Green"], 0, 1, 1.0, 0.9)), 1.0, "MULTIPLY")      # stains
    col = b.mix(col, b.gray3(b.ramp(sep.outputs["Red"], 0, 1, 1.0, 0.25)), 1.0, "MULTIPLY")       # hairlines
    b.link(col, b.bsdf.inputs["Base Color"])
    b.link(b.ramp(sep.outputs["Green"], 0.3, 0.8, 0.55, 0.18), b.bsdf.inputs["Roughness"])        # wet patches
    bump = b.n("ShaderNodeBump", Strength=0.5, Distance=0.004, _invert=True)
    b.link(sep.outputs["Red"], bump.inputs["Height"])
    nmap = b.n("ShaderNodeNormalMap", Strength=0.4); nmap.uv_map = "facade"
    b.link(b.img("concrete_floor_02_nor.jpg", b.mapped(uvn.outputs["UV"], 1.5), True), nmap.inputs["Color"])
    b.link(nmap.outputs["Normal"], bump.inputs["Normal"]); b.link(bump.outputs["Normal"], b.bsdf.inputs["Normal"])
    return m

slab_mats = [
    slab_top(),
    photo("fracture", "concrete_floor_02", 0.5, tint=(0.82, 0.82, 0.8), sat=0.15, val=0.95, dirt=0.25, streak=0.0, coords="object", box=True, nstr=3.0),
    photo("rebar", "rusty_metal_02", 0.25, tint=(0.55, 0.48, 0.42), sat=0.4, val=0.45, dirt=0.0, streak=0.0, rough=0.9),
]

ob_city = city.finish(city_mats)
ob_slab = slab.finish(slab_mats)
ob_slab.pass_index = 1       # render_hero.py builds the slab mask from this
log("meshes built")

# ---------------------------------------------------------------- world and render settings
scene = bpy.context.scene
scene.render.engine = "CYCLES"
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
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 5
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
try: scene.view_settings.look = "AgX - Base Contrast"
except Exception: pass

world = bpy.data.worlds.new("overcast"); scene.world = world
try: world.use_nodes = True
except Exception: pass
wn = world.node_tree.nodes; wl = world.node_tree.links
env = wn.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(os.path.join(TEX, "overcast_soil_puresky.hdr"), check_existing=True)
wl.new(env.outputs["Color"], wn["Background"].inputs["Color"])
wn["Background"].inputs["Strength"].default_value = 2.0
sun_data = bpy.data.lights.new("sun", "SUN")
sun_data.energy = 2.6; sun_data.angle = math.radians(22); sun_data.color = (1.0, 0.985, 0.96)
sun = bpy.data.objects.new("sun", sun_data)
sun.rotation_euler = (math.radians(26), 0, math.radians(200))
scene.collection.objects.link(sun)

cam_data = bpy.data.cameras.new("hero_cam")
cam_data.sensor_fit = "VERTICAL"; cam_data.angle_y = math.radians(40); cam_data.clip_start = 0.05; cam_data.clip_end = 300
cam = bpy.data.objects.new("hero_cam", cam_data); cam.location = (0, 0, 18)
scene.collection.objects.link(cam); scene.camera = cam

# metadata for render_hero.py
scene["city_depth"] = D
scene["city_slab"] = T
widest = max(((x, edge_y(x, 1, False) - edge_y(x, -1, False)) for x in xs if abs(x) < 6), key=lambda p: p[1])[0]
scene["dive_x"] = widest
scene["dive_y"] = center_y(widest)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(TMP, "city.blend"), compress=True)
log("saved city.blend")

if not NO_PREVIEW:
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    scene.cycles.samples = PREVIEW_SAMPLES
    scene.render.image_settings.file_format = "JPEG"
    scene.render.filepath = os.path.join(TMP, "preview_top.jpg")
    bpy.ops.render.render(write_still=True)
    cam.location = (widest - 3.0, center_y(widest - 3.0), -9)
    cam.rotation_euler = (math.radians(62), 0, math.radians(-90))
    cam_data.angle_y = math.radians(55)
    scene.render.filepath = os.path.join(TMP, "preview_inside.jpg")
    bpy.ops.render.render(write_still=True)
    log("previews rendered")
