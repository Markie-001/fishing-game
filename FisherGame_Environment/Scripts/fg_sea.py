"""Details on and in the open water (buoys, beacons, reefs, kelp, fish schools, gulls) and the easter eggs.

Everything floating sits around z = 0. In Unity these are static; give a buoy a Rigidbody + the existing
Floater script if it should bob on the WaterManagement waves.
"""
import bpy, math, random
from mathutils import Vector
from fg_lib import MB, Ground, coll, clear_coll, link, instance, light, mat, text_mesh, srgb
from fg_assets import boat_mesh

OPEN_SEA_Z = -14.0


# ---------------------------------------------------------------- meshes

def nav_buoy_mesh(name, P, kind):
    """Lateral channel buoy: red can (port) or green cone (starboard), with a small light."""
    mb = MB()
    col = P["red"] if kind == "red" else P["green_paint"]
    mb.cyl(0.9, 0.75, 0.9, (0, 0, -0.1), col, seg=6)
    mb.cyl(0.95, 0.95, 0.15, (0, 0, 0.38), P["white"], seg=6)
    for k in range(3):
        a = 2 * math.pi * k / 3
        mb.cyl_between((math.cos(a) * 0.6, math.sin(a) * 0.6, 0.4), (math.cos(a) * 0.2, math.sin(a) * 0.2, 2.2), 0.05, 0.05, col, seg=3)
    if kind == "red":
        mb.cyl(0.35, 0.35, 0.6, (0, 0, 2.5), col, seg=6)
    else:
        mb.cyl(0.45, 0.0, 0.8, (0, 0, 2.6), col, seg=6)
    glow = mat("M_BuoyLight_%s" % kind, (1, 0.2, 0.2) if kind == "red" else (0.2, 1, 0.3), 0.3,
               emit=(1, 0.15, 0.1) if kind == "red" else (0.1, 1, 0.25), emit_strength=8.0)
    mb.box((0.2, 0.2, 0.2), (0, 0, 3.15), glow)
    return mb.build(name, None, mesh_only=True)


def mooring_buoy_mesh(name, P):
    mb = MB()
    mb.ico(0.55, (0, 0, 0.1), P["white"], scale=(1, 1, 0.85), sub=1)
    mb.torus(0.18, 0.04, (0, 0, 0.62), P["metal"], rot=(math.pi / 2, 0, 0), seg=6, rseg=3)
    mb.cyl(0.57, 0.57, 0.12, (0, 0, 0.05), P["blue"], seg=8)
    return mb.build(name, None, mesh_only=True)


def pot_float_mesh(name, P, col):
    mb = MB()
    mb.ico(0.22, (0, 0, 0.05), P[col], scale=(1, 1, 1.3))
    mb.cyl(0.02, 0.02, 1.4, (0, 0, 0.8), P["wood_grey"], seg=4)
    mb.box((0.02, 0.3, 0.2), (0, 0.15, 1.4), P[col])
    return mb.build(name, None, mesh_only=True)


def kelp_mesh(name, P, seed=0):
    rnd = random.Random(seed)
    kelp = mat("M_Kelp", (0.30, 0.42, 0.18), 0.8)
    mb = MB()
    for k in range(4):
        base = Vector((rnd.uniform(-1.2, 1.2), rnd.uniform(-1.2, 1.2), 0))
        h = rnd.uniform(3.0, 5.5)
        n = 3
        pts, faces = [], []
        for i in range(n + 1):
            t = i / n
            c = base + Vector((math.sin(t * 3 + k) * 0.35, math.cos(t * 2 + k) * 0.25, t * h))
            w = 0.18 * (1 - t * 0.7)
            pts += [c + Vector((w, 0, 0)), c - Vector((w, 0, 0))]
        for i in range(n):
            faces.append((i * 2, i * 2 + 1, i * 2 + 3, i * 2 + 2))
        mb.poly(pts, faces, kelp)
    return mb.build(name, None, mesh_only=True)


