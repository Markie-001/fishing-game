"""Island 4 - Fishing Rod Shop Island: small, rugged pine island with a bait & tackle shop."""
import bpy, math, random
from mathutils import Vector
from fg_lib import (MB, IslandShape, build_terrain, Ground, island_setup, place_many, scatter,
                    instance, light, link, mat, text_mesh, DOCK_DECK_Z)
from fg_assets import Dock, boat_mesh, place_npc

PREFIX = "Rod"
FACING = math.radians(-41)                 # towards the middle of the world
SHOP_LOCAL = (8.0, -7.0)
SHOP_Z = 2.5


def shape():
    return IslandShape(
        lobes=[(0, 0, 29), (14, -10, 17), (-13, 12, 16), (-16, -10, 11)],
        peaks=[(-8, 9, 17, 13.0), (-16, -9, 9, 5.0)],
        cliffs=[(math.radians(135), math.radians(45), 9.0), (math.radians(-150), math.radians(20), 5.0)],
        pads=[(SHOP_LOCAL[0], SHOP_LOCAL[1], 8.0, SHOP_Z)],
        seed=53, irregular=0.22, beach_h=1.5, bumps=1.6, seabed_slope=0.45)


def tackle_shop(P):
    """Weathered timber bait & tackle shop with a walk-in interior. Front = +X, origin = ground."""
    mb = MB()
    Lx, Ly, H = 8.0, 11.0, 3.4
    wall, trim = P["wood_grey"], P["navy"]
    glass = P["window_lit"]
    f = 0.5
    mb.box((Lx + 3.0, Ly + 0.6, 0.5), (1.3, 0, 0.25), P["wood_dark"])     # floor + front boardwalk
    x0, x1, y0, y1 = -Lx / 2, Lx / 2, -Ly / 2, Ly / 2
    # front: two shop windows and a double door
    mb.wall((x1, y0), (x1, y1), 0.2, H, wall, openings=[(0.8, 3.8, 0.7, 2.6), (4.6, 6.4, 0.0, 2.4), (7.2, 10.2, 0.7, 2.6)],
            z0=f, glass=glass)
    mb.wall((x0, y0), (x0, y1), 0.2, H, wall, openings=[(4.5, 6.5, 1.2, 2.4)], z0=f, glass=P["glass"])
    mb.wall((x0, y0), (x1, y0), 0.2, H, wall, openings=[(3.0, 5.0, 1.2, 2.4)], z0=f, glass=glass)
    mb.wall((x0, y1), (x1, y1), 0.2, H, wall, openings=[(3.0, 5.0, 1.2, 2.4)], z0=f, glass=glass)
    for x in (x0, x1):
        for y in (y0, y1):
            mb.box((0.3, 0.3, H), (x, y, f + H / 2), P["white"])
    # board-and-batten lines on the facade
    for k in range(12):
        y = y0 + 0.45 + k * 0.92
        if not (4.4 < y - y0 < 6.6):                   # keep the doorway clear
            mb.box((0.06, 0.08, H), (x1 + 0.11, y, f + H / 2), P["wood_dark"])
    # roof: slate gable + front porch roof
    mb.gable_roof(Lx, Ly, 2.4, (0, 0, f + H), P["roof_dark"], overhang=0.5, thick=0.2)
    pr = [(x1 + 0.3, y0 - 0.5, f + H), (x1 + 0.3, y1 + 0.5, f + H), (x1 + 2.9, y1 + 0.5, f + H - 0.6), (x1 + 2.9, y0 - 0.5, f + H - 0.6)]
    pts = pr + [(p[0], p[1], p[2] - 0.15) for p in pr]
    mb.poly(pts, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], P["roof_dark"])
    for y in (y0 - 0.3, -1.0, 1.0, y1 + 0.3):
        mb.box((0.2, 0.2, H - 0.6), (x1 + 2.7, y, f + (H - 0.6) / 2), P["wood_dark"])
    # chimney (stove pipe)
    mb.cyl(0.18, 0.18, 2.0, (x0 + 1.2, y1 - 1.5, f + H + 2.0), P["metal_dark"], seg=8)
    mb.cyl(0.28, 0.28, 0.12, (x0 + 1.2, y1 - 1.5, f + H + 3.0), P["metal_dark"], seg=8)
    # buoys and a life ring hanging on the facade
    cols = [P["red"], P["yellow"], P["white"], P["fabric_orange"], P["blue"]]
    for k in range(5):
        mb.ico(0.18, (x1 + 0.25, y0 + 0.25, f + 2.9 - k * 0.42), cols[k], scale=(1, 1, 1.4))
    mb.torus(0.35, 0.09, (x1 + 0.2, y1 - 0.4, f + 2.6), P["red"], rot=(math.pi / 2, 0, math.pi / 2), seg=12, rseg=5)

    # ---------- interior
    wd, dk, lt = P["wood"], P["wood_dark"], P["wood_light"]
    # L-shaped counter on the left
    mb.box((3.2, 0.7, 1.0), (-0.6, -3.4, f + 0.5), dk)
    mb.box((3.3, 0.8, 0.06), (-0.6, -3.4, f + 1.03), lt)
    mb.box((0.7, 2.0, 1.0), (-1.85, -4.4, f + 0.5), dk)
    mb.box((0.45, 0.35, 0.3), (0.2, -3.4, f + 1.2), P["metal_dark"])       # till
    # rod racks along the back wall (many rods = the shop's identity)
    rnd = random.Random(9)
    for rack_y in (-4.5, -1.5, 1.5, 4.5):
        mb.box((0.3, 2.4, 0.15), (x0 + 0.35, rack_y, f + 0.25), dk)
        mb.box((0.15, 2.4, 0.1), (x0 + 0.2, rack_y, f + 2.6), dk)
        for k in range(9):
            y = rack_y - 1.1 + k * 0.27
            top = Vector((x0 + 0.2, y, f + 3.0 + rnd.uniform(-0.15, 0.15)))
            mb.cyl_between((x0 + 0.38, y, f + 0.3), top, 0.025, 0.008, P["black"] if k % 3 else P["wood_dark"], seg=4)
            mb.cyl(0.04, 0.04, 0.08, (x0 + 0.36, y + 0.04, f + 0.9), P["metal"], rot=(math.pi / 2, 0, 0), seg=6)
    # wall shelves with lure boxes on the right wall
    for z in (1.0, 1.6, 2.2):
        mb.box((3.6, 0.4, 0.05), (0.0, y1 - 0.35, f + z), wd)
        for k in range(8):
            c = cols[(k + int(z * 10)) % len(cols)]
            mb.box((0.3, 0.25, 0.22), (-1.5 + k * 0.43, y1 - 0.35, f + z + 0.14), c)
    # centre display table with reels and a tackle box
    mb.box((1.6, 1.0, 0.85), (0.6, 1.0, f + 0.42), wd)
    for k in range(4):
        mb.cyl(0.12, 0.12, 0.1, (0.1 + k * 0.33, 1.0, f + 0.92), P["metal"], rot=(math.pi / 2, 0, 0), seg=8)
    mb.box((0.6, 0.35, 0.3), (2.6, -0.8, f + 0.15), P["green_paint"])
    # bait fridge
    mb.box((0.8, 1.6, 1.9), (2.8, -4.7, f + 0.95), P["white"])
    mb.box((0.05, 1.4, 1.5), (2.38, -4.7, f + 1.05), P["glass"])
    # mounted fish and hanging net
    mb.ico(0.3, (x0 + 0.15, 0, f + 3.0), P["fish"], scale=(0.4, 3.2, 1.0))
    mb.box((0.06, 1.6, 0.45), (x0 + 0.13, 0, f + 3.0), lt)
    for k in range(3):
        mb.cyl(0.3, 0.1, 0.25, (-1.5 + k * 1.6, 0, f + H - 0.35), P["metal_dark"], seg=8)
        mb.ico(0.1, (-1.5 + k * 1.6, 0, f + H - 0.5), P["lamp_glow"])
    return mb


