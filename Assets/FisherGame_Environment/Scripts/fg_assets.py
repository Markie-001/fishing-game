"""Reusable low-poly assets (shared meshes) plus the dock and boat builders."""
import bpy, math, random
from mathutils import Vector
from fg_lib import MB, DOCK_DECK_Z, coll, clear_coll, link, mat


# ---------------------------------------------------------------- vegetation

def palm_mesh(name, P, height=7.0, lean=1.6, seed=0, fronds=6):
    rnd = random.Random(seed)
    mb = MB()
    a = rnd.uniform(0, 2 * math.pi)
    lean_dir = Vector((math.cos(a), math.sin(a), 0))
    pts = []
    for i in range(5):
        t = i / 4
        pts.append(Vector((0, 0, height * t)) + lean_dir * lean * t * t)
    for i in range(4):
        r = 0.24 - 0.1 * (i / 4)
        mb.cyl_between(pts[i], pts[i + 1] + (pts[i + 1] - pts[i]) * 0.04, r * 1.12, r, P["wood_light"], seg=5)
    top = pts[-1]
    for k in range(2):
        ang = k * 3.1 + rnd.random()
        mb.ico(0.17, top + Vector((math.cos(ang) * 0.25, math.sin(ang) * 0.25, -0.25)), P["wood_dark"], sub=1)
    for f in range(fronds):
        ang = 2 * math.pi * f / fronds + rnd.uniform(-0.2, 0.2)
        d = Vector((math.cos(ang), math.sin(ang), 0))
        side = Vector((-d.y, d.x, 0))
        length = rnd.uniform(3.0, 3.8)
        droop = rnd.uniform(0.18, 0.28)
        rise = rnd.uniform(0.5, 0.9)
        rows = 3
        pts_f, faces = [], []
        for k in range(rows + 1):
            t = k / rows
            c = top + d * length * t + Vector((0, 0, rise * t - droop * (t * length) ** 1.6 / 2.2))
            w = 0.65 * math.sin(math.pi * min(1, t * 1.05)) + 0.05
            pts_f += [c + side * w - Vector((0, 0, 0.12 * w)), c + Vector((0, 0, 0.05)), c - side * w - Vector((0, 0, 0.12 * w))]
        for k in range(rows):
            b = k * 3
            faces += [(b, b + 3, b + 4, b + 1), (b + 1, b + 4, b + 5, b + 2)]
        mb.poly(pts_f, faces, P["leaf"])
    return mb.build(name, None, mesh_only=True)


def pine_mesh(name, P, height=9.0, seed=0):
    rnd = random.Random(seed)
    mb = MB()
    mb.cyl(0.28, 0.18, height * 0.35, (0, 0, height * 0.175), P["wood_dark"], seg=6)
    tiers = 3
    for i in range(tiers):
        t = i / tiers
        r = (1.0 - t * 0.75) * height * 0.26
        z0 = height * (0.22 + t * 0.62)
        mb.cyl(r, 0.05, height * 0.34, (0, 0, z0 + height * 0.17), P["pine"], seg=6,
               rot=(0, 0, rnd.uniform(0, 1)))
    return mb.build(name, None, mesh_only=True)


def broadleaf_mesh(name, P, height=6.0, seed=0):
    rnd = random.Random(seed)
    mb = MB()
    mb.cyl(0.25, 0.16, height * 0.55, (0, 0, height * 0.275), P["wood_dark"], seg=6)
    for k in range(3):
        off = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 0.6))) * height * 0.16
        mb.ico(height * rnd.uniform(0.22, 0.3), Vector((0, 0, height * 0.7)) + off, P["grass_dark"],
               scale=(1, 1, 0.8), jitter=0.18, seed=seed * 10 + k)
    return mb.build(name, None, mesh_only=True)


def bush_mesh(name, P, size=1.2, seed=0, m="bush"):
    rnd = random.Random(seed)
    mb = MB()
    for k in range(2):
        off = Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), 0)) * size
        mb.ico(size * rnd.uniform(0.55, 0.8), off + Vector((0, 0, size * 0.35)), P[m],
               scale=(1, 1, 0.7), jitter=0.2, seed=seed * 7 + k)
    return mb.build(name, None, mesh_only=True)


def rock_mesh(name, P, size=1.5, seed=0, m="rock", flat=0.65):
    mb = MB()
    mb.ico(size, (0, 0, size * flat * 0.35), P[m], scale=(1.0, 0.8, flat), sub=1, jitter=0.28, seed=seed)
    return mb.build(name, None, mesh_only=True)