def fish_school_mesh(name, P, seed=0):
    rnd = random.Random(seed)
    mb = MB()
    for k in range(5):
        p = (rnd.uniform(-2.5, 2.5), rnd.uniform(-1.5, 1.5), rnd.uniform(-0.8, 0.8))
        mb.ico(0.12, p, P["fish"], scale=(2.6, 0.7, 0.9), rot=(0, 0, 0.3 + rnd.uniform(-0.15, 0.15)))
    return mb.build(name, None, mesh_only=True)


def gull_mesh(name, P, flying=False):
    mb = MB()
    mb.ico(0.12, (0, 0, 0.18), P["white"], scale=(2.0, 0.9, 0.9))
    mb.ico(0.07, (0.2, 0, 0.27), P["white"])
    mb.cyl(0.03, 0.0, 0.08, (0.29, 0, 0.26), P["yellow"], rot=(0, math.pi / 2, 0), seg=4)
    wing_up = 0.35 if flying else -0.1
    for s in (-1, 1):
        mb.poly([(0.08, s * 0.06, 0.22), (-0.12, s * 0.06, 0.22), (-0.06, s * 0.5, 0.22 + wing_up), (0.04, s * 0.55, 0.22 + wing_up)],
                [(0, 1, 2, 3)], P["roof_dark"] if not flying else P["white"])
    if not flying:
        for s in (-1, 1):
            mb.cyl(0.01, 0.01, 0.12, (0, s * 0.04, 0.05), P["yellow"], seg=3)
    return mb.build(name, None, mesh_only=True)


def raft(P):
    mb = MB()
    for x in (-1.4, 1.4):
        for y in (-1.4, 1.4):
            mb.cyl(0.35, 0.35, 0.9, (x, y, 0.05), P["blue"], rot=(math.pi / 2, 0, 0), seg=8)
    for k in range(10):
        mb.box((0.3, 3.8, 0.08), (-1.5 + k * 0.335, 0, 0.5), P["wood_light"])
    for y in (-0.25, 0.25):
        mb.cyl(0.03, 0.03, 1.4, (1.95, y, 0.2), P["metal"], seg=4)
    for z in (0.0, -0.35):
        mb.box((0.06, 0.55, 0.04), (1.95, 0, z), P["metal"])
    mb.cyl(0.03, 0.03, 2.0, (-1.7, -1.7, 1.5), P["wood_dark"], seg=4)
    mb.box((0.02, 0.6, 0.4), (-1.7, -1.4, 2.3), P["fabric_orange"])
    return mb


def beacon(P):
    """Yellow/black cardinal beacon on a rock in the middle of the sea: orientation landmark."""
    mb = MB()
    rnd = random.Random(4)
    for k in range(6):
        a = 2 * math.pi * k / 6
        mb.ico(rnd.uniform(2.6, 3.6), (math.cos(a) * 3, math.sin(a) * 3, -4.0 + rnd.uniform(0, 2)), P["rock_dark"],
               scale=(1, 1, 1.6), jitter=0.25, seed=k)
    mb.ico(4.2, (0, 0, -2.5), P["rock"], scale=(1, 1, 0.9), jitter=0.2, seed=9)
    mb.cyl(1.4, 1.6, 1.2, (0, 0, 1.6), P["concrete"], seg=8)
    for k, z in enumerate((2.2, 3.4, 4.6, 5.8)):
        mb.cyl(0.55, 0.5, 1.2, (0, 0, z + 0.6), P["yellow"] if k % 2 == 0 else P["black"], seg=8)
    mb.cyl(0.8, 0.8, 0.15, (0, 0, 7.0), P["metal_dark"], seg=8)
    mb.cyl(0.35, 0.35, 0.6, (0, 0, 7.4), P["lamp_glow"], seg=8)
    for s in (1, -1):
        mb.cyl(0.45, 0.0, 0.7, (0, 0, 8.2 + s * 0.4), P["black"], rot=(0 if s > 0 else math.pi, 0, 0), seg=8)
    mb.box((0.1, 1.2, 0.08), (1.2, 0, 2.3), P["metal"])
    return mb


