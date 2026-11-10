"""Fisher Game environment - shared helpers.

Blender z = 0 is sea level (Unity y = 0, the WaterManagement object's height).
Waves from WaterManagement.GetWaveHeight stay within +/- amplitude (default 1 m),
so everything walkable near the water sits at DOCK_DECK_Z or higher.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler, noise
from mathutils.bvhtree import BVHTree

SEA_LEVEL = 0.0
DOCK_DECK_Z = 1.8
SCENE_NAME = "FisherWorld"
# vertex budget knobs (raise for more detail)
TERRAIN_CELL_SCALE = 1.6     # multiplies every island's terrain cell size
SCATTER_DENSITY = 0.4        # multiplies every scatter() count (trees, bushes, rocks)


# ---------------------------------------------------------------- scene / collections

def scene():
    sc = bpy.data.scenes.get(SCENE_NAME)
    if sc is None:
        sc = bpy.data.scenes.new(SCENE_NAME)
    return sc


def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    par = parent or scene().collection
    if c.name not in par.children:
        par.children.link(c)
    return c


def clear_coll(c):
    """Remove every object (and its now unused mesh) inside c and its children."""
    for child in list(c.children):
        clear_coll(child)
        bpy.data.collections.remove(child)
    for o in list(c.objects):
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Light):
                bpy.data.lights.remove(data)


def island_setup(coll_name, prefix, center):
    """Root collection + sub-collections + root empty for one island (rebuilt from scratch)."""
    root_c = coll(coll_name)
    clear_coll(root_c)
    subs = {k: coll("%s_%s" % (prefix, k), root_c) for k in
            ("Terrain", "Buildings", "Dock", "Props", "Vegetation", "Lights", "NPCs")}
    root = bpy.data.objects.new("%s_Island_Root" % prefix, None)
    root.empty_display_type = 'CUBE'
    root.empty_display_size = 3
    root.location = (center[0], center[1], 0)
    root_c.objects.link(root)
    bpy.context.view_layer.update()
    return root_c, subs, root


def place_many(prefix, meshes, pts, c, parent, seed=0, scale=(0.8, 1.25), sink=0.15):
    rnd = random.Random(seed)
    out = []
    for i, (x, y, z) in enumerate(pts):
        me = meshes[rnd.randrange(len(meshes))] if isinstance(meshes, list) else meshes
        s = rnd.uniform(*scale)
        o = bpy.data.objects.new("%s_%02d" % (prefix, i + 1), me)
        o.location = (x, y, z - sink * s)
        o.rotation_euler = (0, 0, rnd.uniform(0, 2 * math.pi))
        o.scale = (s, s, s)
        out.append(link(o, c, parent))
    return out


def link(o, c, parent=None):
    c.objects.link(o)
    if parent is not None:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


def empty(name, loc, c, parent=None, kind='PLAIN_AXES', size=2.0):
    o = bpy.data.objects.new(name, None)
    o.empty_display_type = kind
    o.empty_display_size = size
    o.location = loc
    link(o, c, parent)
    bpy.context.view_layer.update()
    return o


# ---------------------------------------------------------------- materials

def srgb(c):
    return tuple(x ** 2.2 for x in c)


def mat(name, color, rough=0.7, metal=0.0, emit=None, emit_strength=0.0, alpha=1.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    lin = srgb(color)
    b.inputs["Base Color"].default_value = (*lin, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*srgb(emit), 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    b.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    m.diffuse_color = (*lin, alpha)
    return m


def palette():
    """One shared, slightly desaturated palette for the whole world."""
    P = {}
    P["sand"] = mat("M_Sand", (0.90, 0.80, 0.60), 0.9)
    P["sand_wet"] = mat("M_SandWet", (0.66, 0.56, 0.40), 0.8)
    P["sand_dark"] = mat("M_SandDark", (0.58, 0.52, 0.44), 0.9)
    P["seabed"] = mat("M_Seabed", (0.40, 0.46, 0.40), 0.9)
    P["grass"] = mat("M_Grass", (0.42, 0.62, 0.26), 0.9)
    P["grass_dry"] = mat("M_GrassDry", (0.62, 0.64, 0.32), 0.9)
    P["grass_dark"] = mat("M_GrassDark", (0.25, 0.42, 0.20), 0.9)
    P["rock"] = mat("M_Rock", (0.50, 0.49, 0.47), 0.85)
    P["rock_warm"] = mat("M_RockWarm", (0.66, 0.54, 0.40), 0.85)
    P["rock_dark"] = mat("M_RockDark", (0.33, 0.33, 0.34), 0.85)
    P["wood"] = mat("M_Wood", (0.55, 0.38, 0.23), 0.8)
    P["wood_dark"] = mat("M_WoodDark", (0.33, 0.23, 0.15), 0.8)
    P["wood_light"] = mat("M_WoodLight", (0.76, 0.62, 0.44), 0.8)
    P["wood_grey"] = mat("M_WoodWeathered", (0.56, 0.53, 0.48), 0.9)
    P["white"] = mat("M_PaintWhite", (0.93, 0.93, 0.90), 0.5)
    P["red"] = mat("M_PaintRed", (0.72, 0.16, 0.12), 0.5)
    P["blue"] = mat("M_PaintBlue", (0.18, 0.36, 0.58), 0.5)
    P["navy"] = mat("M_PaintNavy", (0.13, 0.18, 0.30), 0.5)
    P["teal"] = mat("M_PaintTeal", (0.30, 0.64, 0.66), 0.5)
    P["yellow"] = mat("M_PaintYellow", (0.95, 0.74, 0.20), 0.5)
    P["green_paint"] = mat("M_PaintGreen", (0.26, 0.45, 0.32), 0.5)
    P["roof_red"] = mat("M_RoofRed", (0.62, 0.24, 0.18), 0.8)
    P["roof_dark"] = mat("M_RoofSlate", (0.24, 0.26, 0.30), 0.8)
    P["thatch"] = mat("M_Thatch", (0.72, 0.60, 0.38), 0.95)
    P["metal"] = mat("M_Metal", (0.70, 0.71, 0.72), 0.35, metal=1.0)
    P["metal_dark"] = mat("M_MetalDark", (0.22, 0.23, 0.24), 0.45, metal=0.8)
    P["concrete"] = mat("M_Concrete", (0.70, 0.69, 0.66), 0.85)
    P["glass"] = mat("M_Glass", (0.60, 0.78, 0.85), 0.05, alpha=0.35)
    P["window_lit"] = mat("M_WindowWarm", (0.95, 0.80, 0.50), 0.4, emit=(1.0, 0.78, 0.45), emit_strength=2.0)
    P["rope"] = mat("M_Rope", (0.78, 0.68, 0.48), 0.95)
    P["black"] = mat("M_Rubber", (0.06, 0.06, 0.06), 0.8)
    P["leaf"] = mat("M_PalmLeaf", (0.30, 0.55, 0.20), 0.8)
    P["pine"] = mat("M_PineNeedles", (0.18, 0.36, 0.22), 0.9)
    P["bush"] = mat("M_Bush", (0.30, 0.50, 0.22), 0.9)
    P["fabric_white"] = mat("M_FabricWhite", (0.95, 0.94, 0.90), 0.9)
    P["fabric_blue"] = mat("M_FabricBlue", (0.25, 0.50, 0.75), 0.9)
    P["fabric_orange"] = mat("M_FabricOrange", (0.95, 0.50, 0.15), 0.9)
    P["fish"] = mat("M_Fish", (0.60, 0.68, 0.74), 0.3, metal=0.3)
    P["ice"] = mat("M_Ice", (0.85, 0.93, 0.97), 0.2)
    P["lamp_glow"] = mat("M_LampGlow", (1.0, 0.92, 0.70), 0.2, emit=(1.0, 0.90, 0.65), emit_strength=25.0)
    P["fuel_screen"] = mat("M_FuelScreen", (0.2, 0.9, 0.5), 0.3, emit=(0.3, 1.0, 0.6), emit_strength=3.0)
    P["sea_placeholder"] = mat("M_SeaPlaceholder", (0.12, 0.42, 0.55), 0.15, alpha=0.85)
    return P


# ---------------------------------------------------------------- mesh builder

def _faces_of(verts):
    return {f for v in verts for f in v.link_faces}


class MB:
    """Collects primitives into one bmesh with per-part materials."""

    def __init__(self):
        self.bm = bmesh.new()
        self.mats = []

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _tag(self, verts, m, smooth=False):
        mi = self._mi(m)
        for f in _faces_of(verts):
            f.material_index = mi
            f.smooth = smooth
        return verts

    @staticmethod
    def _matrix(loc, rot=(0, 0, 0), scale=(1, 1, 1)):
        S = Matrix.Diagonal((*scale, 1.0))
        return Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ S

    def box(self, size, loc, m, rot=(0, 0, 0)):
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=self._matrix(loc, rot, size))
        return self._tag(r["verts"], m)

    def cyl(self, r1, r2, depth, loc, m, rot=(0, 0, 0), seg=8, smooth=False, cap=True):
        r = bmesh.ops.create_cone(self.bm, cap_ends=cap, cap_tris=False, segments=seg,
                                  radius1=r1, radius2=r2, depth=depth,
                                  matrix=self._matrix(loc, rot))
        return self._tag(r["verts"], m, smooth)

    def cyl_between(self, p1, p2, r1, r2, m, seg=6, smooth=False):
        p1, p2 = Vector(p1), Vector(p2)
        d = p2 - p1
        q = d.to_track_quat('Z', 'Y')
        M = Matrix.Translation((p1 + p2) / 2) @ q.to_matrix().to_4x4()
        r = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg,
                                  radius1=r1, radius2=r2, depth=d.length, matrix=M)
        return self._tag(r["verts"], m, smooth)

    def box_between(self, p1, p2, w, h, m, up=(0, 0, 1)):
        p1, p2 = Vector(p1), Vector(p2)
        d = p2 - p1
        q = d.to_track_quat('Z', 'Y')
        M = Matrix.Translation((p1 + p2) / 2) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((w, h, d.length, 1))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)
        return self._tag(r["verts"], m)

    def ico(self, radius, loc, m, scale=(1, 1, 1), rot=(0, 0, 0), sub=1, jitter=0.0, seed=0, smooth=False):
        r = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=radius,
                                       matrix=self._matrix(loc, rot, scale))
        if jitter:
            rnd = random.Random(seed)
            for v in r["verts"]:
                v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jitter * radius
        return self._tag(r["verts"], m, smooth)

    def poly(self, pts, faces, m, smooth=False):
        vs = [self.bm.verts.new(p) for p in pts]
        for f in faces:
            try:
                self.bm.faces.new([vs[i] for i in f])
            except ValueError:
                pass
        return self._tag(vs, m, smooth)

    def gable_roof(self, w, l, h, loc, m, rot=(0, 0, 0), overhang=0.4, thick=0.15):
        """Triangular prism roof; ridge along local Y. w = width across the ridge."""
        hw, hl = w / 2 + overhang, l / 2 + overhang
        pts = []
        for s in (-1, 1):
            y = s * hl
            pts += [(-hw, y, 0), (0, y, h), (hw, y, 0), (hw, y, -thick), (0, y, h - thick * 1.4), (-hw, y, -thick)]
        M = self._matrix(loc, rot)
        pts = [M @ Vector(p) for p in pts]
        faces = [(0, 1, 7, 6), (1, 2, 8, 7), (2, 3, 9, 8), (3, 4, 10, 9), (4, 5, 11, 10), (5, 0, 6, 11),
                 (0, 5, 4, 1), (1, 4, 3, 2), (6, 7, 10, 11), (7, 8, 9, 10)]
        return self.poly(pts, faces, m)

    def torus(self, R, r, loc, m, rot=(0, 0, 0), seg=12, rseg=6):
        M = self._matrix(loc, rot)
        pts, faces = [], []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            for j in range(rseg):
                b = 2 * math.pi * j / rseg
                x = (R + r * math.cos(b)) * math.cos(a)
                y = (R + r * math.cos(b)) * math.sin(a)
                pts.append(M @ Vector((x, y, r * math.sin(b))))
        for i in range(seg):
            for j in range(rseg):
                a, b = i * rseg + j, i * rseg + (j + 1) % rseg
                c, d = ((i + 1) % seg) * rseg + (j + 1) % rseg, ((i + 1) % seg) * rseg + j
                faces.append((a, b, c, d))
        return self.poly(pts, faces, m)

    def wall(self, a, b, thick, height, m, openings=(), z0=0.0, glass=None):
        """Straight wall from a to b (x, y) with openings [(s0, s1, zb, zt)] in metres along the wall."""
        a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        d = b - a
        L = d.length
        rot = (0, 0, math.atan2(d.y, d.x))
        cuts = sorted({0.0, L, *[s for o in openings for s in o[:2]]})
        for s0, s1 in zip(cuts, cuts[1:]):
            mid = (s0 + s1) / 2
            hole = next((o for o in openings if o[0] <= mid <= o[1]), None)
            spans = [(0.0, height)] if hole is None else [(0.0, hole[2]), (hole[3], height)]
            c = a + d * (mid / L)
            for za, zb in spans:
                if zb - za > 0.01:
                    self.box((s1 - s0 + 0.002, thick, zb - za), (c.x, c.y, z0 + (za + zb) / 2), m, rot=rot)
            if hole is not None and glass is not None and hole[2] > 0.05:
                self.box((s1 - s0, 0.05, hole[3] - hole[2]), (c.x, c.y, z0 + (hole[2] + hole[3]) / 2), glass, rot=rot)

    def build(self, name, c, parent=None, mesh_only=False):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts[:], dist=0.0005)
        self.bm.normal_update()
        me = bpy.data.meshes.get(name) if mesh_only else None
        if me is not None:
            # shared asset: refresh in place so existing instances stay linked
            me.clear_geometry()
            me.materials.clear()
        else:
            me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        if mesh_only:
            for o in bpy.data.objects:
                if o.data == me:
                    o.data = me          # re-sync the object's material slot count with the refreshed mesh
            return me
        o = bpy.data.objects.new(name, me)
        return link(o, c, parent)


def instance(name, mesh, loc, c, parent=None, rot=(0, 0, 0), scale=1.0):
    o = bpy.data.objects.new(name, mesh)
    o.location = loc
    o.rotation_euler = rot
    o.scale = (scale, scale, scale) if isinstance(scale, (int, float)) else scale
    return link(o, c, parent)


def text_mesh(name, body, size, loc, rot, m, c, parent=None, extrude=0.05, align='CENTER'):
    cu = bpy.data.curves.new(name + "_crv", 'FONT')
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.resolution_u = 1                     # low-poly letters
    cu.align_x = align
    cu.align_y = 'CENTER'
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    scene().collection.objects.link(tmp)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    me.name = name
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    me.materials.clear()
    me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    return link(o, c, parent)


def light(name, kind, energy, loc, c, parent=None, color=(1, 1, 1), rot=(0, 0, 0), **kw):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    for k, v in kw.items():
        try:
            setattr(ld, k, v)
        except AttributeError:
            pass
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    o.rotation_euler = rot
    return link(o, c, parent)


# ---------------------------------------------------------------- terrain

def smoothstep(a, b, x):
    if a == b:
        return 0.0 if x < a else 1.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def fbm(x, y, seed, octaves=3, scale=0.04):
    s, amp, tot = scale, 1.0, 0.0
    for i in range(octaves):
        tot += amp * noise.noise(Vector((x * s + seed * 13.1, y * s - seed * 7.7, seed * 3.3 + i * 5.1)))
        s *= 2.1
        amp *= 0.5
    return tot


class IslandShape:
    """Height field for one island in its local coordinates (metres).

    lobes:  [(ox, oy, radius)] unioned into the coastline
    peaks:  [(ox, oy, radius, height)] smooth hills added on land
    cliffs: [(angle_rad, width_rad, height)] steep coast instead of beach on that side
    pads:   [(ox, oy, radius, z)] flat building areas
    """

    def __init__(self, lobes, peaks=(), cliffs=(), pads=(), seed=1, irregular=0.18,
                 beach_h=1.4, bumps=1.2, seabed_slope=0.35):
        self.lobes, self.peaks, self.cliffs, self.pads = lobes, peaks, cliffs, pads
        self.seed, self.irr, self.beach_h, self.bumps, self.slope = seed, irregular, beach_h, bumps, seabed_slope
        self.R = max(r for _, _, r in lobes)

    def coast_t(self, x, y):
        t = 99.0
        for ox, oy, r in self.lobes:
            dx, dy = x - ox, y - oy
            d = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            n = noise.noise(Vector((math.cos(a) * 1.6 + self.seed, math.sin(a) * 1.6, self.seed * 0.37 + ox * 0.01)))
            n += 0.5 * noise.noise(Vector((math.cos(a) * 4.0 - self.seed, math.sin(a) * 4.0, oy * 0.01)))
            t = min(t, d / (r * (1 + self.irr * n)))
        return t

    def height(self, x, y):
        t = self.coast_t(x, y)
        a = math.atan2(y, x)
        cliff_w, cliff_h = 0.0, 0.0
        for ca, cw, ch in self.cliffs:
            da = math.atan2(math.sin(a - ca), math.cos(a - ca))
            w = 1 - smoothstep(cw * 0.6, cw, abs(da))
            if w > cliff_w:
                cliff_w, cliff_h = w, ch
        if t >= 1.0:
            depth = (t - 1.0) * self.R * self.slope * (1 + 1.5 * cliff_w)
            z = -0.4 - min(16.0, depth) + 0.4 * fbm(x, y, self.seed + 4, 2, 0.08)
            return z
        u = 1.0 - t
        beach = -0.4 + smoothstep(0.0, 0.14, u) * (self.beach_h + 0.4)
        cliff = -0.4 + smoothstep(0.0, 0.05, u) * (cliff_h + 0.4)
        z = beach * (1 - cliff_w) + cliff * cliff_w
        inland = smoothstep(0.08, 0.35, u)
        for px, py, pr, ph in self.peaks:
            d = math.hypot(x - px, y - py) / pr
            z += ph * (1 - smoothstep(0.0, 1.0, d)) * inland
        z += self.bumps * fbm(x, y, self.seed, 3, 0.05) * inland
        for px, py, pr, pz in self.pads:
            d = math.hypot(x - px, y - py)
            w = 1 - smoothstep(pr, pr * 1.6 + 3, d)
            z = z * (1 - w) + pz * w
        return z


def build_terrain(name, center, shape, P, c, parent=None, cell=3.0, kind="tropical"):
    """Low-poly triangulated terrain; material picked per face from height and slope."""
    cx, cy = center
    ext = shape.R * 1.9 + max(math.hypot(ox, oy) for ox, oy, _ in shape.lobes)
    cell *= TERRAIN_CELL_SCALE
    n = int(2 * ext / cell)
    bm = bmesh.new()
    rnd = random.Random(shape.seed)
    grid = []
    for i in range(n + 1):
        row = []
        for j in range(n + 1):
            x = -ext + i * cell + rnd.uniform(-0.3, 0.3) * cell
            y = -ext + j * cell + rnd.uniform(-0.3, 0.3) * cell
            row.append(bm.verts.new((cx + x, cy + y, shape.height(x, y))))
        grid.append(row)
    for i in range(n):
        for j in range(n):
            a, b, cc, d = grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]
            if max(v.co.z for v in (a, b, cc, d)) < -9.0:
                continue
            if (i + j) % 2:
                bm.faces.new((a, b, cc)); bm.faces.new((a, cc, d))
            else:
                bm.faces.new((a, b, d)); bm.faces.new((b, cc, d))
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.normal_update()

    if kind == "tropical":
        order = ["seabed", "sand_wet", "sand", "grass", "rock_warm"]
    elif kind == "rocky":
        order = ["seabed", "sand_dark", "sand_dark", "grass_dark", "rock"]
    elif kind == "meadow":
        order = ["seabed", "sand_wet", "sand", "grass_dry", "rock_warm"]
    else:
        order = ["seabed", "sand_wet", "sand", "grass", "rock"]
    mats = [P[k] for k in order]
    for f in bm.faces:
        z = sum(v.co.z for v in f.verts) / len(f.verts)
        steep = f.normal.z < 0.78
        if z < -1.2:
            mi = 0
        elif z < 0.5:
            mi = 1
        elif steep and z > 1.0:
            mi = 4
        elif z < shape.beach_h + 0.6:
            mi = 2
        else:
            mi = 3
        f.material_index = mi
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    link(o, c, parent)
    bpy.context.view_layer.update()
    return o


class Ground:
    """Ray-casts straight down onto terrain objects."""

    def __init__(self, objs):
        self.trees = []
        for o in objs:
            bm = bmesh.new()
            bm.from_mesh(o.data)
            bm.transform(o.matrix_world)
            self.trees.append(BVHTree.FromBMesh(bm))
            bm.free()

    def z(self, x, y, default=None):
        best = None
        for t in self.trees:
            hit = t.ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)))
            if hit[0] is not None and (best is None or hit[0].z > best):
                best = hit[0].z
        return best if best is not None else default

    def normal_z(self, x, y):
        for t in self.trees:
            hit = t.ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)))
            if hit[0] is not None:
                return hit[1].z
        return 1.0

    def shore(self, start, angle, level=DOCK_DECK_Z - 0.2, step=0.5, max_d=200):
        """Walk outward from start along angle; return first point where ground drops below level."""
        sx, sy = start
        ca, sa = math.cos(angle), math.sin(angle)
        d = 0.0
        while d < max_d:
            z = self.z(sx + ca * d, sy + sa * d, -20)
            if z < level:
                return Vector((sx + ca * d, sy + sa * d, z))
            d += step
        return Vector((sx + ca * d, sy + sa * d, -20))


def scatter(ground, center, radius, count, seed, zmin, zmax, slope_min=0.85, avoid=(), min_gap=0.0):
    """Random points on terrain within a height band, away from 'avoid' circles [(x, y, r)]."""
    rnd = random.Random(seed)
    count = max(1, int(round(count * SCATTER_DENSITY)))
    pts, tries = [], 0
    while len(pts) < count and tries < count * 60:
        tries += 1
        a = rnd.uniform(0, 2 * math.pi)
        r = radius * math.sqrt(rnd.random())
        x, y = center[0] + math.cos(a) * r, center[1] + math.sin(a) * r
        z = ground.z(x, y)
        if z is None or not (zmin <= z <= zmax):
            continue
        if ground.normal_z(x, y) < slope_min:
            continue
        if any(math.hypot(x - ax, y - ay) < ar for ax, ay, ar in avoid):
            continue
        if min_gap and any(math.hypot(x - px, y - py) < min_gap for px, py, _ in pts):
            continue
        pts.append((x, y, z))
    return pts