# ---------------------------------------------------------------- props

def fuel_pump_mesh(name, P, brand="red"):
    """Marine fuel dispenser: plinth, cabinet, lit display, hose reel, sign mast."""
    mb = MB()
    c = P[brand]
    mb.box((1.1, 0.8, 0.12), (0, 0, 0.06), P["concrete"])
    mb.box((0.8, 0.55, 1.35), (0, 0, 0.8), c)
    mb.box((0.84, 0.59, 0.12), (0, 0, 1.53), P["white"])
    mb.box((0.5, 0.04, 0.28), (0, -0.29, 1.15), P["fuel_screen"])
    mb.box((0.5, 0.04, 0.28), (0, 0.29, 1.15), P["fuel_screen"])
    mb.box((0.62, 0.03, 0.42), (0, -0.285, 0.62), P["white"])
    mb.box((0.62, 0.03, 0.42), (0, 0.285, 0.62), P["white"])
    mb.cyl(0.22, 0.22, 0.12, (0.47, 0, 0.9), P["black"], rot=(0, math.pi / 2, 0), seg=10)
    mb.cyl_between((0.53, 0, 0.9), (0.62, 0.0, 0.35), 0.035, 0.035, P["black"])
    mb.cyl_between((0.62, 0.0, 0.35), (0.7, 0.0, 0.9), 0.035, 0.035, P["black"])
    mb.box((0.08, 0.12, 0.25), (0.72, 0, 1.0), P["metal_dark"])
    mb.cyl(0.05, 0.05, 2.6, (-0.48, 0, 1.3), P["metal"], seg=6)
    mb.box((0.06, 0.75, 0.45), (-0.48, 0, 2.55), c)
    mb.box((0.07, 0.6, 0.12), (-0.48, 0, 2.55), P["white"])
    return mb.build(name, None, mesh_only=True)


def barrel_mesh(name, P, m="blue"):
    mb = MB()
    mb.cyl(0.3, 0.3, 0.9, (0, 0, 0.45), P[m], seg=10)
    for z in (0.18, 0.72):
        mb.cyl(0.315, 0.315, 0.05, (0, 0, z), P["metal_dark"], seg=10)
    return mb.build(name, None, mesh_only=True)


def crate_mesh(name, P, size=0.7):
    mb = MB()
    s = size
    mb.box((s, s, s), (0, 0, s / 2), P["wood_light"])
    for z in (0.08, s - 0.08):
        mb.box((s + 0.03, s + 0.03, 0.08), (0, 0, z), P["wood"])
    mb.box((0.06, s + 0.03, s), (0, 0, s / 2), P["wood"], rot=(0.0, 0.85, 0))
    return mb.build(name, None, mesh_only=True)


def fish_crate_mesh(name, P):
    mb = MB()
    mb.box((0.9, 0.55, 0.06), (0, 0, 0.03), P["blue"])
    for x, w in ((-0.43, 0.04), (0.43, 0.04)):
        mb.box((w, 0.55, 0.3), (x, 0, 0.18), P["blue"])
    for y in (-0.255, 0.255):
        mb.box((0.9, 0.04, 0.3), (0, y, 0.18), P["blue"])
    mb.box((0.82, 0.47, 0.06), (0, 0, 0.25), P["ice"])
    for k in range(2):
        mb.ico(0.07, (-0.18 + k * 0.32, 0.04 * (-1) ** k, 0.3), P["fish"], scale=(3.0, 1.0, 0.8), rot=(0, 0, 0.2 * k))
    return mb.build(name, None, mesh_only=True)


def lamp_post_mesh(name, P):
    mb = MB()
    mb.cyl(0.1, 0.07, 3.3, (0, 0, 1.65), P["metal_dark"], seg=4)
    mb.cyl(0.14, 0.14, 0.3, (0, 0, 3.47), P["lamp_glow"], seg=4)
    mb.cyl(0.25, 0.05, 0.2, (0, 0, 3.72), P["metal_dark"], seg=4)
    return mb.build(name, None, mesh_only=True)


def bollard_mesh(name, P):
    mb = MB()
    mb.cyl(0.14, 0.12, 0.45, (0, 0, 0.225), P["metal_dark"], seg=8)
    mb.cyl(0.19, 0.19, 0.07, (0, 0, 0.47), P["metal_dark"], seg=8)
    return mb.build(name, None, mesh_only=True)