# ---------------------------------------------------------------- easter egg meshes

def rubber_duck(P):
    duck_y = mat("M_DuckYellow", (1.0, 0.85, 0.15), 0.25)
    mb = MB()
    mb.ico(1.6, (0, 0, 0.5), duck_y, scale=(1.35, 1.0, 0.75), sub=2)
    mb.ico(0.9, (0.9, 0, 2.0), duck_y, sub=2)
    mb.cyl(0.4, 0.25, 0.6, (1.8, 0, 1.85), P["fabric_orange"], rot=(0, math.pi / 2, 0), seg=8)
    for s in (-1, 1):
        mb.ico(0.14, (1.55, s * 0.4, 2.25), P["black"], sub=1)
        mb.ico(0.6, (-0.2, s * 1.0, 0.8), duck_y, scale=(1.4, 0.35, 0.6), sub=1)
    mb.ico(0.5, (-1.9, 0, 1.2), duck_y, scale=(0.8, 0.6, 0.9), sub=1)
    return mb


def sea_serpent(P):
    """Original low-poly sea monster: three humps, head and tail fin poking out of the water."""
    scales = mat("M_SerpentScales", (0.18, 0.45, 0.35), 0.5)
    belly = mat("M_SerpentBelly", (0.85, 0.75, 0.45), 0.6)
    mb = MB()
    for k in range(3):
        x = k * 7.0
        mb.torus(2.4, 0.75, (x, 0, -0.6), scales, rot=(math.pi / 2, 0, 0), seg=14, rseg=6)
        for j in range(3):
            mb.cyl(0.35, 0.0, 0.8, (x - 0.8 + j * 0.8, 0, 2.8 - abs(j - 1) * 0.25), P["fabric_orange"], seg=4)
    head = Vector((-5.5, 0, 2.4))
    mb.cyl_between((-3.2, 0, -0.5), head, 0.8, 0.65, scales, seg=8)
    mb.ico(1.1, head + Vector((-0.6, 0, 0.3)), scales, scale=(1.5, 0.9, 0.8), sub=1)
    mb.ico(0.5, head + Vector((-1.7, 0, -0.05)), belly, scale=(1.6, 0.9, 0.5), sub=1)
    for s in (-1, 1):
        mb.ico(0.22, head + Vector((-1.0, s * 0.6, 0.75)), P["yellow"], sub=1)
        mb.ico(0.1, head + Vector((-1.15, s * 0.68, 0.78)), P["black"], sub=1)
        mb.cyl(0.18, 0.0, 0.7, head + Vector((0.1, s * 0.45, 1.2)), P["white"], rot=(0, -0.5, 0), seg=4)
    mb.poly([(20.5, 0, -0.2), (23.5, 0, 2.8), (22.2, 0, 0.6), (24.0, 0, -0.2)], [(0, 1, 2), (0, 2, 3)], P["fabric_orange"])
    return mb


def treasure_islet(P):
    mb = MB()
    mb.ico(7.0, (0, 0, -3.0), P["sand"], scale=(1.0, 0.85, 0.55), sub=2, jitter=0.05, seed=3)
    mb.ico(9.5, (0, 0, -6.0), P["sand_wet"], scale=(1.0, 0.85, 0.5), sub=2, jitter=0.05, seed=4)
    for r in (0.6, -0.6):
        mb.box((2.0, 0.35, 0.05), (2.0, -1.5, 0.86), P["red"], rot=(0, 0, r))
    mb.cyl(0.04, 0.04, 1.2, (2.9, -0.6, 1.3), P["wood"], rot=(0.25, 0.1, 0), seg=4)
    mb.box((0.28, 0.04, 0.38), (2.86, -0.75, 0.72), P["metal"], rot=(0.25, 0.1, 0))
    for k in range(3):
        a = k * 2.0
        mb.ico(0.45, (math.cos(a) * 4.5, math.sin(a) * 3.6, 0.5), P["rock"], scale=(1, 1, 0.6), jitter=0.2, seed=k)
    return mb