def rod_sign(P):
    """Roof-top sign: a big fish on a hook."""
    mb = MB()
    body = [(-2.0, 0, 0), (-0.6, 0, 0.9), (1.2, 0, 0.7), (1.9, 0, 0), (1.2, 0, -0.7), (-0.6, 0, -0.9)]
    tail = [(-1.8, 0, 0), (-3.0, 0, 0.9), (-2.7, 0, 0), (-3.0, 0, -0.9)]
    for pts, m in ((body, P["teal"]), (tail, P["teal"])):
        back = [(x, 0.15, z) for x, _, z in pts]
        n = len(pts)
        faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + \
                [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        mb.poly(pts + back, faces, m)
    mb.ico(0.15, (1.2, -0.03, 0.2), P["white"])
    mb.box((0.5, 0.16, 0.08), (0.5, 0.07, -0.55), P["yellow"])
    mb.cyl(0.05, 0.05, 1.8, (-0.8, 0.07, -1.6), P["metal_dark"], seg=4)
    mb.cyl(0.05, 0.05, 1.8, (0.8, 0.07, -1.6), P["metal_dark"], seg=4)
    return mb


def crab_pots(P, n=6, seed=0):
    mb = MB()
    rnd = random.Random(seed)
    for k in range(n):
        x, y, z = (k % 3) * 0.95, (k // 3) * 0.0, (k // 3) * 0.62
        mb.box((0.9, 0.7, 0.05), (x, y, z + 0.03), P["wood_dark"])
        mb.box((0.9, 0.7, 0.05), (x, y, z + 0.57), P["wood_dark"])
        for sx in (-0.42, 0.42):
            for sy in (-0.32, 0.32):
                mb.box((0.05, 0.05, 0.6), (x + sx, y + sy, z + 0.3), P["wood_dark"])
        for k2 in range(2):
            mb.box((0.88, 0.02, 0.02), (x, y - 0.33, z + 0.2 + k2 * 0.2), P["rope"])
            mb.box((0.88, 0.02, 0.02), (x, y + 0.33, z + 0.2 + k2 * 0.2), P["rope"])
        mb.ico(0.12, (x + 0.2, y - 0.4, z + 0.5), P["fabric_orange"])
    return mb


def build(P, A, center):
    cx, cy = center
    root_c, C, root = island_setup("40_RodShop_Island", PREFIX, center)
    W = lambda lx, ly: Vector((cx + lx, cy + ly, 0))

    terrain = build_terrain("Rod_Terrain", center, shape(), P, C["Terrain"], root, cell=2.2, kind="rocky")
    g = Ground([terrain])
    fwd = Vector((math.cos(FACING), math.sin(FACING), 0))
    side = Vector((-fwd.y, fwd.x, 0))

    # --- shop
    sp = W(*SHOP_LOCAL)
    sz = g.z(sp.x, sp.y, SHOP_Z)
    shop = tackle_shop(P).build("Rod_TackleShop", C["Buildings"], root)
    shop.location = (sp.x, sp.y, sz)
    shop.rotation_euler = (0, 0, FACING)
    text_mesh("Rod_Sign_BaitTackle", "BAIT & TACKLE", 0.5, tuple(sp + fwd * 4.15 + Vector((0, 0, sz + 3.55))),
              (math.pi / 2, 0, FACING + math.pi / 2), P["white"], C["Buildings"], root, extrude=0.04)
    sign = rod_sign(P).build("Rod_Sign_Fish", C["Buildings"], root)
    sign.location = tuple(sp + fwd * 0.4 + Vector((0, 0, sz + 0.5 + 3.4 + 3.2)))
    sign.rotation_euler = (0, 0, FACING - math.pi / 2)
    # Mark, the rod seller, behind the L-counter facing into the shop
    place_npc("Mark", P, tuple(sp - fwd * 0.4 - side * 4.3 + Vector((0, 0, sz + 0.5))), FACING + math.pi / 2,
              C["NPCs"], root)
    for k, y in enumerate((-1.6, 1.6)):
        p = sp + side * y
        light("Rod_Shop_InteriorLight_%d" % (k + 1), 'POINT', 90, (p.x, p.y, sz + 3.3), C["Lights"], root,
              color=(1.0, 0.82, 0.55), shadow_soft_size=0.3)
    p = sp + fwd * 6.0
    light("Rod_Porch_Light", 'POINT', 40, (p.x, p.y, sz + 3.5), C["Lights"], root, color=(1.0, 0.8, 0.5))

    # --- dock: zig-zag boardwalk with a covered net shed on the end
    front = sp + fwd * 7.0
    shore = g.shore((front.x, front.y), FACING)
    start = shore - fwd * 2.5
    dock = Dock("Rod_Dock", (start.x, start.y, 0), FACING, g, P, plank_m="wood_grey", pile_m="wood_dark")
    dock.rect(0, 12, -1.1, 1.1, rail=True)
    dock.rect(12, 15, -1.1, 7.0)
    dock.rect(15, 26, 4.0, 7.0)
    dock.rect(26, 31, 0.0, 9.0)
    dock.cleats([(30.6, 0.4), (30.6, 8.6), (20, 6.9), (24, 6.9)])
    dock.tires([(31.1, 2.5), (31.1, 6.5), (20, 7.5)])
    dock.build(C["Dock"], root)
    instance("Rod_FuelPump", A["fuel_red"], dock.w(29.5, 1.2), C["Dock"], root, rot=(0, 0, FACING + math.pi / 2))
    instance("Rod_Dock_Lamp_A", A["lamp"], dock.w(26.4, 8.6), C["Dock"], root)
    instance("Rod_Dock_Lamp_B", A["lamp"], dock.w(12.4, 6.6), C["Dock"], root)
    for k, (u, v) in enumerate([(26.4, 8.6), (12.4, 6.6)]):
        light("Rod_Dock_LampLight_%d" % (k + 1), 'POINT', 70, tuple(dock.w(u, v, DOCK_DECK_Z + 3.4)), C["Lights"], root,
              color=(1.0, 0.85, 0.6))
    # small open shed with nets on the dock head
    mb = MB()
    for u in (26.4, 29.0):
        for v in (5.6, 8.6):
            mb.box((0.18, 0.18, 2.6), dock.w(u, v, DOCK_DECK_Z + 1.3), P["wood_dark"])
    mb.box((3.6, 3.8, 0.12), dock.w(27.7, 7.1, DOCK_DECK_Z + 2.7), P["roof_dark"], rot=(0.12, 0, FACING))
    mb.build("Rod_Dock_NetShed", C["Dock"], root)
    instance("Rod_Dock_NetRack", A["net"], dock.w(27.7, 8.7), C["Props"], root, rot=(0, 0, FACING))
    pots = crab_pots(P, 6, 1).build("Rod_Dock_CrabPots", C["Props"], root)
    pots.location = dock.w(16.5, 5.2)
    pots.rotation_euler = (0, 0, FACING)
    for k, (u, v, a) in enumerate([(14.0, 0.0, "barrel_wood"), (14.0, -0.65, "barrel_wood"), (22.5, 6.3, "barrel_red"),
                                   (13.2, 5.8, "crate"), (13.2, 6.5, "crate")]):
        instance("Rod_Dock_Prop_%d" % (k + 1), A[a], dock.w(u, v), C["Props"], root, rot=(0, 0, FACING + k))

    # --- outside the shop: rod rack, coolers, bait tank, benches, an old rowboat on the shore
    mb = MB()
    rack = sp + fwd * 5.4 + side * 4.4
    rz = g.z(rack.x, rack.y, sz)
    for s in (-1.2, 1.2):
        q = rack + side * s
        mb.box((0.12, 0.12, 1.4), (q.x, q.y, rz + 0.7), P["wood_dark"])
    a, b = rack - side * 1.25, rack + side * 1.25
    mb.box_between((a.x, a.y, rz + 1.2), (b.x, b.y, rz + 1.2), 0.12, 0.12, P["wood_dark"])
    mb.box_between((a.x, a.y, rz + 0.25), (b.x, b.y, rz + 0.25), 0.25, 0.1, P["wood_dark"])
    for k in range(8):
        q = rack + side * (-1.0 + k * 0.28)
        mb.cyl_between((q.x, q.y, rz + 0.3), (q.x - fwd.x * 0.35, q.y - fwd.y * 0.35, rz + 3.0), 0.025, 0.008, P["black"], seg=4)
    tank = sp + fwd * 5.6 - side * 3.6
    tz = g.z(tank.x, tank.y, sz)
    mb.box((1.6, 0.9, 0.8), (tank.x, tank.y, tz + 0.4), P["blue"], rot=(0, 0, FACING))
    water = mat("M_BaitTankWater", (0.2, 0.45, 0.5), 0.05)
    mb.box((1.5, 0.8, 0.05), (tank.x, tank.y, tz + 0.78), water, rot=(0, 0, FACING))
    for k in range(2):
        q = sp + fwd * 5.2 + side * (1.5 + k * 0.9)
        qz = g.z(q.x, q.y, sz)
        mb.box((0.8, 0.5, 0.5), (q.x, q.y, qz + 0.25), P["white"] if k else P["red"], rot=(0, 0, FACING))
        mb.box((0.82, 0.52, 0.08), (q.x, q.y, qz + 0.52), P["white"], rot=(0, 0, FACING))
    mb.build("Rod_Shop_OutdoorProps", C["Props"], root)
    q = sp + fwd * 4.7 + side * 1.2
    instance("Rod_Porch_Bench", A["bench"], (q.x, q.y, sz + 0.5), C["Props"], root, rot=(0, 0, FACING + math.pi / 2))
    row = sp + fwd * 9.0 - side * 9.0
    instance("Rod_Rowboat_Beached", boat_mesh("Rod_Rowboat_Beached", P, 3.6, 1.4, "wood", "white", "none"),
             (row.x, row.y, g.z(row.x, row.y, 1.0) + 0.35), C["Props"], root, rot=(0.12, 0.08, FACING + 2.4))

    # --- vegetation and rocks: dense pines on the hill, dark rocks on the cliffs
    avoid = [(sp.x, sp.y, 9.5), (start.x, start.y, 3.5), (rack.x, rack.y, 2.0), (row.x, row.y, 3.0)]
    pines = scatter(g, W(-6, 6), 34, 30, 401, 2.5, 30, 0.75, avoid, 4.0)
    place_many("Rod_Pine", A["pine"], pines, C["Vegetation"], root, 1, (0.7, 1.2))
    bushes = scatter(g, center, 36, 30, 402, 1.8, 25, 0.7, avoid, 2.0)
    place_many("Rod_Bush", A["bush_dark"], bushes, C["Vegetation"], root, 2, (0.6, 1.3))
    cliffs = scatter(g, W(-14, 14), 26, 30, 403, -2.0, 12, 0.0, avoid, 2.5)
    place_many("Rod_Rock_Cliff", A["rock_dark"] + A["rock"][1:3], cliffs, C["Vegetation"], root, 3, (1.0, 2.2), 0.6)
    shore = scatter(g, center, 48, 30, 404, -1.5, 1.2, 0.3, avoid + [(dock.w(15, 3).x, dock.w(15, 3).y, 17)], 2.0)
    place_many("Rod_Rock_Shore", A["rock_dark"] + A["rock"][:1], shore, C["Vegetation"], root, 4, (0.5, 1.3), 0.4)
    return root