def life_ring_mesh(name, P):
    mb = MB()
    mb.box((0.1, 0.1, 1.5), (0, 0, 0.75), P["wood"])
    ring = mb.torus(0.32, 0.08, (0, -0.1, 1.15), P["red"], rot=(math.pi / 2, 0, 0), seg=12, rseg=5)
    return mb.build(name, None, mesh_only=True)


def net_mesh(name, P, w=2.4, h=1.6):
    """Fishing net hanging between two poles, with floats."""
    mb = MB()
    for x in (-w / 2, w / 2):
        mb.cyl(0.06, 0.05, h + 0.6, (x, 0, (h + 0.6) / 2), P["wood_grey"], seg=6)
    cols, rows = 9, 6
    pts, faces = [], []
    for i in range(cols + 1):
        for j in range(rows + 1):
            x = -w / 2 + w * i / cols
            sag = 0.25 * math.sin(math.pi * i / cols)
            z = h + 0.3 - sag - (h - 0.2) * j / rows
            pts.append((x, 0.03 * ((i + j) % 2), z))
    for i in range(cols):
        for j in range(rows):
            if (i + j) % 2 == 0:
                a = i * (rows + 1) + j
                faces.append((a, a + rows + 1, a + rows + 2, a + 1))
    mb.poly(pts, faces, P["rope"])
    for i in range(1, cols, 2):
        x = -w / 2 + w * i / cols
        mb.ico(0.08, (x, 0, h + 0.3 - 0.25 * math.sin(math.pi * i / cols)), P["fabric_orange"], sub=1)
    return mb.build(name, None, mesh_only=True)


def bench_mesh(name, P):
    mb = MB()
    for x in (-0.7, 0.7):
        mb.box((0.08, 0.4, 0.42), (x, 0, 0.21), P["wood_dark"])
    for y in (-0.13, 0.0, 0.13):
        mb.box((1.6, 0.11, 0.05), (0, y, 0.45), P["wood_light"])
    return mb.build(name, None, mesh_only=True)


def deck_chair_mesh(name, P, fabric="fabric_blue"):
    mb = MB()
    mb.box((0.6, 1.1, 0.05), (0, 0, 0.32), P[fabric], rot=(0.12, 0, 0))
    mb.box((0.6, 0.7, 0.05), (0, 0.72, 0.62), P[fabric], rot=(-0.95, 0, 0))
    for x in (-0.3, 0.3):
        mb.box((0.05, 1.3, 0.05), (x, 0.05, 0.3), P["wood"], rot=(0.15, 0, 0))
        mb.box((0.05, 0.05, 0.9), (x, 0.55, 0.45), P["wood"], rot=(-0.5, 0, 0))
    return mb.build(name, None, mesh_only=True)


def umbrella_mesh(name, P, fabric="fabric_white"):
    mb = MB()
    mb.cyl(0.03, 0.03, 2.4, (0, 0, 1.2), P["wood"], seg=6)
    mb.cyl(1.3, 0.05, 0.5, (0, 0, 2.35), P[fabric], seg=8)
    return mb.build(name, None, mesh_only=True)


# ---------------------------------------------------------------- boats