def golden_fish(P):
    gold = mat("M_Gold", (1.0, 0.78, 0.25), 0.25, metal=1.0)
    mb = MB()
    mb.cyl(0.35, 0.4, 0.5, (0, 0, 0.25), P["rock"], seg=6)
    mb.ico(0.22, (0, 0, 0.75), gold, scale=(2.2, 0.6, 1.1), sub=1)
    mb.poly([(-0.45, 0, 0.75), (-0.75, 0, 1.0), (-0.75, 0, 0.5)], [(0, 1, 2)], gold)
    return mb


def treasure_chest(P):
    mb = MB()
    mb.box((1.2, 0.75, 0.6), (0, 0, 0.3), P["wood_dark"])
    mb.cyl(0.38, 0.38, 1.2, (0, 0, 0.6), P["wood"], rot=(0, math.pi / 2, 0), seg=8)
    for x in (-0.45, 0.45):
        mb.box((0.08, 0.8, 0.7), (x, 0, 0.35), P["yellow"])
    gold = mat("M_Gold", (1.0, 0.78, 0.25), 0.25, metal=1.0)
    for k in range(6):
        mb.cyl(0.08, 0.08, 0.03, (0.8 + k * 0.12, 0.2 * (-1) ** k, 0.02 + 0.03 * (k % 3)), gold, seg=8)
    return mb


# ---------------------------------------------------------------- builders

def _ground():
    terr = [o for o in bpy.data.objects if o.name.endswith("_Terrain") and o.type == 'MESH']
    return Ground(terr)


def _depth(g, x, y):
    return g.z(x, y, OPEN_SEA_Z)


