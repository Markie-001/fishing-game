"""Island 5 - Cave Island (Teun's Rots): small rocky islet with a big rock and a walk-in cave. Quest hub."""
import bpy, bmesh, math, random
from mathutils import Vector
from fg_lib import (MB, IslandShape, build_terrain, Ground, island_setup, place_many, scatter,
                    instance, light, link, mat, text_mesh, DOCK_DECK_Z)
from fg_assets import Dock, place_npc
from island_home import campfire

PREFIX = "Cave"
FACING = math.radians(-90)                 # dock and cave mouth face south, towards the middle of the world
CAVE_LOCAL = (0.0, 4.0)
CAVE_Z = 2.4


def shape():
    return IslandShape(
        lobes=[(0, 0, 29), (-16, 10, 15), (15, 11, 14)],
        peaks=[(-17, 12, 10, 6.0), (16, 13, 9, 4.0)],
        cliffs=[(math.radians(90), math.radians(70), 7.0)],
        pads=[(CAVE_LOCAL[0], CAVE_LOCAL[1], 16.0, CAVE_Z)],
        seed=71, irregular=0.2, beach_h=1.5, bumps=1.2, seabed_slope=0.4)


def cave_shell(P, size=(14.0, 11.5, 9.5), mouth_half=math.radians(36), mouth_h=0.55, seed=3, thick=1.8):
    """Hollow, faceted rock dome; mouth opening towards local +X. Origin = floor centre."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    rnd = random.Random(seed)
    for v in bm.verts:
        v.co *= 1.0 + rnd.uniform(-0.1, 0.12)
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        ang = abs(math.atan2(c.y, c.x))
        if c.z < -0.12 or (ang < mouth_half and c.z < mouth_h and c.x > 0):
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=thick)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.smooth = False
    me = bpy.data.meshes.new("Cave_Rock_Shell")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(P["rock"])
    return me


def crag(mb, size, loc, m, rot, rnd, jitter=0.22):
    """Box with jittered corners: one layered rock slab."""
    for v in mb.box(size, loc, m, rot=rot):
        v.co += Vector((rnd.uniform(-1, 1) * size[0], rnd.uniform(-1, 1) * size[1], rnd.uniform(-1, 1) * size[2])) * jitter * 0.5


def rock_massif(P, cp, cz, fwd, side):
    """Broad, terraced horseshoe of rock slabs wrapped around the cave dome (open at the mouth).

    Every slab is wider than it is tall, so the silhouette reads as a craggy hill, not a column.
    """
    mb = MB()
    rnd = random.Random(8)
    base_a = math.atan2(fwd.y, fwd.x)
    mats = [P["rock"], P["rock_dark"], P["rock"]]
    for i, a in enumerate(range(60, 301, 24)):
        back = 1.0 - abs(a - 180) / 120.0                       # 1 at the back, 0 near the mouth
        ang = base_a + math.radians(a)
        r = 16.0 + rnd.uniform(-0.5, 1.5)                          # stays outside the dome's inner wall
        c = cp + Vector((math.cos(ang), math.sin(ang), 0)) * r
        tangent = ang + math.pi / 2
        layers = 2 + int(back * 2.2)
        for k in range(layers):
            w = 9.5 - k * 1.8 + rnd.uniform(-0.8, 0.8)
            d = 7.0 - k * 1.3 + rnd.uniform(-0.6, 0.6)
            h = 3.4 - k * 0.3
            inward = Vector((math.cos(ang), math.sin(ang), 0)) * (-k * 1.2)
            p = c + inward
            tilt = (rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12), tangent + rnd.uniform(-0.2, 0.2))
            crag(mb, (w, d, h), (p.x, p.y, cz + 0.6 + k * 2.9), mats[(i + k) % 3], tilt, rnd)
    # flat cap slabs over the dome so it is not a smooth bubble
    for k, (du, dv, z, s) in enumerate(((-3, 0, 10.6, 9.0), (-6, 4, 11.4, 6.5), (-5, -4, 11.2, 6.0), (1, 2, 10.2, 7.0))):
        p = cp + fwd * du + side * dv
        crag(mb, (s, s * 0.75, 2.2), (p.x, p.y, cz + z), mats[k % 3], (rnd.uniform(-0.1, 0.1), rnd.uniform(-0.1, 0.1), rnd.random()), rnd)
    # grass tufts and a few bushes on the terraces
    for k in range(10):
        a = math.radians(rnd.uniform(80, 280)) + base_a
        r = rnd.uniform(15.5, 18.0)
        p = cp + Vector((math.cos(a), math.sin(a), 0)) * r
        mb.ico(rnd.uniform(0.7, 1.2), (p.x, p.y, cz + rnd.choice((2.4, 5.2))), P["bush"], scale=(1, 1, 0.55), jitter=0.2, seed=k)
    return mb


def sea_arch(P, base, g):
    """Natural rock arch standing in the shallows."""
    mb = MB()
    rnd = random.Random(5)
    # legs side by side along X, so the opening faces the sea lane to the south
    legs = [base + Vector((-5.5, 0, 0)), base + Vector((5.5, 0, 0))]
    for k, p in enumerate(legs):
        gz = g.z(p.x, p.y, -6.0)
        z, j = gz + 1.0, 0
        while z < 6.5:                                   # stack slabs from the seabed up to the span
            crag(mb, (5.4 - min(j, 4) * 0.25, 4.6 - min(j, 4) * 0.2, 2.8), (p.x, p.y, z), P["rock_dark"] if (j + k) % 2 else P["rock"],
                 (0, 0, rnd.uniform(-0.3, 0.3)), rnd)
            z += 2.4
            j += 1
    top = (legs[0] + legs[1]) / 2
    crag(mb, (17.0, 4.6, 2.8), (top.x, top.y, 7.0), P["rock"], (0, rnd.uniform(-0.06, 0.06), 0), rnd, jitter=0.15)
    crag(mb, (12.0, 3.4, 1.6), (top.x, top.y, 8.7), P["rock_dark"], (0.05, 0, 0), rnd, jitter=0.2)
    mb.ico(0.9, (top.x + 2.0, top.y, 9.7), P["bush"], scale=(1.8, 1.0, 0.5), jitter=0.2)
    return mb


def cave_interior(P):
    """Props inside the cave in its local frame (mouth = +X). Floor z = 0."""
    mb = MB()
    crystal = mat("M_CaveCrystal", (0.35, 0.95, 0.90), 0.2, emit=(0.3, 1.0, 0.9), emit_strength=6.0)
    pool = mat("M_CavePool", (0.05, 0.30, 0.35), 0.05, emit=(0.1, 0.55, 0.6), emit_strength=1.2)
    # gravel floor over the terrain inside the dome
    floor = mat("M_CaveFloor", (0.38, 0.35, 0.31), 0.95)
    n = 24
    ring = [(12.8 * math.cos(2 * math.pi * k / n), 10.3 * math.sin(2 * math.pi * k / n), 0.04) for k in range(n)]
    mb.poly([(0, 0, 0.04)] + ring, [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)], floor)
    # glowing pool at the back (legendary-fish spot in the questline)
    mb.cyl(3.0, 3.0, 0.06, (-5.5, 0.5, 0.06), pool, seg=12)
    for k in range(12):
        a = 2 * math.pi * k / 12
        mb.ico(0.45, (-5.5 + math.cos(a) * 3.2, 0.5 + math.sin(a) * 3.2, 0.15), P["rock_dark"], scale=(1, 1, 0.6), jitter=0.25, seed=k)
    # crystal clusters
    rnd = random.Random(11)
    for cx, cy in ((-7.8, -4.0), (-3.5, 6.6), (-8.5, 4.5), (2.0, -6.8)):
        for k in range(5):
            h = rnd.uniform(0.5, 1.4)
            tilt = (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 0)
            mb.cyl(0.14, 0.0, h, (cx + rnd.uniform(-0.4, 0.4), cy + rnd.uniform(-0.4, 0.4), h / 2), crystal, rot=tilt, seg=5)
    # old chest
    mb.box((1.0, 0.6, 0.5), (-1.5, -5.2, 0.25), P["wood_dark"])
    mb.cyl(0.3, 0.3, 1.0, (-1.5, -5.2, 0.5), P["wood"], rot=(0, math.pi / 2, 0), seg=8)
    for x in (-1.85, -1.15):
        mb.box((0.06, 0.64, 0.58), (x, -5.2, 0.3), P["metal_dark"])
    mb.box((0.12, 0.05, 0.14), (-1.5, -4.88, 0.45), P["yellow"])
    # stone table with an old sea chart
    mb.cyl(0.4, 0.5, 0.75, (1.5, 4.2, 0.37), P["rock"], seg=7)
    mb.cyl(1.1, 1.0, 0.18, (1.5, 4.2, 0.82), P["rock"], seg=7)
    mb.box((0.9, 0.65, 0.01), (1.5, 4.2, 0.92), P["wood_light"], rot=(0, 0, 0.3))
    mb.box((0.2, 0.2, 0.25), (1.95, 4.5, 1.03), P["lamp_glow"])
    # crates and barrels near the mouth
    for k, (x, y) in enumerate(((4.5, -5.0), (5.2, -4.2), (4.6, -4.2))):
        mb.box((0.6, 0.6, 0.6), (x, y, 0.3 + (0.6 if k == 2 else 0)), P["wood_light"], rot=(0, 0, k * 0.4))
    # timber mine frame at the cave mouth
    for y in (-2.8, 2.8):
        mb.box((0.35, 0.35, 3.6), (12.6, y, 1.8), P["wood_dark"])
    mb.box((0.45, 6.6, 0.4), (12.6, 0, 3.75), P["wood_dark"])
    mb.box((0.1, 1.6, 0.5), (12.85, 0, 4.25), P["wood_light"])
    # torches
    for x, y in ((12.9, -3.3), (12.9, 3.3), (-3.0, -6.8), (-3.0, 7.2)):
        mb.cyl(0.05, 0.04, 1.6, (x, y, 0.8), P["wood_dark"], seg=5)
        mb.cyl(0.12, 0.08, 0.15, (x, y, 1.65), P["metal_dark"], seg=6)
        mb.cyl(0.12, 0.0, 0.35, (x, y, 1.9), mat("M_Fire", (1.0, 0.45, 0.1), 0.5, emit=(1.0, 0.45, 0.12), emit_strength=8.0), seg=5)
    return mb


def tent(P):
    mb = MB()
    pts = [(-1.4, -1.2, 0), (-1.4, 1.2, 0), (1.4, 1.2, 0), (1.4, -1.2, 0), (-1.4, 0, 1.7), (1.4, 0, 1.7)]
    mb.poly(pts, [(0, 3, 5, 4), (1, 4, 5, 2), (0, 4, 1), (3, 2, 5)], P["fabric_orange"])
    for x in (-1.45, 1.45):
        mb.cyl(0.04, 0.04, 1.8, (x, 0, 0.9), P["wood_dark"], seg=4)
    return mb


def quest_board(P):
    mb = MB()
    for y in (-0.9, 0.9):
        mb.box((0.14, 0.14, 2.3), (0, y, 1.15), P["wood_dark"])
    mb.box((0.08, 2.1, 1.2), (0, 0, 1.55), P["wood"])
    mb.gable_roof(0.5, 2.3, 0.35, (0, 0, 2.3), P["roof_dark"], overhang=0.15, thick=0.06)
    rnd = random.Random(2)
    for k in range(5):
        y = -0.7 + k * 0.35
        mb.box((0.02, 0.28, 0.36), (0.05, y, 1.5 + rnd.uniform(-0.2, 0.25)), P["wood_light"], rot=(rnd.uniform(-0.1, 0.1), 0, 0))
    return mb


def build(P, A, center):
    cx, cy = center
    root_c, C, root = island_setup("50_Cave_Island", PREFIX, center)
    W = lambda lx, ly: Vector((cx + lx, cy + ly, 0))

    terrain = build_terrain("Cave_Terrain", center, shape(), P, C["Terrain"], root, cell=2.2, kind="rocky")
    g = Ground([terrain])
    fwd = Vector((math.cos(FACING), math.sin(FACING), 0))
    side = Vector((-fwd.y, fwd.x, 0))

    # --- the rock with the cave
    cp = W(*CAVE_LOCAL)
    cz = g.z(cp.x, cp.y, CAVE_Z)
    shell = bpy.data.objects.new("Cave_Rock_Shell", cave_shell(P))
    shell.location = (cp.x, cp.y, cz - 0.3)
    shell.rotation_euler = (0, 0, FACING)
    link(shell, C["Buildings"], root)
    rock_massif(P, cp, cz, fwd, side).build("Cave_Rock_Massif", C["Buildings"], root)
    sea_arch(P, W(44, -22), g).build("Cave_SeaArch", C["Buildings"], root)
    inner = cave_interior(P).build("Cave_Interior_Props", C["Props"], root)
    inner.location = (cp.x, cp.y, cz)
    inner.rotation_euler = (0, 0, FACING)
    for k, (lx, ly) in enumerate(((12.9, -3.3), (12.9, 3.3), (-3.0, -6.8), (-3.0, 7.2))):
        p = cp + fwd * lx + side * ly
        light("Cave_Torch_Light_%d" % (k + 1), 'POINT', 60, (p.x, p.y, cz + 2.0), C["Lights"], root, color=(1.0, 0.55, 0.2),
              shadow_soft_size=0.15)
    p = cp - fwd * 5.5 + side * 0.5
    light("Cave_Pool_Light", 'POINT', 120, (p.x, p.y, cz + 1.0), C["Lights"], root, color=(0.3, 1.0, 0.9))
    for name, (lx, ly, z) in (("Cave_Entrance_Trigger", (12.6, 0, 1.0)), ("Cave_Chest_Spot", (-1.5, -5.2, 0.5)),
                              ("Cave_Pool_FishingSpot", (-5.5, 0.5, 0.1)), ("Cave_SeaChart_Spot", (1.5, 4.2, 0.95))):
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = 'SPHERE'
        e.empty_display_size = 0.6
        e.location = tuple(cp + fwd * lx + side * ly + Vector((0, 0, cz + z)))
        link(e, C["Props"], root)

    # --- dock (short L-pier) with fuel pump
    mouth = cp + fwd * 13.0
    shore = g.shore((mouth.x, mouth.y), FACING)
    start = shore - fwd * 2.5
    dock = Dock("Cave_Dock", (start.x, start.y, 0), FACING, g, P, plank_m="wood_grey", pile_m="wood_dark")
    dock.rect(0, 16, -1.1, 1.1)
    dock.rect(16, 19.5, -6.5, 1.1)
    dock.cleats([(19.1, -6.0), (19.1, 0.6), (8.0, 1.0)])
    dock.tires([(19.6, -4.0), (19.6, -1.0)])
    dock.build(C["Dock"], root)
    instance("Cave_FuelPump", A["fuel_blue"], dock.w(17.6, -5.5), C["Dock"], root, rot=(0, 0, FACING + math.pi / 2))
    instance("Cave_Dock_Lamp", A["lamp"], dock.w(16.3, 0.9), C["Dock"], root)
    light("Cave_Dock_LampLight", 'POINT', 70, tuple(dock.w(16.3, 0.9, DOCK_DECK_Z + 3.4)), C["Lights"], root, color=(1.0, 0.85, 0.6))
    instance("Cave_Dock_LifeRing", A["life_ring"], dock.w(12.0, -1.05), C["Dock"], root, rot=(0, 0, FACING))

    # --- Teun's camp in front of the cave
    camp = cp + fwd * 17.0 + side * 6.0
    camp_z = g.z(camp.x, camp.y, CAVE_Z)
    campfire(P, (camp.x, camp.y, camp_z)).build("Cave_Campfire", C["Props"], root)
    light("Cave_Campfire_Light", 'POINT', 120, (camp.x, camp.y, camp_z + 0.8), C["Lights"], root, color=(1.0, 0.5, 0.15))
    tp = camp + side * 4.0 - fwd * 1.0
    t = tent(P).build("Cave_Tent", C["Props"], root)
    t.location = (tp.x, tp.y, g.z(tp.x, tp.y, CAVE_Z))
    t.rotation_euler = (0, 0, FACING + 0.3)
    bp = cp + fwd * 16.5 - side * 5.0
    board = quest_board(P).build("Cave_QuestBoard", C["Props"], root)
    board.location = (bp.x, bp.y, g.z(bp.x, bp.y, CAVE_Z))
    board.rotation_euler = (0, 0, FACING)
    text_mesh("Cave_QuestBoard_Sign", "QUESTS", 0.32, tuple(bp + fwd * 0.12 + Vector((0, 0, board.location.z + 2.25))),
              (math.pi / 2, 0, FACING + math.pi / 2), P["white"], C["Props"], root, extrude=0.02)
    for k, (dx, dy, a) in enumerate(((1.2, -0.6, "barrel_wood"), (1.0, 0.2, "crate"))):
        p = camp + fwd * dx + side * dy - side * 2.6
        instance("Cave_Camp_Prop_%d" % (k + 1), A[a], (p.x, p.y, g.z(p.x, p.y, CAVE_Z)), C["Props"], root)

    # --- Teun, the quest giver, standing by the fire facing the dock
    tn = camp + fwd * 1.6 - side * 1.0
    place_npc("Teun", P, (tn.x, tn.y, g.z(tn.x, tn.y, CAVE_Z)), FACING, C["NPCs"], root)

    # --- vegetation & rocks
    avoid = [(cp.x, cp.y, 16.5), (camp.x, camp.y, 7.0), (start.x, start.y, 4.0), (bp.x, bp.y, 2.5),
             (mouth.x, mouth.y, 6.0)]
    bushes = scatter(g, center, 34, 22, 501, 1.8, 20, 0.7, avoid, 2.0)
    place_many("Cave_Bush", A["bush_dark"], bushes, C["Vegetation"], root, 1, (0.6, 1.2))
    pines = scatter(g, center, 34, 6, 502, 3.0, 20, 0.75, avoid, 6.0)
    place_many("Cave_Pine", A["pine"], pines, C["Vegetation"], root, 2, (0.6, 0.9))
    rocks = scatter(g, center, 45, 35, 503, -2.0, 10, 0.0, avoid + [(dock.w(10, -2).x, dock.w(10, -2).y, 12)], 2.5)
    place_many("Cave_Rock", A["rock_dark"] + A["rock"], rocks, C["Vegetation"], root, 3, (0.7, 1.8), 0.5)
    return root
