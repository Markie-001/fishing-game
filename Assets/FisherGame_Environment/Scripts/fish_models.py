"""Low-poly fish model generator. Every fish in fish_data.FISH becomes one mesh.

A fish is built along +X (nose at +0.5, tail base at -0.5, length 1), then scaled to the species' average length
in metres and turned so the head points to Blender -Y (Unity +Z with the project's FBX settings).
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler
from fg_lib import MB, mat
import fish_data as D

# ---------------------------------------------------------------- body plans (relative to length 1)

PLANS = {
    "fusiform":  dict(hmax=0.12, wmax=0.09, tp=0.35, a=0.75, pr=0.20),
    "slim":      dict(hmax=0.075, wmax=0.06, tp=0.35, a=0.9, pr=0.18),
    "compressed": dict(hmax=0.20, wmax=0.06, tp=0.40, a=0.6, pr=0.18),
    "deep":      dict(hmax=0.32, wmax=0.05, tp=0.45, a=0.55, pr=0.16),
    "flat":      dict(hmax=0.08, wmax=0.14, tp=0.25, a=0.45, pr=0.20),
    "eel":       dict(hmax=0.05, wmax=0.045, tp=0.12, a=0.6, pr=0.08, eel=True),
    "round":     dict(hmax=0.28, wmax=0.26, tp=0.45, a=0.5, pr=0.10),
    "box":       dict(hmax=0.20, wmax=0.19, tp=0.45, a=0.4, pr=0.10, n=4.0),
    "shark":     dict(hmax=0.11, wmax=0.10, tp=0.33, a=1.2, pr=0.14),
    "flatfish":  dict(hmax=0.30, wmax=0.04, tp=0.45, a=0.6, pr=0.15, lie=True),
    "ray":       dict(hmax=0.05, wmax=0.55, tp=0.42, a=0.6, pr=0.06, ray=True),
    "angler":    dict(hmax=0.22, wmax=0.26, tp=0.25, a=0.4, pr=0.12),
    "diamond":   dict(hmax=0.30, wmax=0.07, tp=0.45, a=1.0, pr=0.12, lin=True),
    "blenny":    dict(hmax=0.10, wmax=0.08, tp=0.20, a=0.35, pr=0.30),
    "pipefish":  dict(hmax=0.025, wmax=0.022, tp=0.15, a=0.5, pr=0.3, eel=True),
    "lookdown":  dict(hmax=0.30, wmax=0.05, tp=0.15, a=0.25, pr=0.10),
    "mahi":      dict(hmax=0.14, wmax=0.07, tp=0.12, a=0.30, pr=0.14),
    "hatchet":   dict(hmax=0.32, wmax=0.05, tp=0.30, a=0.5, pr=0.12, keel=True),
    "gulper":    dict(hmax=0.10, wmax=0.06, tp=0.08, a=0.5, pr=0.03, eel=True),
    "sturgeon":  dict(hmax=0.08, wmax=0.09, tp=0.35, a=1.3, pr=0.15),
    "chimaera":  dict(hmax=0.14, wmax=0.09, tp=0.22, a=0.5, pr=0.04),
    "oarfish":   dict(hmax=0.05, wmax=0.012, tp=0.08, a=0.5, pr=0.15, eel=True),
    "mola":      dict(hmax=0.45, wmax=0.09, tp=0.50, a=0.5, pr=0.75),
    "serpent":   dict(hmax=0.05, wmax=0.05, tp=0.10, a=0.6, pr=0.12, eel=True, wave=0.06),
    "coin":      dict(hmax=0.48, wmax=0.06, tp=0.50, a=0.5, pr=0.30),
    "seahorse":  dict(hmax=0.07, wmax=0.06, tp=0.3, a=0.6, pr=0.2),     # built by Fish.seahorse()
    "seadragon": dict(hmax=0.04, wmax=0.04, tp=0.3, a=0.6, pr=0.2),
}


def hexcol(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def cmat(h):
    return mat("M_Fish_%s" % h.lstrip("#").lower(), hexcol(h), 0.55)


def gmat(h):
    return mat("M_FishGlow_%s" % h.lstrip("#").lower(), hexcol(h), 0.3, emit=hexcol(h), emit_strength=5.0)


def glass_mat(h):
    return mat("M_FishGlass_%s" % h.lstrip("#").lower(), hexcol(h), 0.05, alpha=0.4)


EYE = None
PUPIL = None


def profile(t, p):
    """Body size factor 0..1 at t (0 = nose, 1 = tail base)."""
    tp, a, pr = p["tp"], p["a"], p["pr"]
    if p.get("eel"):
        if t < tp:
            return max(0.25, (1 - (1 - t / tp) ** 2) ** a)
        return 1 - (1 - pr) * ((t - tp) / (1 - tp)) ** 2.5
    if p.get("lin"):
        return max(0.08, t / tp) if t < tp else 1 - (1 - pr) * (t - tp) / (1 - tp)
    if t < tp:
        return max(0.06, (1 - (1 - t / tp) ** 2) ** a)
    return 1 - (1 - pr) * ((t - tp) / (1 - tp)) ** 1.5


def ray_width(t, p, rnd_round):
    tp = p["tp"]
    diamond = (t / tp) if t < tp else max(0.0, 1 - (t - tp) / (1 - tp)) ** 1.1
    disc = math.sqrt(max(0.0, 1 - ((t - 0.5) / 0.5) ** 2))
    return p["wmax"] * (diamond * (1 - rnd_round) + disc * rnd_round)


class Fish:
    """Builds one fish into an MB in normalised units."""

    def __init__(self, f):
        self.f = f
        lk = dict(f["look"])
        if f["plan"] == "angler" and "big_mouth" not in lk["extras"]:
            lk["extras"] = lk["extras"] + ["big_mouth"]          # every angler gets the huge gaping mouth
        self.lk = lk
        self.p = dict(PLANS[f["plan"]])
        for k, v in lk["shape"].items():
            self.p[k] = v
        self.rnd = random.Random(f["id"] * 7919)
        back, belly, fin, accent = lk["colors"]
        glass = lk["pattern"] == "glass"
        self.M = {
            "back": glass_mat(back) if glass else cmat(back),
            "belly": glass_mat(belly) if glass else cmat(belly),
            "fin": glass_mat(fin) if glass else cmat(fin),
            "accent": cmat(accent),
            "glow": gmat(accent),
        }
        if lk["pattern"] in ("glow_fins",):
            self.M["fin"] = gmat(fin)
        if lk["pattern"] == "coin":
            self.M["back"] = mat("M_Fish_Gold", hexcol(back), 0.25, metal=1.0)
            self.M["accent"] = mat("M_Fish_GoldDark", hexcol(accent), 0.3, metal=1.0)
        self.mb = MB()
        self.N, self.R = 8, 6
        self.rings = []

    # ---------------- body dimensions
    def dims(self, t):
        p = self.p
        s = profile(t, p)
        if p.get("ray"):
            w = ray_width(t, p, p.get("round", 0.5))
            h = p["hmax"] * max(0.15, s)
        else:
            h, w = p["hmax"] * s, p["wmax"] * s
        c = 0.0
        if p.get("wave"):
            c = p["wave"] * math.sin(t * math.pi * 4)
        if p.get("keel"):
            c = -0.15 * h
        return h, w, c

    def x(self, t):
        return 0.5 - t

    # ---------------- body
    def body(self):
        mb, N, R = self.mb, self.N, self.R
        n = self.p.get("n", 2.0)
        ts = [(i / (N - 1)) ** 1.15 for i in range(N)]
        ts[0] = 0.0
        pts, faces, meta = [], [], []
        nose_h, _, nose_c = self.dims(0.0)
        pts.append((0.5, 0.0, nose_c + nose_h * 0.1))
        for i, t in enumerate(ts[1:], 1):
            h, w, c = self.dims(t)
            for j in range(R):
                ang = 2 * math.pi * j / R + math.pi / R
                ca, sa = math.cos(ang), math.sin(ang)
                y = w * math.copysign(abs(ca) ** (2 / n), ca)
                z = c + h * math.copysign(abs(sa) ** (2 / n), sa)
                pts.append((self.x(t), y, z))
        tail_c = len(pts)
        h, w, c = self.dims(1.0)
        pts.append((self.x(1.0) - 0.004, 0.0, c))
        ring = lambda i: 1 + (i - 1) * R
        for j in range(R):
            faces.append((0, ring(1) + (j + 1) % R, ring(1) + j))
            meta.append((0.02, j))
        for i in range(1, N - 1):
            for j in range(R):
                a, b = ring(i) + j, ring(i) + (j + 1) % R
                faces.append((a, b, b + R, a + R))
                meta.append(((ts[i] + ts[i + 1]) / 2, j))
        last = ring(N - 1)
        for j in range(R):
            faces.append((last + j, last + (j + 1) % R, tail_c))
            meta.append((1.0, j))
        bm = mb.bm
        vs = [bm.verts.new(p) for p in pts]
        for fi, (face, (t, j)) in enumerate(zip(faces, meta)):
            fc = bm.faces.new([vs[k] for k in face])
            fc.material_index = mb._mi(self.pattern_mat(t, j, fi))
        self.body_verts = vs

    def pattern_mat(self, t, j, fi):
        R = self.R
        ang = 2 * math.pi * (j + 0.5) / R + math.pi / R
        up = math.sin(ang)                        # +1 top, -1 bottom
        pat = self.lk["pattern"]
        M, rnd = self.M, self.rnd
        base = M["back"] if up > -0.25 else M["belly"]
        side = abs(up) < 0.35
        if pat in ("plain", "glass", "photophores", "glow_fins", "tail_accent"):
            return M["back"] if up > -0.55 else M["belly"]
        if pat == "gradient":
            return base
        if pat == "spots":
            return M["accent"] if (up > -0.3 and rnd.random() < 0.22 and 0.05 < t < 0.95) else base
        if pat == "big_spots":
            return M["belly"] if (up < 0.1 and rnd.random() < 0.45) else M["back"]
        if pat == "mottled":
            r = rnd.random()
            return M["accent"] if r < 0.25 else (M["fin"] if r < 0.4 else base)
        if pat in ("stripes_h", "stripe_tail", "stripe_yellow"):
            return M["accent"] if (side and 0.1 < t < 0.98) else base
        if pat == "bands":
            return M["accent"] if (0.1 < t < 0.95 and int(t * 7) % 2 == 1) else base
        if pat == "bars":
            return M["accent"] if (up > -0.1 and 0.1 < t < 0.95 and int(t * 7) % 2 == 1) else base
        if pat == "wavy":
            return M["accent"] if (up > 0.1 and (int(t * 14) + j) % 2 == 0) else base
        if pat == "spot_row":
            return M["accent"] if (side and up > 0 and 0.2 < t < 0.7 and int(t * 12) % 2 == 0) else base
        if pat == "head_band":
            return M["accent"] if (t < 0.2 and up > -0.2) else base
        if pat == "scales":
            return M["accent"] if (up > -0.3 and (int(t * 14) + j) % 2 == 0) else base
        if pat == "diag":
            return M["accent"] if (up > -0.2 and (int(t * 12) + j) % 3 == 0) else base
        if pat == "swirl":
            return M["accent"] if ((int(t * 10) * 2 + j) % 4 in (0, 1)) else base
        if pat == "fin_tips":
            return base
        if pat == "manta":
            return M["belly"] if up < 0 else (M["accent"] if (0.25 < t < 0.45 and side) else M["back"])
        if pat == "belly_plates":
            return M["accent"] if (up < -0.3 and int(t * 16) % 2 == 0) else M["back"]
        if pat == "stars":
            return M["back"] if up > -0.2 else M["belly"]
        if pat == "coin":
            return M["back"]
        return base

    # ---------------- fins
    def fin(self, pts, m, thick=0.006, normal=Vector((0, 1, 0))):
        """Thin extruded polygon (pts in order)."""
        n = len(pts)
        off = normal * (thick / 2)
        allp = [Vector(p) + off for p in pts] + [Vector(p) - off for p in pts]
        faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + \
                [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        self.mb.poly(allp, faces, m)

    def top(self, t):
        h, w, c = self.dims(t)
        return c + h * 0.9

    def bottom(self, t):
        h, w, c = self.dims(t)
        return c - h * 0.9

    def along_fin(self, t0, t1, height, shape="tri", sweep=0.3, side=1, m=None, spiky=False, k=3):
        """Dorsal (side=1) or anal (side=-1) fin along the body."""
        m = m or self.fin_mat("dorsal")
        base, topp = [], []
        for i in range(k + 1):
            u = i / k
            t = t0 + (t1 - t0) * u
            z = self.top(t) if side > 0 else self.bottom(t)
            base.append((self.x(t), 0, z))
            if shape == "tri":
                hp = (u / 0.3) if u < 0.3 else max(0.08, 1 - (u - 0.3) / 0.7)
            elif shape == "round":
                hp = math.sin(math.pi * min(1, u * 1.02)) ** 0.7 + 0.05
            elif shape == "flat":
                hp = min(1, u / 0.15, (1 - u) / 0.15 + 0.2)
            elif shape == "sickle":
                hp = (u / 0.15) if u < 0.15 else max(0.05, (1 - (u - 0.15) / 0.85) ** 2.2)
            elif shape == "front":
                hp = 1.0 - u * 0.85
            else:
                hp = 1.0
            if spiky and i % 2 == 1:
                hp *= 0.55
            hh = height * hp
            topp.append((self.x(t) - sweep * hh, 0, z + side * hh))
        self.fin(base + topp[::-1], m)

    def fin_mat(self, which):
        pat = self.lk["pattern"]
        if pat in ("tail_accent", "stripe_tail", "stripe_yellow") and which == "tail":
            return self.M["accent"]
        if pat == "fin_tips" and which in ("tail", "dorsal"):
            return self.M["accent"]
        if pat == "glow_fins":
            return self.M["fin"]
        return self.M["fin"]

    def dorsal(self):
        d = self.lk["dorsal"]
        H = self.p["hmax"]
        F = lambda *a, **k: self.along_fin(*a, **k)
        acc = self.M["accent"]
        if d == "single":
            F(0.33, 0.6, H * 0.8, "tri")
        elif d == "single_front":
            F(0.22, 0.42, H * 0.8, "tri")
        elif d == "double":
            F(0.28, 0.46, H * 0.75, "tri", spiky=True)
            F(0.52, 0.7, H * 0.55, "tri")
        elif d == "double_far":
            F(0.3, 0.4, H * 0.8, "tri")
            F(0.72, 0.82, H * 0.7, "tri")
        elif d == "triple":
            F(0.25, 0.4, H * 0.6, "round")
            F(0.44, 0.62, H * 0.55, "round")
            F(0.66, 0.82, H * 0.5, "round")
        elif d in ("spiny", "spiny_black"):
            m = acc if d == "spiny_black" else None
            F(0.24, 0.5, H * 0.75, "flat", spiky=True, k=8, m=m)
            F(0.5, 0.78, H * 0.6, "round")
        elif d == "long":
            F(0.18, 0.97, H * 0.45, "flat", sweep=0.15, k=10)
        elif d == "long_low":
            F(0.2, 0.75, H * 0.35, "front", k=8)
        elif d == "long_tall":
            F(0.06, 0.92, H * 0.85, "front", sweep=0.25, k=12)
        elif d == "small":
            F(0.55, 0.72, H * 0.45, "round")
        elif d == "small_rear":
            F(0.65, 0.75, H * 1.0, "tri")
            F(0.8, 0.9, H * 0.8, "tri")
        elif d == "rear":
            F(0.68, 0.86, H * 0.7, "tri")
        elif d == "sail":
            F(0.12, 0.72, H * 3.0, "round", sweep=0.15, k=12, spiky=True)
        elif d == "sail_small":
            F(0.25, 0.7, H * 1.3, "round", spiky=True, k=8)
        elif d in ("filament", "filament_short"):
            F(0.25, 0.8, H * 0.6, "flat", k=8)
            L = 0.35 if d == "filament" else 0.15
            t = 0.7
            self.mb.cyl_between((self.x(t), 0, self.top(t) + H * 0.5), (self.x(t) - L, 0, self.top(t) + H * 0.9), 0.006, 0.002, self.fin_mat("dorsal"), seg=4)
        elif d == "spine":
            F(0.3, 0.4, H * 1.1, "front", sweep=0.4)
            F(0.7, 0.85, H * 0.35, "round")
        elif d == "trigger":
            F(0.25, 0.33, H * 0.6, "front", sweep=0.4)
            F(0.45, 0.85, H * 0.5, "front", sweep=0.4)
        elif d in ("shark", "shark_tall", "shark_low"):
            hh = {"shark": 1.2, "shark_tall": 2.0, "shark_low": 0.7}[d]
            F(0.32, 0.5, H * hh, "sickle", sweep=0.6)
            F(0.72, 0.8, H * hh * 0.35, "sickle", sweep=0.4)
        elif d == "sickle":
            F(0.3, 0.45, H * 1.0, "sickle", sweep=0.5)
            F(0.55, 0.66, H * 0.8, "sickle", sweep=0.8)
        elif d == "sickle_tall":
            F(0.2, 0.42, H * 2.0, "sickle", sweep=0.4)
        elif d == "hump":
            self.mb.ico(H * 0.4, (self.x(0.45), 0, self.top(0.45)), self.M["back"], scale=(1.5, 0.6, 0.7))
        elif d == "lobe":
            F(0.35, 0.55, H * 1.2, "sickle", sweep=0.5)
        elif d == "lion":
            for k in range(10):
                t = 0.15 + k * 0.06
                hh = H * (1.6 - abs(k - 3) * 0.1)
                col = self.M["accent"] if k % 2 else self.M["back"]
                self.mb.cyl_between((self.x(t), 0, self.top(t)), (self.x(t) - hh * 0.35, 0, self.top(t) + hh), 0.006, 0.002, col, seg=4)
            F(0.15, 0.8, H * 0.35, "flat", k=8)
        elif d == "crest":
            F(0.02, 0.98, H * 0.9, "flat", sweep=0.05, k=16, m=self.M["accent"])
            for k in range(6):
                self.mb.cyl_between((0.47 - k * 0.012, 0, self.top(0.03)), (0.5 - k * 0.03, 0, self.top(0.03) + H * (3.0 - k * 0.3)),
                                    0.004, 0.001, self.M["accent"], seg=4)
        elif d == "mola":
            F(0.62, 0.8, H * 1.0, "sickle", sweep=0.35)
        elif d == "crown":
            F(0.3, 0.55, H * 0.8, "sickle", sweep=0.4)
        elif d == "mane":
            for k in range(14):
                t = 0.06 + k * 0.065
                hh = self.p["hmax"] * 1.4
                self.mb.cyl(hh * 0.25, 0.0, hh, (self.x(t), 0, self.top(t) + hh * 0.4), self.M["accent"], rot=(0, -0.4, 0), seg=4)
        elif d == "crystal":
            for k in range(5):
                t = 0.25 + k * 0.11
                hh = H * (0.9 - abs(k - 2) * 0.15)
                self.mb.cyl(hh * 0.18, 0.0, hh, (self.x(t), 0, self.top(t) + hh * 0.45), self.M["glow"], rot=(0, -0.3, 0), seg=5)

    def anal(self):
        a = self.lk["anal"]
        H = self.p["hmax"]
        F = lambda *a_, **k: self.along_fin(*a_, side=-1, **k)
        if a == "std":
            F(0.6, 0.78, H * 0.5, "tri", m=self.fin_mat("anal"))
        elif a == "double":
            F(0.48, 0.62, H * 0.45, "round", m=self.fin_mat("anal"))
            F(0.66, 0.8, H * 0.4, "round", m=self.fin_mat("anal"))
        elif a == "long":
            F(0.3, 0.97, H * 0.4, "flat", sweep=0.15, k=10, m=self.fin_mat("anal"))
        elif a == "tall":
            F(0.5, 0.85, H * 0.5, "front", sweep=0.4, m=self.fin_mat("anal"))
        elif a == "sickle":
            F(0.55, 0.68, H * 0.9, "sickle", sweep=0.6, m=self.fin_mat("anal"))
        elif a == "shark":
            F(0.7, 0.78, H * 0.4, "sickle", sweep=0.5, m=self.fin_mat("anal"))
        elif a == "rear":
            F(0.68, 0.86, H * 0.6, "tri", m=self.fin_mat("anal"))
        elif a == "filament":
            F(0.5, 0.8, H * 0.6, "flat", k=8, m=self.fin_mat("anal"))
            t = 0.75
            self.mb.cyl_between((self.x(t), 0, self.bottom(t) - H * 0.5), (self.x(t) - 0.3, 0, self.bottom(t) - H * 0.9), 0.006, 0.002, self.fin_mat("anal"), seg=4)
        elif a == "lobe":
            F(0.62, 0.78, H * 0.9, "sickle", sweep=0.5, m=self.fin_mat("anal"))
        elif a == "small":
            F(0.6, 0.72, H * 0.4, "round", m=self.fin_mat("anal"))
        elif a == "mola":
            F(0.62, 0.8, H * 1.0, "sickle", sweep=0.35, m=self.fin_mat("anal"))

    def tail(self):
        tl = self.lk["tail"]
        if tl == "none":
            return
        h, w, c = self.dims(1.0)
        H = self.p["hmax"]
        x0 = self.x(1.0) + 0.01
        S = max(H * 1.3, 0.09)
        shapes = {
            "forked": [(0, .25), (1.0, 1.0), (.55, 0), (1.0, -1.0), (0, -.25)],
            "forked_low": [(0, .25), (.8, .8), (.5, 0), (1.2, -1.15), (0, -.25)],
            "lunate": [(0, .2), (.5, .55), (.95, 1.15), (.62, .25), (.55, 0), (.62, -.25), (.95, -1.15), (.5, -.55), (0, -.2)],
            "truncate": [(0, .3), (.75, .85), (.8, 0), (.75, -.85), (0, -.3)],
            "heterocercal": [(0, .2), (1.3, 1.0), (.95, .2), (.6, -.1), (.75, -.55), (0, -.2)],
            "thresher": [(0, .2), (3.2, 1.3), (3.0, 1.1), (.6, -.05), (.65, -.5), (0, -.2)],
            "eel": [(0, .4), (.45, 0), (0, -.4)],
            "paddle": [(0, .3), (.35, .5), (.5, 0), (.35, -.5), (0, -.3)],
            "diphycercal": [(0, .35), (.6, .75), (.5, .25), (.9, .18), (1.05, 0), (.9, -.18), (.5, -.25), (.6, -.75), (0, -.35)],
            "fin_tip": [(0, .2), (.6, .9), (.9, 0), (.6, -.9), (0, -.2)],
        }
        m = self.fin_mat("tail")
        if tl in ("rounded", "fan"):
            r = 0.8 if tl == "rounded" else 0.6
            pts = [(0, .25)] + [(0.1 + r * math.cos(a), r * math.sin(a)) for a in [math.radians(70 - i * 20) for i in range(8)]] + [(0, -.25)]
        elif tl == "lunate_big":
            pts = [(x * 1.35, z * 1.35) for x, z in shapes["lunate"]]
        elif tl == "clavus":
            S = H * 0.95
            pts = [(0, 1.0), (.18, .9), (.12, .6), (.2, .3), (.12, 0), (.2, -.3), (.12, -.6), (.18, -.9), (0, -1.0)]
        elif tl in ("whip", "whip_short", "whip_glow"):
            L = {"whip": 0.7, "whip_short": 0.3, "whip_glow": 0.5}[tl]
            end = (x0 - L, 0, c)
            self.mb.cyl_between((x0 + 0.02, 0, c), end, max(h, 0.01) * 0.6, 0.002, self.M["back"], seg=5)
            if tl == "whip_glow":
                self.mb.ico(0.015, end, self.M["glow"])
            return
        else:
            pts = shapes[tl]
        self.fin([(x0 - px * S, 0, c + pz * S) for px, pz in pts], m)

    def pectorals(self):
        pc = self.lk["pect"]
        if pc == "none" or self.p.get("ray"):
            return
        H = self.p["hmax"]
        t = 0.22 if self.f["plan"] != "shark" else 0.3
        h, w, c = self.dims(t)
        size = {"std": 0.09, "small": 0.05, "big": 0.14, "wing": 0.26, "wing_huge": 0.45, "fan": 0.3, "sickle": 0.22,
                "legs": 0.07, "lobe": 0.12}[pc]
        if self.f["plan"] == "shark" and pc == "std":
            size = 0.18
        size *= max(0.7, min(1.6, H / 0.12)) if pc in ("std", "small", "big") else 1.0
        m = self.fin_mat("pect")
        if pc == "fan":
            m = self.M["accent"]
        for s in (-1, 1):
            root = Vector((self.x(t), s * w * 0.85, c - h * 0.3))
            if pc == "legs":
                a = root + Vector((0.02, s * 0.06, -h * 0.9))
                self.mb.cyl_between(root, a, 0.018, 0.014, self.M["back"], seg=5)
                self.mb.ico(0.02, a, self.M["fin"], scale=(1.5, 1.2, 0.5))
                continue
            if pc == "lobe":
                a = root + Vector((-0.04, s * 0.05, -0.03))
                self.mb.cyl_between(root, a, 0.02, 0.016, self.M["back"], seg=5)
                root = a
            out = Vector((0, s, 0))
            back_dir = Vector((-1, 0, 0))
            spread = 0.55 if pc in ("wing", "wing_huge") else 0.35
            if pc in ("std", "small", "big", "lobe", "sickle") and self.f["plan"] == "shark":
                spread = 0.45
            down = Vector((0, 0, -0.35)) if pc not in ("wing", "wing_huge") else Vector((0, 0, -0.05))
            d1 = (back_dir * (1 - spread) + out * spread + down).normalized()
            wid = size * (0.45 if pc != "sickle" else 0.2)
            perp = Vector((1, 0, 0)).cross(d1).normalized() if abs(d1.x) < 0.9 else Vector((0, 0, 1))
            tip = root + d1 * size
            pts = [root + perp * wid * 0.3, root + d1 * size * 0.5 + perp * wid, tip, root + d1 * size * 0.6 - perp * wid * 0.5, root - perp * wid * 0.3]
            self.fin(pts, m, normal=perp.cross(d1).normalized())

    # ---------------- head details
    def eyes(self):
        if "hammer" in self.lk["extras"]:
            return
        plan = self.f["plan"]
        te = 0.1 if plan not in ("angler", "lookdown", "mahi", "deep", "coin") else 0.14
        if plan in ("eel", "pipefish", "oarfish", "serpent", "gulper"):
            te = 0.04
        h, w, c = self.dims(te)
        r = max(0.012, min(0.05, 0.02 * self.lk["eye"] * (1 + self.p["hmax"])))
        if plan in ("eel", "pipefish", "oarfish", "serpent"):
            r = min(r, self.p["hmax"] * 0.45)
        positions = []
        if plan == "flatfish":
            positions = [(self.x(te), w + r * 0.2, c + h * 0.25), (self.x(te + 0.06), w + r * 0.2, c - h * 0.1)]
            normals = [Vector((0, 1, 0))] * 2
        elif "eyes_up" in self.lk["extras"] or plan == "ray":
            positions = [(self.x(te + 0.03), s * w * 0.4, c + h * 0.9) for s in (-1, 1)]
            normals = [Vector((0, 0, 1))] * 2
        else:
            positions = [(self.x(te), s * w * 0.82, c + h * 0.3) for s in (-1, 1)]
            normals = [Vector((0, s, 0.2)).normalized() for s in (-1, 1)]
        for pos, nrm in zip(positions, normals):
            # flat disc eye: white rim, black outer cap as pupil (12 verts instead of two spheres)
            p = Vector(pos)
            rot = nrm.to_track_quat('Z', 'Y').to_euler()
            vs = self.mb.cyl(r, r * 0.7, r * 0.5, p, PUPIL, rot=rot, seg=6)
            axis = nrm.normalized()
            for fc in {f for v in vs for f in v.link_faces}:
                if abs(fc.normal.dot(axis)) < 0.9:
                    fc.material_index = self.mb._mi(EYE)

    def mouth(self):
        if self.f["plan"] in ("seahorse", "seadragon", "ray"):
            return
        h, w, c = self.dims(0.03)
        self.mb.box((0.02, max(w, 0.01) * 1.4, max(0.003, self.p["hmax"] * 0.06)), (0.49, 0, c - h * 0.2), PUPIL)

    # ---------------- extras
    def extras(self):
        ex = self.lk["extras"]
        mb, M, H = self.mb, self.M, self.p["hmax"]
        rnd = random.Random(self.f["id"])
        hN, wN, cN = self.dims(0.04)
        nose = Vector((0.5, 0, cN))
        for e in ex:
            if e in ("barbels", "chin_barbel", "chin_barbels"):
                n = {"barbels": 4, "chin_barbel": 1, "chin_barbels": 2}[e]
                for k in range(n):
                    s = 0 if n == 1 else (-1 if k % 2 else 1)
                    y = s * (0.015 + 0.02 * (k // 2))
                    root = Vector((0.47, y, cN - hN * 0.5))
                    end = root + Vector((0.08 if e == "barbels" else 0.0, y * 2.5, -0.07 - 0.02 * (k // 2)))
                    mb.cyl_between(root, end, 0.004, 0.0015, M["fin"], seg=4)
            elif e == "barb":
                c = self.dims(1.0)[2]
                mb.cyl(0.008, 0.0, 0.06, (self.x(1.0) - 0.2, 0, c + 0.01), M["accent"], rot=(0, -math.pi / 2, 0), seg=4)
            elif e == "barnacles":
                for k in range(6):
                    t = rnd.uniform(0.1, 0.8)
                    h, w, c = self.dims(t)
                    mb.ico(0.012 + rnd.random() * 0.01, (self.x(t), rnd.uniform(-w, w) * 0.8, c + h * rnd.uniform(0.4, 0.95)),
                           cmat("#d8d4c8") if k % 2 else cmat("#8a887c"), scale=(1, 1, 0.6))
            elif e == "beak":
                mb.cyl_between(nose + Vector((0, 0, 0.004)), nose + Vector((0.22, 0, 0.004)), 0.01, 0.002, M["back"], seg=5)
                mb.cyl_between(nose - Vector((0, 0, 0.006)), nose + Vector((0.26, 0, -0.006)), 0.01, 0.002, M["back"], seg=5)
            elif e == "beak_parrot":
                mb.ico(hN * 1.2 + 0.01, nose + Vector((0.01, 0, -0.005)), cmat("#f0f0e0"), scale=(0.8, 0.9, 0.9))
            elif e == "big_mouth":
                big = {"gulper": 0.22, "angler": 0.16}.get(self.f["plan"], 0.1)
                mb.box((big * 0.5, max(wN, 0.03) * 2.2, 0.01), nose + Vector((0.0, 0, -big * 0.35)), M["back"], rot=(0, -0.5, 0))
                mb.box((big * 0.5, max(wN, 0.03) * 2.2, 0.01), nose + Vector((0.0, 0, big * 0.15)), M["back"], rot=(0, 0.25, 0))
                mb.ico(big * 0.35, nose + Vector((-0.02, 0, -big * 0.1)), PUPIL, scale=(0.5, 1.0, 1.0))
                if self.f["plan"] != "gulper":
                    mb.box((0.01, wN * 2.1, big * 0.25), nose + Vector((0.005, 0, -big * 0.1)), M["accent"])
            elif e == "bill":
                mb.cyl_between(nose, nose + Vector((0.4, 0, 0.01)), H * 0.25, 0.002, M["back"], seg=6)
            elif e == "cephalic":
                for s in (-1, 1):
                    mb.box((0.12, 0.03, 0.01), nose + Vector((0.03, s * 0.12, 0.0)), M["back"], rot=(0.4 * s, 0, 0.25 * s))
            elif e == "crest":
                h, w, c = self.dims(0.08)
                self.fin([(0.44, 0, c + h * 0.9), (0.46, 0, c + h * 1.6), (0.43, 0, c + h * 1.3), (0.41, 0, c + h * 1.7), (0.38, 0, c + h * 0.9)], M["fin"])
            elif e == "crown":
                h, w, c = self.dims(0.12)
                for k in range(5):
                    a = math.radians(-30 + k * 15)
                    root = Vector((self.x(0.12), 0, c + h * 0.9))
                    mb.cyl_between(root, root + Vector((math.sin(a) * 0.06, 0, 0.12 + 0.02 * (2 - abs(k - 2)))), 0.006, 0.001, M["accent"], seg=4)
            elif e == "crystals":
                for k in range(6):
                    t = rnd.uniform(0.2, 0.8)
                    h, w, c = self.dims(t)
                    s = rnd.choice((-1, 1))
                    mb.cyl(0.015, 0.0, 0.08, (self.x(t), s * w * 0.8, c + h * 0.2), M["glow"], rot=(s * 1.2, 0, rnd.random()), seg=5)
            elif e == "duck_bill":
                mb.ico(0.09, nose + Vector((0.07, 0, -0.01)), M["accent"], scale=(1.7, 1.4, 0.4))
            elif e == "eyespot":
                h, w, c = self.dims(0.45)
                for s in (-1, 1):
                    mb.ico(h * 0.18, (self.x(0.45), s * w * 0.95, c), M["accent"], scale=(1, 0.3, 1))
            elif e == "fangs":
                for k in range(4):
                    y = (-1 if k % 2 else 1) * 0.012
                    z = cN + (0.01 if k < 2 else -0.012)
                    mb.cyl(0.006, 0.0, 0.07, (0.48, y, z + (0.02 if k < 2 else -0.02)), cmat("#f0ece0"), rot=(0, math.pi if k >= 2 else 0, 0), seg=4)
            elif e == "finlets":
                for k in range(5):
                    t = 0.74 + k * 0.045
                    for side in (1, -1):
                        z = self.top(t) if side > 0 else self.bottom(t)
                        self.fin([(self.x(t), 0, z), (self.x(t) - 0.015, 0, z + side * 0.02), (self.x(t) - 0.02, 0, z)], M["accent"])
            elif e == "gills":
                for k in range(4):
                    t = 0.17 + k * 0.025
                    h, w, c = self.dims(t)
                    for s in (-1, 1):
                        mb.box((0.004, 0.004, h * 0.6), (self.x(t), s * w * 0.95, c), PUPIL)
            elif e == "hammer":
                bar = 0.24
                mb.box((0.05, bar * 2, 0.025), (0.48, 0, cN), M["back"])
                for s in (-1, 1):
                    mb.ico(0.012, (0.48, s * bar, cN), EYE)
                    mb.ico(0.008, (0.48, s * (bar + 0.008), cN), PUPIL)
            elif e in ("horns", "horns_back"):
                h, w, c = self.dims(0.1)
                for s in (-1, 1):
                    if e == "horns":
                        mb.cyl(0.012, 0.0, 0.1, (self.x(0.1) + 0.04, s * w * 0.5, c + h * 0.85), M["back"], rot=(0, math.pi / 2 - 0.4, 0), seg=4)
                        mb.cyl(0.012, 0.0, 0.08, (self.x(0.95) - 0.03, s * self.dims(0.95)[1] * 0.6, self.bottom(0.95)), M["back"], rot=(0, -math.pi / 2 - 0.3, 0), seg=4)
                    else:
                        mb.cyl(0.012, 0.0, 0.09, (self.x(0.06) - 0.03, s * w * 0.5, c + h * 1.1), M["accent"], rot=(0, -math.pi / 2 + 0.6, s * 0.3), seg=4)
            elif e == "hump":
                h, w, c = self.dims(0.12)
                mb.ico(h * 0.7, (self.x(0.12), 0, c + h * 0.7), M["back"], scale=(1.0, 0.8, 0.8))
            elif e == "leaves":
                for k in range(9):
                    t = 0.15 + k * 0.09
                    s = 1 if k % 2 else -1
                    self.fin([(self.x(t), s * 0.01, self.top(t)), (self.x(t) - 0.03, s * 0.06, self.top(t) + 0.07), (self.x(t) - 0.07, s * 0.03, self.top(t) + 0.03)],
                             M["accent"], normal=Vector((0, 1, 0)))
            elif e in ("lure", "lure2", "lure_small"):
                h, w, c = self.dims(0.08)
                L = {"lure": 0.2, "lure2": 0.13, "lure_small": 0.07}[e]
                y = 0.03 if e == "lure2" else 0.0
                a = Vector((self.x(0.08), y, c + h * 0.9))
                b = a + Vector((0.04, 0, L * 0.8))
                d = b + Vector((L * 0.6, 0, -L * 0.15))
                mb.cyl_between(a, b, 0.004, 0.003, M["back"], seg=4)
                mb.cyl_between(b, d, 0.003, 0.002, M["back"], seg=4)
                mb.ico(0.015 if e != "lure_small" else 0.008, d, M["glow"], sub=1)
            elif e == "nostrils":
                for s in (-1, 1):
                    mb.cyl(0.006, 0.012, 0.025, (0.5, s * 0.01, cN + 0.01), M["accent"], rot=(0, math.pi / 2, 0), seg=5)
            elif e == "photophores":
                for k in range(7):
                    t = 0.12 + k * 0.11
                    h, w, c = self.dims(t)
                    for s in (-1, 1):
                        mb.ico(max(0.004, h * 0.08), (self.x(t), s * w * 0.6, c - h * 0.8), M["glow"])
            elif e in ("scutes", "scutes_side"):
                rows = [(0.0, 1.0)] if e == "scutes_side" else [(1.0, 0.0), (0.7, 0.75), (-0.3, 0.95)]
                for k in range(9):
                    t = 0.15 + k * 0.08 if e == "scutes" else 0.5 + k * 0.05
                    h, w, c = self.dims(t)
                    for zf, yf in rows:
                        for s in ((-1, 1) if yf else (1,)):
                            pos = (self.x(t), s * w * yf * 1.0, c + h * zf * 1.0)
                            mb.ico(max(0.006, h * 0.15), pos, M["accent"], scale=(1.3, 0.7, 0.7), sub=1)
            elif e == "skeleton":
                bone = gmat("#e8fff8")
                mb.cyl_between((0.42, 0, 0), (-0.48, 0, 0), 0.006, 0.004, bone, seg=4)
                for k in range(10):
                    t = 0.15 + k * 0.07
                    h, w, c = self.dims(t)
                    mb.cyl_between((self.x(t), 0, c), (self.x(t) - 0.02, 0, c + h * 0.75), 0.002, 0.001, bone, seg=3)
                    mb.cyl_between((self.x(t), 0, c), (self.x(t) - 0.02, 0, c - h * 0.7), 0.002, 0.001, bone, seg=3)
            elif e == "snout_eagle":
                mb.ico(0.06, nose + Vector((0.04, 0, -0.005)), M["back"], scale=(1.5, 1.0, 0.5))
            elif e == "spikes":
                for k in range(16):
                    t = rnd.uniform(0.1, 0.85)
                    a = rnd.uniform(0, 2 * math.pi)
                    h, w, c = self.dims(t)
                    n = Vector((0, math.cos(a), math.sin(a)))
                    base = Vector((self.x(t), w * math.cos(a), c + h * math.sin(a)))
                    mb.cyl_between(base, base + n * 0.05, 0.008, 0.0, M["accent"], seg=3)
            elif e == "tabs":
                for k in range(8):
                    t = rnd.uniform(0.05, 0.5)
                    h, w, c = self.dims(t)
                    s = rnd.choice((-1, 1))
                    mb.box((0.02, 0.004, 0.025), (self.x(t), s * w * 0.95, c + h * rnd.uniform(-0.2, 0.9)), M["fin"], rot=(s * 0.6, 0, rnd.random()))
            elif e == "tail_spot":
                h, w, c = self.dims(0.92)
                for s in (-1, 1):
                    mb.ico(max(0.01, h * 0.6), (self.x(0.92), s * w * 0.9, c), M["accent"], scale=(1, 0.3, 1))
            elif e == "teeth":
                for k in range(6):
                    y = -wN * 0.8 + k * wN * 0.32
                    for zs in (1, -1):
                        mb.cyl(0.005, 0.0, 0.018, (0.485, y, cN - hN * 0.2 + zs * 0.006), cmat("#f4f0e8"), rot=(0, 0 if zs < 0 else math.pi, 0), seg=3)
            elif e == "tentacles":
                for k in range(6):
                    a = math.radians(-60 + k * 24)
                    p = Vector((0.42, 0, cN - hN * 0.8))
                    d = Vector((0.06, math.sin(a) * 0.08, -0.06))
                    for j in range(3):
                        q = p + d + Vector((0, 0, -0.02 * j))
                        mb.cyl_between(p, q, 0.012 - j * 0.003, 0.009 - j * 0.003, M["back"], seg=5)
                        p = q
                        d = Vector((d.x * 0.6, d.y * 0.9, -0.05 + 0.03 * j))
                    mb.ico(0.008, p, M["glow"])
            elif e == "tubercles":
                for k in range(10):
                    t = 0.15 + (k % 5) * 0.15
                    h, w, c = self.dims(t)
                    zf = 0.75 if k < 5 else 0.1
                    for s in (-1, 1):
                        mb.ico(max(0.006, h * 0.1), (self.x(t), s * w * (0.6 if k < 5 else 0.97), c + h * zf), M["accent"], sub=1)
        if self.lk["pattern"] == "stars":
            for k in range(16):
                t = rnd.uniform(0.15, 0.8)
                h, w, c = self.dims(t)
                mb.ico(0.008, (self.x(t), rnd.uniform(-w, w) * 0.9, c + h * 0.95), M["glow"])
        if self.lk["pattern"] == "coin":
            mb.torus(self.p["hmax"] * 0.92, 0.012, (0.0, 0, 0), M["accent"], rot=(math.pi / 2, 0, 0), seg=20, rseg=4)
            for s in (-1, 1):
                mb.box((0.18, 0.004, 0.18), (0.0, s * self.p["wmax"] * 0.75, 0.0), M["accent"], rot=(0, math.pi / 4, 0))

    # ---------------- special builders
    def seahorse(self, dragon=False):
        """Upright seahorse/seadragon: curved spine of tapering segments, horse head, curled tail."""
        mb, M = self.mb, self.M
        pts = []
        for k in range(14):
            u = k / 13
            if dragon:
                pts.append(Vector((0.35 - u * 0.75, 0, 0.08 * math.sin(u * math.pi * 1.5))))
            else:
                z = 0.45 - u * 0.8
                x = 0.08 * math.sin(u * math.pi * 1.2) - (0.12 * (u - 0.75) / 0.25 if u > 0.75 else 0)
                pts.append(Vector((x, 0, z)))
        if not dragon:
            for k in range(6):
                a = k / 5 * math.pi * 1.4
                pts.append(pts[-1] + Vector((0.03 * math.cos(a + math.pi), 0, 0.03 * math.sin(a))))
        n = len(pts)
        for k in range(n - 1):
            r = (0.07 if not dragon else 0.04) * (1 - k / n) ** 0.8 + 0.006
            mm = M["accent"] if (k % 3 == 2) else M["back"]
            mb.cyl_between(pts[k], pts[k + 1] + (pts[k + 1] - pts[k]) * 0.1, r * 1.05, r * 0.92, mm, seg=6)
        head = pts[0] + Vector((0.02, 0, 0.05 if not dragon else 0.01))
        mb.ico(0.055 if not dragon else 0.04, head, M["back"], scale=(1.2, 0.8, 1.0))
        snout_end = head + (Vector((0.14, 0, -0.05)) if not dragon else Vector((0.16, 0, 0)))
        mb.cyl_between(head, snout_end, 0.018, 0.012, M["back"], seg=6)
        for s in (-1, 1):
            mb.ico(0.012, head + Vector((0.02, s * 0.038, 0.01)), EYE)
            mb.ico(0.007, head + Vector((0.025, s * 0.046, 0.01)), PUPIL)
        if not dragon:
            for k in range(4):
                mb.cyl(0.008, 0.0, 0.04, head + Vector((-0.02 + k * 0.012, 0, 0.05)), M["accent"], seg=4)
            mid = pts[5]
            self.fin([mid + Vector((-0.06, 0, 0.03)), mid + Vector((-0.12, 0, 0.0)), mid + Vector((-0.06, 0, -0.06))], M["fin"])
        else:
            for k in range(10):
                p = pts[1 + k]
                for s in (-1, 1):
                    self.fin([p, p + Vector((-0.02, s * 0.03, 0.08)), p + Vector((-0.06, s * 0.02, 0.05))], M["accent"])
                    if k % 2 == 0:
                        self.fin([p, p + Vector((-0.01, s * 0.04, -0.07)), p + Vector((-0.05, s * 0.02, -0.05))], M["accent"])

    def build(self):
        global EYE, PUPIL
        EYE = mat("M_FishEye", (0.95, 0.93, 0.85), 0.2)
        PUPIL = mat("M_FishPupil", (0.03, 0.03, 0.04), 0.2)
        plan = self.f["plan"]
        if plan in ("seahorse", "seadragon"):
            self.seahorse(dragon=(plan == "seadragon"))
        else:
            self.body()
            self.tail()
            self.dorsal()
            self.anal()
            self.pectorals()
            self.eyes()
            self.mouth()
            self.extras()
        if self.p.get("lie"):                                        # flatfish lie on their blind side
            R = Matrix.Rotation(math.pi / 2, 4, 'X')
            bmesh.ops.transform(self.mb.bm, matrix=R, verts=self.mb.bm.verts[:])
        return self.mb


def fish_object(f, name, real_size=True):
    """Mesh at the species' average length (or 1 m), head pointing to -Y, origin at the body centre.

    Built at length 1 first so vertex merging is scale independent, then scaled.
    """
    me = Fish(f).build().build(name, None, mesh_only=True)
    L = f["size_avg"] / 100.0 if real_size else 1.0
    me.transform(Matrix.Rotation(-math.pi / 2, 4, 'Z') @ Matrix.Scale(L, 4))
    me.update()
    return bpy.data.objects.new(name, me)