def boat_mesh(name, P, length=6.0, beam=2.2, hull="white", stripe="navy", style="motor"):
    """Low-poly boat; origin at the waterline, bow towards +X."""
    mb = MB()
    L, B = length, beam / 2
    N, M = 12, 7

    def width(t):
        if t < 0.45:
            return B * (0.86 + 0.14 * t / 0.45)
        return max(0.02, B * math.sqrt(max(0.0, 1 - ((t - 0.45) / 0.55) ** 2)))

    def top(t):
        return 0.55 + 0.25 * t * t + 0.06 * L / 6

    def depth(t):
        return (0.85 + 0.05 * L / 6) * (1 - 0.35 * t)

    pts, faces = [], []
    for i in range(N):
        t = i / (N - 1)
        x = -L / 2 + L * t
        w, zt, d = width(t), top(t), depth(t)
        for j in range(M):
            a = -math.pi / 2 + math.pi * j / (M - 1)
            pts.append((x, w * math.sin(a), zt - d * abs(math.cos(a)) ** 0.6))
    for i in range(N - 1):
        for j in range(M - 1):
            faces.append((i * M + j, (i + 1) * M + j, (i + 1) * M + j + 1, i * M + j + 1))
    mb.poly(pts, faces, P[hull])
    deck = []
    for i in range(N - 1):
        deck.append((i * M, i * M + M - 1, (i + 1) * M + M - 1, (i + 1) * M))
    mb.poly(pts, deck, P["wood_light"] if style != "fisher" else P["wood_grey"])
    mb.poly(pts, [tuple(range(0, M))[::-1], tuple(range((N - 1) * M, N * M))], P[hull])
    # stripe just under the gunwale
    for s in (-1, 1):
        a = mb.box_between((-L / 2 + 0.1, s * (width(0) + 0.01), top(0) - 0.12),
                           (L / 2 - L * 0.2, s * (width(0.8) + 0.01), top(0.8) - 0.12), 0.03, 0.12, P[stripe])
    zt = top(0.3)
    if style == "motor":
        mb.box((0.9, beam * 0.55, 0.7), (L * 0.02, 0, zt + 0.35), P["white"])
        mb.box((0.06, beam * 0.6, 0.5), (L * 0.02 + 0.45, 0, zt + 0.8), P["glass"], rot=(0, -0.5, 0))
        mb.box((0.5, 0.35, 0.6), (-L / 2 - 0.15, 0, zt - 0.1), P["metal_dark"])
        mb.box((0.25, 0.2, 0.5), (-L / 2 - 0.2, 0, zt - 0.55), P["metal_dark"])
        for k in range(2):
            mb.box((0.6, beam * 0.5, 0.35), (-L * 0.28 + k * 0.7, 0, zt + 0.17), P["fabric_white"])
    elif style == "cruiser":
        mb.box((L * 0.42, beam * 0.72, 1.0), (L * 0.05, 0, zt + 0.5), P["white"])
        mb.box((L * 0.43, beam * 0.73, 0.32), (L * 0.05, 0, zt + 0.62), P["navy"])
        mb.box((0.06, beam * 0.7, 0.55), (L * 0.27, 0, zt + 1.15), P["glass"], rot=(0, -0.6, 0))
        mb.box((L * 0.3, beam * 0.6, 0.06), (L * 0.0, 0, zt + 1.55), P["white"])
        for x in (-L * 0.1, L * 0.1):
            mb.cyl(0.03, 0.03, 0.55, (x, beam * 0.28, zt + 1.27), P["metal"], seg=4)
            mb.cyl(0.03, 0.03, 0.55, (x, -beam * 0.28, zt + 1.27), P["metal"], seg=4)
        mb.box((0.6, 0.4, 0.5), (-L / 2 - 0.2, 0, zt - 0.2), P["metal_dark"])
    elif style == "fisher":
        mb.box((L * 0.28, beam * 0.7, 1.5), (-L * 0.18, 0, zt + 0.75), P["white"])
        mb.box((L * 0.3, beam * 0.75, 0.1), (-L * 0.18, 0, zt + 1.55), P[stripe])
        mb.box((0.04, beam * 0.6, 0.45), (-L * 0.18 + L * 0.14 + 0.02, 0, zt + 1.05), P["glass"])
        mb.cyl(0.05, 0.04, 3.0, (L * 0.1, 0, zt + 1.5), P["metal"], seg=6)
        mb.cyl_between((L * 0.1, 0, zt + 2.6), (-L * 0.45, 0, zt + 0.9), 0.03, 0.03, P["metal"])
        mb.box((0.8, 0.6, 0.35), (L * 0.2, 0.35, zt + 0.18), P["blue"])
    elif style == "sail":
        mb.cyl(0.06, 0.05, L * 1.1, (L * 0.1, 0, zt + L * 0.55), P["metal"], seg=6)
        sail = [(L * 0.08, 0, zt + 0.7), (L * 0.08, 0, zt + L * 1.05), (-L * 0.38, 0, zt + 0.7)]
        mb.poly(sail, [(0, 1, 2)], P["fabric_white"])
        mb.cyl_between((L * 0.1, 0, zt + 0.6), (-L * 0.4, 0, zt + 0.6), 0.04, 0.04, P["metal"])
        mb.box((L * 0.3, beam * 0.5, 0.45), (-L * 0.02, 0, zt + 0.22), P["white"])
    return mb.build(name, None, mesh_only=True)


# ---------------------------------------------------------------- docks