def build_sea_details(P, A, islands):
    c = coll("60_Sea_Details")
    clear_coll(c)
    subs = {k: coll("Sea_%s" % k, c) for k in ("Buoys", "Beacon", "Reefs", "Underwater", "Wildlife", "Floating")}
    root = bpy.data.objects.new("Sea_Details_Root", None)
    root.empty_display_type = 'CUBE'
    c.objects.link(root)
    g = _ground()
    rnd = random.Random(77)

    red, green = nav_buoy_mesh("Asset_NavBuoy_Red", P, "red"), nav_buoy_mesh("Asset_NavBuoy_Green", P, "green")
    mooring = mooring_buoy_mesh("Asset_MooringBuoy", P)
    floats = [pot_float_mesh("Asset_PotFloat_%s" % k, P, k) for k in ("fabric_orange", "yellow", "red")]
    kelp = [kelp_mesh("Asset_Kelp_%d" % k, P, k) for k in range(3)]
    school = fish_school_mesh("Asset_FishSchool", P)
    gull, gull_fly = gull_mesh("Asset_Gull", P), gull_mesh("Asset_Gull_Flying", P, True)

    # --- channel buoys: a red/green gate on the approach to every island
    n = 0
    for key, info in islands.items():
        cx, cy = info["center"]
        d = Vector((-cx, -cy, 0)).normalized()
        side = Vector((-d.y, d.x, 0))
        shore = g.shore((cx, cy), math.atan2(d.y, d.x), level=-2.5, step=1.0, max_d=200)
        for k, dist in enumerate((25.0, 55.0)):
            p = shore + d * dist
            for s, me in ((1, red), (-1, green)):
                q = p + side * 13.0 * s
                n += 1
                instance("Sea_NavBuoy_%s_%s_%d" % (key, "Red" if s > 0 else "Green", k + 1), me, (q.x, q.y, 0.0),
                         subs["Buoys"], root, rot=(0, 0, rnd.random() * 6))

    # --- mooring buoys off Home and the marina, pot floats off the Rod shop and Fish island
    def ring_points(center, r0, r1, count, seed, min_depth=-3.0):
        rr = random.Random(seed)
        pts = []
        while len(pts) < count:
            a = rr.uniform(0, 2 * math.pi)
            r = rr.uniform(r0, r1)
            x, y = center[0] + math.cos(a) * r, center[1] + math.sin(a) * r
            if _depth(g, x, y) < min_depth:
                pts.append((x, y))
        return pts

    for key, count in (("Home", 3), ("Dealer", 4)):
        for k, (x, y) in enumerate(ring_points(islands[key]["center"], 70, 95, count, 10 + count)):
            instance("Sea_MooringBuoy_%s_%d" % (key, k + 1), mooring, (x, y, 0.0), subs["Buoys"], root)
    for key, count in (("Rod", 10), ("Fish", 8), ("Cave", 5)):
        for k, (x, y) in enumerate(ring_points(islands[key]["center"], 55, 80, count, 20 + count)):
            instance("Sea_PotFloat_%s_%02d" % (key, k + 1), floats[k % 3], (x, y, 0.0), subs["Floating"], root,
                     rot=(0, 0, rnd.random() * 6))

    # --- net float line off Fish island
    fx, fy = islands["Fish"]["center"]
    mb = MB()
    prev = None
    for k in range(16):
        a = math.radians(200 + k * 3.0)
        p = Vector((fx + math.cos(a) * 95, fy + math.sin(a) * 95, 0.05))
        mb.ico(0.18, p, P["fabric_orange"] if k % 2 else P["white"], scale=(1.3, 1, 0.8))
        if prev is not None:
            mb.cyl_between(prev, p, 0.02, 0.02, P["rope"], seg=3)
        prev = p
    mb.build("Sea_NetFloatLine_Fish", subs["Floating"], root)

    # --- swim raft off Home beach
    hx, hy = islands["Home"]["center"]
    d = Vector((-hx, -hy, 0)).normalized()
    side = Vector((-d.y, d.x, 0))
    rp = g.shore((hx, hy), math.atan2(d.y, d.x) - 0.6, level=-2.5, step=1.0) + d * 12
    r = raft(P).build("Sea_SwimRaft_Home", subs["Floating"], root)
    r.location = (rp.x, rp.y, 0.0)
    r.rotation_euler = (0, 0, 0.4)

    # --- beacon in the middle of the world
    b = beacon(P).build("Sea_Beacon_Center", subs["Beacon"], root)
    b.location = (0.0, 30.0, 0.0)
    light("Sea_Beacon_Light", 'POINT', 800, (0.0, 30.0, 7.5), subs["Beacon"], root, color=(1.0, 0.9, 0.6), use_shadow=False)
    instance("Sea_Gull_Beacon", gull, (0.4, 30.2, 8.75), subs["Wildlife"], root, rot=(0, 0, 1.2))

    # --- reefs: jagged rock clusters poking out of open water between the islands
    reef_centres = [(10, -170), (-210, 30), (215, 25), (95, 300), (-120, 330), (-300, -260)]
    rocks = A["rock_dark"] + A["rock"]
    for i, (x, y) in enumerate(reef_centres):
        for k in range(rnd.randint(3, 6)):
            px, py = x + rnd.uniform(-12, 12), y + rnd.uniform(-12, 12)
            s = rnd.uniform(3.0, 5.5)
            instance("Sea_Reef_%d_Rock_%d" % (i + 1, k + 1), rocks[rnd.randrange(len(rocks))], (px, py, -2.5 - rnd.uniform(0, 1.5) * s * 0.4),
                     subs["Reefs"], root, rot=(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.random() * 6), scale=s)
        if i % 2 == 0:
            instance("Sea_Gull_Reef_%d" % (i + 1), gull, (x, y, 2.6), subs["Wildlife"], root, rot=(0, 0, rnd.random() * 6))

    # --- underwater: kelp in the shallows around every island, fish schools (future fishing spots)
    for key, info in islands.items():
        cx, cy = info["center"]
        placed = 0
        tries = 0
        while placed < 8 and tries < 400:
            tries += 1
            a = rnd.uniform(0, 2 * math.pi)
            r = rnd.uniform(20, 90)
            x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
            z = _depth(g, x, y)
            if -8.0 < z < -2.5:
                placed += 1
                s = max(0.3, min(1.2, (-z - 1.2) / 5.5))       # keep the tips ~1 m under the surface
                instance("Sea_Kelp_%s_%d" % (key, placed), kelp[placed % 3], (x, y, z), subs["Underwater"], root,
                         rot=(0, 0, rnd.random() * 6), scale=s)
    spots = [(-60, -60), (80, -40), (60, 110), (-90, 60), (-20, 210), (260, -10), (-280, -120), (150, -300)]
    for k, (x, y) in enumerate(spots):
        instance("Sea_FishSchool_%d" % (k + 1), school, (x, y, -2.5), subs["Underwater"], root, rot=(0, 0, rnd.random() * 6))
        e = bpy.data.objects.new("Sea_FishingSpot_%d" % (k + 1), None)
        e.empty_display_type = 'CIRCLE'
        e.empty_display_size = 6.0
        e.location = (x, y, 0.0)
        link(e, subs["Underwater"], root)

    # --- gulls flying over each island and on some buoys
    for key, info in islands.items():
        cx, cy = info["center"]
        for k in range(3):
            a = rnd.uniform(0, 2 * math.pi)
            instance("Sea_Gull_Flying_%s_%d" % (key, k + 1), gull_fly,
                     (cx + math.cos(a) * 25, cy + math.sin(a) * 25, rnd.uniform(18, 28)), subs["Wildlife"], root,
                     rot=(0, rnd.uniform(-0.2, 0.2), a + math.pi / 2), scale=1.6)
    buoys = [o for o in subs["Buoys"].objects if "NavBuoy" in o.name]
    for k, o in enumerate(buoys[::5]):
        instance("Sea_Gull_OnBuoy_%d" % (k + 1), gull, (o.location.x, o.location.y, 3.2), subs["Wildlife"], root,
                 rot=(0, 0, rnd.random() * 6))

    # --- drifting barrels and a crate
    for k, (x, y) in enumerate(((-40, -120), (120, 40), (-150, -20), (40, 250))):
        me = A["barrel"] if k % 2 else A["crate"]
        instance("Sea_Drift_%d" % (k + 1), me, (x, y, -0.35), subs["Floating"], root,
                 rot=(math.pi / 2 if k % 2 else 0.3, 0.2, rnd.random() * 6))
    return root