class Dock:
    """Timber dock built from rectangles in a local (u = outward, v = left) frame.

    Rectangles: (u0, u1, v0, v1). Planks run across the long side.
    """

    def __init__(self, name, start, angle, ground, P, deck_z=DOCK_DECK_Z, plank_m="wood", pile_m="wood_dark"):
        self.name, self.start, self.angle, self.ground, self.P = name, Vector(start), angle, ground, P
        self.deck_z = deck_z
        self.du = Vector((math.cos(angle), math.sin(angle), 0))
        self.dv = Vector((-math.sin(angle), math.cos(angle), 0))
        self.rects = []
        self.mb = MB()
        self.plank_m, self.pile_m = P[plank_m], P[pile_m]

    def w(self, u, v, z=None):
        p = self.start + self.du * u + self.dv * v
        p.z = self.deck_z if z is None else z
        return p

    def rect(self, u0, u1, v0, v1, posts=True, rail=False):
        self.rects.append((u0, u1, v0, v1))
        P, mb = self.P, self.mb
        along_u = (u1 - u0) >= (v1 - v0)
        rnd = random.Random(len(self.rects) * 31 + int(u0 * 7))
        z = self.deck_z - 0.05
        if along_u:
            n = int((u1 - u0) / 0.8)
            for k in range(n):
                u = u0 + (k + 0.5) * (u1 - u0) / n
                self._plank(u, u, v0 - 0.05, v1 + 0.05, z, rnd)
        else:
            n = int((v1 - v0) / 0.8)
            for k in range(n):
                v = v0 + (k + 0.5) * (v1 - v0) / n
                self._plank(u0 - 0.05, u1 + 0.05, v, v, z, rnd)
        # stringers
        zs = self.deck_z - 0.22
        for v in (v0 + 0.15, v1 - 0.15):
            mb.box_between(self.w(u0, v, zs), self.w(u1, v, zs), 0.16, 0.26, self.pile_m)
        for u in (u0 + 0.15, u1 - 0.15):
            mb.box_between(self.w(u, v0, zs), self.w(u, v1, zs), 0.16, 0.26, self.pile_m)
        if posts:
            step = 5.0
            nu = max(1, int(round((u1 - u0) / step)))
            nv = max(1, int(round((v1 - v0) / step)))
            spots = set()
            for k in range(nu + 1):
                u = u0 + 0.15 + (u1 - u0 - 0.3) * k / nu
                spots.add((round(u, 2), v0 + 0.15)); spots.add((round(u, 2), v1 - 0.15))
            for k in range(nv + 1):
                v = v0 + 0.15 + (v1 - v0 - 0.3) * k / nv
                spots.add((u0 + 0.15, round(v, 2))); spots.add((u1 - 0.15, round(v, 2)))
            for u, v in spots:
                p = self.w(u, v)
                gz = self.ground.z(p.x, p.y, -6.0)
                if gz > self.deck_z - 0.3:
                    continue
                mb.cyl_between(self.w(u, v, gz - 0.5), self.w(u, v, self.deck_z + 0.35), 0.17, 0.15, self.pile_m, seg=4)
        if rail:
            for v in (v0 + 0.1, v1 - 0.1):
                n = max(1, int((u1 - u0) / 2.0))
                for k in range(n + 1):
                    u = u0 + (u1 - u0) * k / n
                    mb.box((0.1, 0.1, 1.0), self.w(u, v, self.deck_z + 0.5), self.P["wood_dark"])
                mb.box_between(self.w(u0, v, self.deck_z + 1.0), self.w(u1, v, self.deck_z + 1.0), 0.1, 0.12, self.P["wood_dark"])
        return self

    def _plank(self, ua, ub, va, vb, z, rnd):
        jitter = rnd.uniform(-0.015, 0.015)
        if ua == ub:
            self.mb.box_between(self.w(ua, va, z + jitter), self.w(ua, vb, z + jitter), 0.74, 0.08, self.plank_m)
        else:
            self.mb.box_between(self.w(ua, va, z + jitter), self.w(ub, va, z + jitter), 0.74, 0.08, self.plank_m)

    def cleats(self, spots):
        for u, v in spots:
            p = self.w(u, v, self.deck_z + 0.07)
            self.mb.box((0.35, 0.08, 0.06), p, self.P["metal_dark"], rot=(0, 0, self.angle))
            self.mb.box((0.08, 0.08, 0.1), p - Vector((0, 0, 0.04)), self.P["metal_dark"], rot=(0, 0, self.angle))
        return self

    def tires(self, spots, side=1):
        """Old tyres hung on the outer edge as fenders."""
        for u, v in spots:
            p = self.w(u, v, self.deck_z - 0.45)
            self.mb.torus(0.3, 0.1, p, self.P["black"], rot=(math.pi / 2, 0, self.angle), seg=10, rseg=5)
        return self

    def build(self, c, parent=None):
        return self.mb.build(self.name, c, parent)


# ---------------------------------------------------------------- NPCs

NPC_STYLES = {
    # name: skin, hair, top, sleeves, legs, shoes, extra details
    "Emre": dict(skin=(0.78, 0.58, 0.42), hair=(0.08, 0.06, 0.05), top=(0.95, 0.95, 0.93), sleeves=(0.95, 0.95, 0.93),
                 legs=(0.13, 0.18, 0.30), shoes=(0.35, 0.22, 0.12), hair_style="short", sunglasses=True, blazer=(0.12, 0.17, 0.30)),
    "Mark": dict(skin=(0.93, 0.76, 0.64), hair=(0.62, 0.30, 0.14), top=(0.36, 0.40, 0.22), sleeves=(0.70, 0.18, 0.15),
                 legs=(0.25, 0.35, 0.52), shoes=(0.22, 0.36, 0.22), hair_style="cap", cap=(0.22, 0.36, 0.22), beard="short",
                 boots=True),
    "Ruben": dict(skin=(0.90, 0.72, 0.60), hair=(0.85, 0.72, 0.45), top=(0.98, 0.78, 0.15), sleeves=(0.98, 0.78, 0.15),
                  legs=(0.12, 0.12, 0.14), shoes=(0.93, 0.93, 0.90), hair_style="beanie", beanie=(0.18, 0.36, 0.60),
                  apron=(0.93, 0.93, 0.90), boots=True),
    "Teun": dict(skin=(0.82, 0.62, 0.48), hair=(0.92, 0.92, 0.90), top=(0.40, 0.26, 0.16), sleeves=(0.40, 0.26, 0.16),
                 legs=(0.18, 0.16, 0.15), shoes=(0.08, 0.07, 0.07), hair_style="captain", beard="long", coat=True,
                 lantern=True, boots=True),
    # the player character (placeholder look, can be swapped for a rigged model later)
    "Player": dict(skin=(0.86, 0.66, 0.52), hair=(0.30, 0.20, 0.12), top=(0.20, 0.55, 0.55), sleeves=(0.20, 0.55, 0.55),
                   legs=(0.55, 0.50, 0.36), shoes=(0.95, 0.95, 0.93), hair_style="bucket", bucket=(0.80, 0.72, 0.52),
                   backpack=(0.85, 0.40, 0.15), rod_on_back=True),
}