def build_fishing_zones():
    """Circle empties for every fishing-zone anchor (see fish_catalog.md, section 3).

    Name: FishingZone_<CODE>_<n>_r<radius>; custom properties zone/zone_name/radius/priority/depth travel with the FBX.
    The Drop has no circle: it is everything farther than 330 m from FishingZone_OPEN_1.
    """
    import fish_data as FD
    c = coll("80_FishingZones")
    clear_coll(c)
    root = bpy.data.objects.new("FishingZones_Root", None)
    root.empty_display_type = 'CUBE'
    c.objects.link(root)
    for code in FD.ZONE_ORDER:
        Z = FD.ZONES[code]
        for k, (x, y, r) in enumerate(Z["anchors"]):
            if r >= 9000:
                continue
            e = bpy.data.objects.new("FishingZone_%s_%d_r%d" % (code, k + 1, r), None)
            e.empty_display_type = 'CIRCLE'
            e.empty_display_size = r
            e.location = (x, y, 0.5)
            e["zone"] = code
            e["zone_name"] = Z["name"]
            e["radius"] = float(r)
            e["priority"] = Z["priority"]
            e["depth"] = Z["depth"]
            link(e, c, root)
    return root


def build_easter_eggs(P, A):
    c = coll("70_EasterEggs")
    clear_coll(c)
    root = bpy.data.objects.new("EasterEggs_Root", None)
    root.empty_display_type = 'CUBE'
    c.objects.link(root)
    g = _ground()

    # 1. Sunken shipwreck in the north-west with a treasure chest on the seabed
    wx, wy = -360.0, 300.0
    hull = boat_mesh("EE_Shipwreck", P, 18.0, 5.2, "wood_dark", "wood", "none")
    instance("EE_Shipwreck", hull, (wx, wy, -2.2), c, root, rot=(0.35, -0.25, 0.7))
    mb = MB()
    mb.cyl_between((wx + 1, wy + 0.5, -1.0), (wx + 2.0, wy + 1.4, 6.5), 0.18, 0.14, P["wood_dark"], seg=6)   # broken mast
    mb.cyl_between((wx + 2.0, wy + 1.4, 5.5), (wx + 4.0, wy + 0.2, 4.6), 0.1, 0.08, P["wood_dark"], seg=5)
    mb.poly([(wx + 2.0, wy + 1.4, 6.2), (wx + 3.6, wy + 0.6, 5.0), (wx + 2.1, wy + 1.3, 3.0)], [(0, 1, 2)], P["fabric_white"])
    mb.ico(10.0, (wx - 2, wy - 6, -15.0), P["sand_wet"], scale=(1.4, 1.0, 0.6), sub=2, jitter=0.05)
    mb.build("EE_Shipwreck_MastAndSeabed", c, root)
    ch = treasure_chest(P).build("EE_Shipwreck_TreasureChest", c, root)
    ch.location = (wx - 4.0, wy - 6.0, -9.0)
    ch.rotation_euler = (0.1, 0.05, 0.4)

    # 2. Tiny treasure islet with an X in the sand (south-east corner)
    tx, ty = 380.0, -385.0
    isl = treasure_islet(P).build("EE_TreasureIslet", c, root)
    isl.location = (tx, ty, 0.0)
    instance("EE_TreasureIslet_Palm", A["palm"][1], (tx - 1.5, ty + 1.0, 0.8), c, root, rot=(0, 0, 0.5))

    # 3. Giant rubber duck drifting in the south-west
    duck = rubber_duck(P).build("EE_RubberDuck", c, root)
    duck.location = (-390.0, -380.0, -0.3)
    duck.rotation_euler = (0, 0, 2.3)

    # 4. Sea serpent humps in the far north-east
    s = sea_serpent(P).build("EE_SeaSerpent", c, root)
    s.location = (380.0, 395.0, 0.0)
    s.rotation_euler = (0, 0, -0.6)

    # 5. "TEUN WAS HERE" carved in the back wall of the cave + golden fish idol hidden behind the lighthouse
    shell = bpy.data.objects.get("Cave_Rock_Shell")
    if shell:
        f = shell.rotation_euler.z
        fwd = Vector((math.cos(f), math.sin(f), 0))
        side = Vector((-fwd.y, fwd.x, 0))
        p = shell.location - fwd * 9.4 - side * 4.0 + Vector((0, 0, 2.6))
        text_mesh("EE_Cave_TeunWasHere", "TEUN WAS HERE", 0.45, tuple(p), (math.pi / 2, 0, f + math.pi / 2),
                  mat("M_Carving", (0.85, 0.82, 0.75), 0.9), c, root, extrude=0.03)
    lh = bpy.data.objects.get("Fish_Lighthouse")
    if lh:
        f = lh.rotation_euler.z
        back = lh.location - Vector((math.cos(f), math.sin(f), 0)) * 8.0
        z = g.z(back.x, back.y, lh.location.z)
        gf = golden_fish(P).build("EE_GoldenFish", c, root)
        gf.location = (back.x, back.y, z)
        gf.rotation_euler = (0, 0, f)
    return root