def npc_mesh(name, P, who):
    """Low-poly NPC, ~1.8 m, A-pose arms (rig-friendly), origin between the feet, facing +X."""
    s = NPC_STYLES[who]
    m = lambda key, col: mat("M_NPC_%s_%s" % (who, key), col, 0.8)
    skin, hair = m("Skin", s["skin"]), m("Hair", s["hair"])
    top, sleeves, legs, shoes = m("Top", s["top"]), m("Sleeves", s["sleeves"]), m("Legs", s["legs"]), m("Shoes", s["shoes"])
    black = P["black"]
    mb = MB()
    for y in (-0.11, 0.11):
        mb.box((0.27, 0.12, 0.1), (0.04, y, 0.05), shoes)
        if s.get("boots"):
            mb.cyl(0.075, 0.08, 0.38, (0, y, 0.28), shoes, seg=6)
            mb.cyl_between((0, y, 0.45), (0, y * 0.9, 0.93), 0.08, 0.09, legs, seg=6)
        else:
            mb.cyl_between((0, y, 0.08), (0, y * 0.9, 0.93), 0.075, 0.09, legs, seg=6)
    mb.box((0.25, 0.36, 0.2), (0, 0, 0.95), legs)
    mb.cyl(0.2, 0.23, 0.6, (0, 0, 1.3), top, seg=8)
    if s.get("blazer"):
        bl = m("Blazer", s["blazer"])
        for y in (-1, 1):
            mb.box((0.36, 0.14, 0.58), (-0.02, y * 0.13, 1.3), bl)
        mb.box((0.2, 0.42, 0.5), (-0.1, 0, 1.31), bl)
    if s.get("apron"):
        ap = m("Apron", s["apron"])
        mb.box((0.04, 0.36, 0.85), (0.215, 0, 1.05), ap)
        mb.box((0.03, 0.06, 0.3), (0.2, 0, 1.52), ap)
    if s.get("coat"):
        mb.cyl(0.24, 0.32, 0.6, (0, 0, 0.75), top, seg=8)
        for y in (-1, 1):
            mb.box((0.04, 0.1, 0.12), (0.22, y * 0.07, 1.42), P["yellow"])
    mb.ico(0.1, (0, -0.26, 1.54), sleeves)
    mb.ico(0.1, (0, 0.26, 1.54), sleeves)
    for y in (-1, 1):
        sh, el, ha = Vector((0, y * 0.27, 1.53)), Vector((0.02, y * 0.43, 1.25)), Vector((0.06, y * 0.52, 0.98))
        mb.cyl_between(sh, el, 0.068, 0.06, sleeves, seg=6)
        mb.cyl_between(el, ha, 0.058, 0.05, sleeves if s.get("coat") else skin, seg=6)
        mb.ico(0.065, ha - Vector((0, 0, 0.04)), skin)
    mb.cyl(0.06, 0.06, 0.12, (0, 0, 1.65), skin, seg=6)
    mb.ico(0.15, (0, 0, 1.82), skin, scale=(1.0, 0.92, 1.1), sub=2)
    for y in (-0.05, 0.05):
        mb.box((0.02, 0.035, 0.035), (0.14, y, 1.84), black)
    mb.box((0.05, 0.035, 0.05), (0.155, 0, 1.79), skin)
    if s.get("sunglasses"):
        mb.box((0.03, 0.2, 0.05), (0.145, 0, 1.845), black)
    hs = s["hair_style"]
    if hs == "short":
        mb.ico(0.168, (-0.03, 0, 1.9), hair, scale=(1.0, 0.98, 0.72), sub=2)
        mb.box((0.08, 0.3, 0.12), (-0.11, 0, 1.8), hair)
    elif hs == "cap":
        c = m("Cap", s["cap"])
        mb.cyl(0.155, 0.14, 0.12, (-0.01, 0, 1.94), c, seg=8)
        mb.box((0.16, 0.24, 0.025), (0.17, 0, 1.9), c, rot=(0, 0.15, 0))
    elif hs == "beanie":
        c = m("Beanie", s["beanie"])
        mb.ico(0.16, (-0.01, 0, 1.9), c, scale=(1.0, 0.98, 0.85), sub=1)
        mb.cyl(0.162, 0.162, 0.06, (-0.01, 0, 1.87), c, seg=8)
    elif hs == "bucket":
        c = m("Hat", s["bucket"])
        mb.ico(0.158, (-0.01, 0, 1.9), hair, scale=(1.0, 0.98, 0.7), sub=1)
        mb.cyl(0.15, 0.135, 0.13, (-0.01, 0, 1.97), c, seg=10)
        mb.cyl(0.25, 0.25, 0.025, (-0.01, 0, 1.91), c, seg=10)
    elif hs == "captain":
        mb.cyl(0.165, 0.165, 0.09, (0, 0, 1.95), P["navy"], seg=10)
        mb.cyl(0.19, 0.19, 0.06, (-0.01, 0, 2.02), P["white"], seg=10)
        mb.box((0.14, 0.26, 0.02), (0.17, 0, 1.92), black, rot=(0, 0.2, 0))
        mb.box((0.02, 0.06, 0.04), (0.165, 0, 1.97), P["yellow"])
    if s.get("beard") == "short":
        mb.ico(0.12, (0.06, 0, 1.73), hair, scale=(0.9, 1.1, 0.8), sub=1)
    elif s.get("beard") == "long":
        mb.ico(0.13, (0.07, 0, 1.68), hair, scale=(0.8, 1.05, 1.3), sub=1)
        mb.ico(0.05, (0.15, 0, 1.79), hair, scale=(0.6, 2.2, 0.6))
    if s.get("backpack"):
        bp = m("Backpack", s["backpack"])
        mb.box((0.18, 0.32, 0.42), (-0.29, 0, 1.3), bp)
        mb.box((0.06, 0.26, 0.16), (-0.39, 0, 1.2), bp)
    if s.get("rod_on_back"):
        mb.cyl_between((-0.36, -0.2, 0.75), (-0.42, 0.22, 2.5), 0.018, 0.008, P["black"], seg=4)
        mb.cyl(0.05, 0.05, 0.05, (-0.37, -0.15, 0.95), P["metal"], rot=(math.pi / 2, 0, 0), seg=6)
    if s.get("lantern"):
        h = Vector((0.06, 0.52, 0.92))
        mb.cyl_between(h, h - Vector((0, 0, 0.12)), 0.01, 0.01, P["metal_dark"], seg=4)
        mb.box((0.14, 0.14, 0.03), h - Vector((0, 0, 0.14)), P["metal_dark"])
        mb.box((0.11, 0.11, 0.16), h - Vector((0, 0, 0.24)), P["lamp_glow"])
        mb.box((0.14, 0.14, 0.03), h - Vector((0, 0, 0.34)), P["metal_dark"])
    return mb.build(name, None, mesh_only=True)


def place_npc(who, P, loc, facing, c, parent=None, name=None, spot_name=None):
    """NPC mesh + an empty marker '<Name>_Spot' (for scripts / dialogue triggers later)."""
    name = name or "NPC_%s" % who
    me = npc_mesh(name, P, who)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = (0, 0, facing)
    link(o, c, parent)
    spot = bpy.data.objects.new(spot_name or "%s_Spot" % name, None)
    spot.empty_display_type = 'SINGLE_ARROW'
    spot.empty_display_size = 1.0
    spot.location = loc
    spot.rotation_euler = (math.pi / 2, 0, facing - math.pi / 2)
    link(spot, c, parent)
    return o


# ---------------------------------------------------------------- library

def build_library(P):
    lib = coll("00_Assets_Library")
    clear_coll(lib)
    A = {}
    A["palm"] = [palm_mesh("Asset_Palm_%d" % i, P, height=6.5 + i * 1.2, lean=1.2 + i * 0.5, seed=i + 3) for i in range(3)]
    A["pine"] = [pine_mesh("Asset_Pine_%d" % i, P, height=8 + i * 2.5, seed=i) for i in range(3)]
    A["tree"] = [broadleaf_mesh("Asset_Tree_%d" % i, P, height=5 + i * 1.5, seed=i + 2) for i in range(2)]
    A["bush"] = [bush_mesh("Asset_Bush_%d" % i, P, size=0.9 + 0.4 * i, seed=i) for i in range(3)]
    A["bush_dark"] = [bush_mesh("Asset_BushDark_%d" % i, P, size=1.0 + 0.3 * i, seed=i + 9, m="grass_dark") for i in range(2)]
    A["rock"] = [rock_mesh("Asset_Rock_%d" % i, P, size=1.0 + i * 0.7, seed=i + 1) for i in range(4)]
    A["rock_warm"] = [rock_mesh("Asset_RockWarm_%d" % i, P, size=1.2 + i * 0.9, seed=i + 20, m="rock_warm") for i in range(3)]
    A["rock_dark"] = [rock_mesh("Asset_RockDark_%d" % i, P, size=1.0 + i * 0.8, seed=i + 40, m="rock_dark", flat=0.8) for i in range(3)]
    A["fuel_red"] = fuel_pump_mesh("Asset_FuelPump_Red", P, "red")
    A["fuel_blue"] = fuel_pump_mesh("Asset_FuelPump_Blue", P, "blue")
    A["fuel_yellow"] = fuel_pump_mesh("Asset_FuelPump_Yellow", P, "yellow")
    A["barrel"] = barrel_mesh("Asset_Barrel_Blue", P, "blue")
    A["barrel_red"] = barrel_mesh("Asset_Barrel_Red", P, "red")
    A["barrel_wood"] = barrel_mesh("Asset_Barrel_Wood", P, "wood")
    A["crate"] = crate_mesh("Asset_Crate", P)
    A["fish_crate"] = fish_crate_mesh("Asset_FishCrate", P)
    A["lamp"] = lamp_post_mesh("Asset_LampPost", P)
    A["bollard"] = bollard_mesh("Asset_Bollard", P)
    A["life_ring"] = life_ring_mesh("Asset_LifeRingStand", P)
    A["net"] = net_mesh("Asset_NetRack", P)
    A["bench"] = bench_mesh("Asset_Bench", P)
    A["chair"] = deck_chair_mesh("Asset_DeckChair", P)
    A["umbrella"] = umbrella_mesh("Asset_Umbrella", P)
    # library objects so the meshes are visible/browsable in the outliner (collection excluded from view layer)
    for i, (k, v) in enumerate(A.items()):
        for j, me in enumerate(v if isinstance(v, list) else [v]):
            o = bpy.data.objects.new(me.name, me)
            o.location = (i * 4.0, j * 4.0 - 400, 0)
            lib.objects.link(o)
    return A


def exclude_library():
    from fg_lib import scene
    sc = scene()
    for vl in sc.view_layers:
        lc = vl.layer_collection.children.get("00_Assets_Library")
        if lc:
            lc.exclude = True
