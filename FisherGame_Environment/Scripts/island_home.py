"""Island 1 - Home Island: the player's quiet tropical island with a beach house."""
import bpy, math, random
from mathutils import Vector
from fg_lib import (MB, IslandShape, build_terrain, Ground, island_setup, place_many, scatter,
                    instance, light, link, mat, DOCK_DECK_Z)
from fg_assets import Dock, place_npc

PREFIX = "Home"
FACING = math.radians(33)          # towards the middle of the world
HOUSE_LOCAL = (13.0, 6.0)


def shape():
    return IslandShape(
        lobes=[(0, 0, 40), (24, -16, 25), (-22, 20, 24), (-30, -18, 18)],
        peaks=[(-16, 12, 26, 7.5), (-30, -16, 14, 4.0), (6, -24, 14, 2.5)],
        cliffs=[(math.radians(200), math.radians(28), 6.0)],
        pads=[(HOUSE_LOCAL[0], HOUSE_LOCAL[1], 7.5, 2.2)],
        seed=11, irregular=0.16, beach_h=1.5, bumps=1.0)


def beach_house(P):
    """Raised timber beach house, front (+X) with a covered porch. Origin = ground level."""
    mb = MB()
    s = 0.9                       # stilt height
    f = s + 0.2                   # floor top
    H = 2.8
    wood, trim, dark = P["wood_light"], P["white"], P["wood_dark"]
    shutter = P["teal"]
    for x in (-2.8, -0.2, 2.4, 4.9):
        for y in (-3.6, 0.0, 3.6):
            mb.box((0.26, 0.26, s + 0.6), (x, y, (s - 0.6) / 2), dark)
    mb.box((8.1, 7.7, 0.2), (1.05, 0, s + 0.1), P["wood"])
    # walls with clapboard lines
    walls = [((5.0, 0.2, H), (0, -3.5, f + H / 2)), ((5.0, 0.2, H), (0, 3.5, f + H / 2)),
             ((0.2, 7.0, H), (-2.5, 0, f + H / 2)), ((0.2, 7.0, H), (2.5, 0, f + H / 2))]
    for size, loc in walls:
        mb.box(size, loc, wood)
        for k in range(1, 7):
            z = f + k * 0.4
            sx, sy = size[0] + 0.04, size[1] + 0.04
            mb.box((sx, sy, 0.05), (loc[0], loc[1], z), P["wood"])
    for x in (-2.5, 2.5):
        for y in (-3.5, 3.5):
            mb.box((0.28, 0.28, H), (x, y, f + H / 2), trim)

    def window(cx, cy, axis, w=1.2, h=1.0, z0=f + 1.0):
        n = Vector((1, 0, 0)) if axis == 'x' else Vector((0, 1, 0))
        sgn = 1 if (cx if axis == 'x' else cy) > 0 else -1
        off = n * sgn * 0.12
        c = Vector((cx, cy, z0 + h / 2)) + off
        if axis == 'x':
            mb.box((0.06, w, h), c, P["glass"])
            mb.box((0.1, w + 0.2, 0.1), c + Vector((0, 0, h / 2)), trim)
            mb.box((0.1, w + 0.2, 0.12), c - Vector((0, 0, h / 2)), trim)
            for sy in (-1, 1):
                mb.box((0.06, 0.55, h + 0.1), c + Vector((0.03 * sgn, sy * (w / 2 + 0.35), 0)), shutter)
        else:
            mb.box((w, 0.06, h), c, P["glass"])
            mb.box((w + 0.2, 0.1, 0.1), c + Vector((0, 0, h / 2)), trim)
            mb.box((w + 0.2, 0.1, 0.12), c - Vector((0, 0, h / 2)), trim)
            for sx in (-1, 1):
                mb.box((0.55, 0.06, h + 0.1), c + Vector((sx * (w / 2 + 0.35), 0.03 * sgn, 0)), shutter)

    window(2.5, -2.0, 'x'); window(2.5, 2.0, 'x')
    window(-2.5, 0.0, 'x', w=1.6)
    window(0.0, -3.5, 'y'); window(0.0, 3.5, 'y')
    # door
    mb.box((0.08, 1.0, 2.1), (2.62, 0, f + 1.05), P["teal"])
    mb.box((0.1, 1.25, 0.12), (2.64, 0, f + 2.16), trim)
    for y in (-0.56, 0.56):
        mb.box((0.1, 0.12, 2.15), (2.64, y, f + 1.07), trim)
    mb.ico(0.05, (2.7, 0.35, f + 1.0), P["metal"])
    # roofs (thatch) and ridge beam
    mb.gable_roof(5.0, 7.0, 2.1, (0, 0, f + H), P["thatch"], overhang=0.7, thick=0.25)
    mb.box((0.2, 8.6, 0.2), (0, 0, f + H + 2.05), P["wood_dark"])
    porch_roof = [(2.3, -4.1, f + H + 0.25), (2.3, 4.1, f + H + 0.25), (5.6, 4.1, f + H - 0.45), (5.6, -4.1, f + H - 0.45)]
    pr = porch_roof + [(p[0], p[1], p[2] - 0.2) for p in porch_roof]
    mb.poly(pr, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], P["thatch"])
    # porch posts and rails (gap for the steps)
    for y in (-3.6, -1.0, 1.0, 3.6):
        mb.box((0.18, 0.18, H - 0.3), (4.95, y, f + (H - 0.3) / 2), trim)
    for (y0, y1) in ((-3.6, -1.0), (1.0, 3.6)):
        mb.box_between((4.95, y0, f + 0.95), (4.95, y1, f + 0.95), 0.1, 0.1, trim)
        for k in range(1, 6):
            y = y0 + (y1 - y0) * k / 6
            mb.box((0.06, 0.06, 0.9), (4.95, y, f + 0.48), trim)
    for y in (-3.6, 3.6):
        mb.box_between((2.6, y, f + 0.95), (4.95, y, f + 0.95), 0.1, 0.1, trim)
    # steps down to the sand
    for k in range(4):
        mb.box((0.35, 1.8, 0.1), (5.25 + k * 0.35, 0, f - 0.25 - k * 0.27), P["wood"])
    for y in (-0.95, 0.95):
        mb.box_between((5.05, y, f - 0.1), (6.6, y, -0.1), 0.1, 0.25, P["wood_dark"])
    # porch furniture: bench, table, lanterns, hanging plants
    mb.box((0.5, 1.6, 0.08), (3.4, -2.5, f + 0.45), P["wood"])
    for y in (-3.2, -1.8):
        mb.box((0.45, 0.08, 0.45), (3.4, y, f + 0.22), P["wood_dark"])
    mb.cyl(0.4, 0.4, 0.06, (3.6, 2.2, f + 0.7), P["wood"], seg=8)
    mb.cyl(0.06, 0.06, 0.7, (3.6, 2.2, f + 0.35), P["wood_dark"], seg=6)
    for y in (-1.2, 1.2):
        mb.cyl(0.1, 0.1, 0.25, (4.95, y, f + 2.1), P["lamp_glow"], seg=6)
    for y in (-2.3, 2.6):
        mb.cyl(0.18, 0.12, 0.22, (4.6, y, f + 1.95), P["roof_red"], seg=6)
        mb.ico(0.25, (4.6, y, f + 2.12), P["bush"], sub=1)
    # side water tank + outdoor shower at the back
    mb.cyl(0.55, 0.55, 1.4, (-3.4, 2.6, s + 0.9), P["green_paint"], seg=10)
    mb.box((0.15, 0.15, 2.4), (-3.6, -2.8, 1.2 - 0.3), P["wood_dark"])
    mb.box((0.6, 0.08, 0.06), (-3.35, -2.8, 2.05), P["metal"])
    return mb


def hammock(P, p1, p2, height=1.3):
    mb = MB()
    p1, p2 = Vector(p1), Vector(p2)
    d = (p2 - p1)
    side = Vector((-d.y, d.x, 0)).normalized()
    pts, faces = [], []
    n = 10
    for k in range(n + 1):
        t = k / n
        c = p1.lerp(p2, t)
        c.z = p1.z + height - 0.6 * math.sin(math.pi * t)
        w = 0.15 + 0.5 * math.sin(math.pi * t)
        pts += [c + side * w, c - side * w + Vector((0, 0, 0.02))]
    for k in range(n):
        faces.append((k * 2, k * 2 + 2, k * 2 + 3, k * 2 + 1))
    mb.poly(pts, faces, P["fabric_orange"])
    return mb


def campfire(P, loc):
    mb = MB()
    x, y, z = loc
    for k in range(9):
        a = 2 * math.pi * k / 9
        mb.ico(0.22, (x + math.cos(a) * 0.75, y + math.sin(a) * 0.75, z + 0.08), P["rock"], scale=(1, 1, 0.7), jitter=0.25, seed=k)
    for k in range(3):
        a = 2 * math.pi * k / 3
        mb.cyl_between((x + math.cos(a) * 0.5, y + math.sin(a) * 0.5, z + 0.05), (x, y, z + 0.4), 0.07, 0.06, P["wood_dark"])
    fire = mat("M_Fire", (1.0, 0.45, 0.1), 0.5, emit=(1.0, 0.45, 0.12), emit_strength=8.0)
    mb.cyl(0.28, 0.02, 0.6, (x, y, z + 0.35), fire, seg=5)
    for k in range(4):
        a = 2 * math.pi * k / 4 + 0.6
        mb.cyl_between((x + math.cos(a) * 1.4, y + math.sin(a) * 1.4, z + 0.2), (x + math.cos(a) * 1.4 + math.cos(a + 1.57) * 0.9, y + math.sin(a) * 1.4 + math.sin(a + 1.57) * 0.9, z + 0.2), 0.16, 0.16, P["wood"], seg=6)
    return mb


def build(P, A, center):
    cx, cy = center
    root_c, C, root = island_setup("10_Home_Island", PREFIX, center)
    W = lambda lx, ly: (cx + lx, cy + ly)

    terrain = build_terrain("Home_Terrain", center, shape(), P, C["Terrain"], root, cell=2.6, kind="tropical")
    g = Ground([terrain])

    # --- beach house
    hx, hy = W(*HOUSE_LOCAL)
    hz = g.z(hx, hy, 2.0)
    house = beach_house(P).build("Home_BeachHouse", C["Buildings"], root)
    house.location = (hx, hy, hz)
    house.rotation_euler = (0, 0, FACING)
    fwd = Vector((math.cos(FACING), math.sin(FACING), 0))
    side = Vector((-fwd.y, fwd.x, 0))
    light("Home_House_InteriorLight", 'POINT', 60, (hx, hy, hz + 2.6), C["Lights"], root,
          color=(1.0, 0.8, 0.55), shadow_soft_size=0.4)
    light("Home_Porch_Light", 'POINT', 25, tuple(Vector((hx, hy, hz + 3.0)) + fwd * 4.6), C["Lights"], root,
          color=(1.0, 0.75, 0.45), shadow_soft_size=0.2)

    # the player, standing on the sand next to the porch steps, looking towards the dock
    pp = Vector((hx, hy, 0)) + fwd * 7.2 + side * 2.6
    place_npc("Player", P, (pp.x, pp.y, g.z(pp.x, pp.y, hz)), FACING, C["NPCs"], root,
              name="Player_Model", spot_name="Player_Spawn")

    # --- private dock straight out from the house
    steps = Vector((hx, hy, 0)) + fwd * 6.8
    shore = g.shore((steps.x, steps.y), FACING)
    start = shore - fwd * 3.0
    dock = Dock("Home_Dock", (start.x, start.y, 0), FACING, g, P)
    dock.rect(0, 22, -1.2, 1.2)
    dock.rect(22, 26, -5.0, 5.0)                       # T-head
    dock.rect(9, 12, 1.2, 7.0)                         # side finger for the player's boat
    dock.cleats([(25.6, -4.5), (25.6, 4.5), (11.6, 6.5), (9.4, 6.5), (16, -1.1)])
    dock.tires([(26.1, -2.5), (26.1, 2.5), (12.1, 4.0)])
    dock.build(C["Dock"], root)
    pump = instance("Home_FuelPump", A["fuel_red"], dock.w(24.2, -3.8), C["Dock"], root, rot=(0, 0, FACING + math.pi / 2))
    instance("Home_Dock_LifeRing", A["life_ring"], dock.w(21.6, 1.05), C["Dock"], root, rot=(0, 0, FACING))
    instance("Home_Dock_Lamp_A", A["lamp"], dock.w(25.7, 4.7), C["Dock"], root)
    instance("Home_Dock_Lamp_B", A["lamp"], dock.w(0.5, -1.1), C["Dock"], root)
    light("Home_Dock_LampLight", 'POINT', 80, tuple(dock.w(25.7, 4.7, DOCK_DECK_Z + 3.4)), C["Lights"], root,
          color=(1.0, 0.85, 0.6))
    for k, (u, v) in enumerate([(23.0, 4.2), (23.6, 3.6), (1.5, 0.8)]):
        instance("Home_Dock_Crate_%d" % (k + 1), A["crate"] if k < 2 else A["barrel_red"], dock.w(u, v), C["Props"], root,
                 rot=(0, 0, FACING + k * 0.4))

    # --- stepping-stone path from the porch steps to the dock
    mb = MB()
    a, b = steps + fwd * 0.4, Vector((start.x, start.y, 0))
    n = max(2, int((b - a).length / 1.1))
    rnd = random.Random(4)
    for k in range(n + 1):
        p = a.lerp(b, k / n) + side * rnd.uniform(-0.25, 0.25)
        z = g.z(p.x, p.y, 1.5)
        mb.cyl(0.42, 0.42, 0.12, (p.x, p.y, z + 0.02), P["rock"], seg=7, rot=(0, 0, rnd.random()))
    mb.build("Home_Path_Stones", C["Props"], root)

    # message in a bottle washed up next to the dock: start of the questline (see QUESTLINE.md)
    bp = Vector((start.x, start.y, 0)) - side * 4.5 + fwd * 1.5
    bz = g.z(bp.x, bp.y, 0.8)
    bottle_glass = mat("M_BottleGlass", (0.35, 0.65, 0.45), 0.1, alpha=0.6)
    mb = MB()
    mb.cyl(0.07, 0.07, 0.24, (0, 0, 0), bottle_glass, rot=(0, math.pi / 2, 0), seg=8)
    mb.cyl(0.07, 0.025, 0.08, (0.16, 0, 0), bottle_glass, rot=(0, math.pi / 2, 0), seg=8)
    mb.cyl(0.026, 0.026, 0.05, (0.22, 0, 0), P["wood_light"], rot=(0, math.pi / 2, 0), seg=6)
    mb.cyl(0.04, 0.04, 0.16, (-0.01, 0, 0), P["wood_light"], rot=(0, math.pi / 2, 0), seg=6)
    bottle = mb.build("Home_MessageBottle", C["Props"], root)
    bottle.location = (bp.x, bp.y, bz + 0.06)
    bottle.rotation_euler = (0, 0.1, FACING + 0.8)

    # --- beach life: chairs, umbrella, hammock between two palms, campfire, surfboards
    beach = Vector((hx, hy, 0)) + fwd * 9.0 + side * 9.0
    for k, off in enumerate((0.0, 1.4)):
        p = beach + side * off
        instance("Home_DeckChair_%d" % (k + 1), A["chair"], (p.x, p.y, g.z(p.x, p.y, 1.0)), C["Props"], root,
                 rot=(0, 0, FACING + math.pi + 0.1 * k))
    p = beach + side * 0.7 + fwd * 1.4
    instance("Home_Umbrella", A["umbrella"], (p.x, p.y, g.z(p.x, p.y, 1.0)), C["Props"], root)
    h1 = Vector((hx, hy, 0)) - side * 9.0 + fwd * 3.0
    h2 = h1 - side * 4.2 + fwd * 1.5
    for k, h in enumerate((h1, h2)):
        h.z = g.z(h.x, h.y, 1.5)
        instance("Home_Palm_Hammock_%d" % (k + 1), A["palm"][k], tuple(h), C["Vegetation"], root, rot=(0, 0, k * 2.0))
    hammock(P, h1 + Vector((0, 0, 0.3)), h2 + Vector((0, 0, 0.3))).build("Home_Hammock", C["Props"], root)
    fire = Vector((hx, hy, 0)) + fwd * 5.0 - side * 7.5
    fz = g.z(fire.x, fire.y, 1.5)
    campfire(P, (fire.x, fire.y, fz)).build("Home_Campfire", C["Props"], root)
    light("Home_Campfire_Light", 'POINT', 120, (fire.x, fire.y, fz + 0.8), C["Lights"], root, color=(1.0, 0.5, 0.15))
    mb = MB()
    for k, col in enumerate(("yellow", "teal")):
        p = Vector((hx, hy, 0)) - fwd * 1.0 + side * (4.6 + k * 0.6)
        z = g.z(p.x, p.y, 2)
        mb.ico(1.0, (p.x, p.y, z + 1.0), P[col], scale=(0.28, 0.06, 1.0), rot=(0.12, 0, FACING), sub=2)
    mb.build("Home_Surfboards", C["Props"], root)

    # --- vegetation and rocks
    house_avoid = [(hx, hy, 9.0), (start.x, start.y, 4.0), (beach.x, beach.y, 3.5), (fire.x, fire.y, 3.5),
                   (h1.x, h1.y, 2.5), (h2.x, h2.y, 2.5)]
    path_pts = [(a.lerp(b, t).x, a.lerp(b, t).y, 2.0) for t in (0.0, 0.33, 0.66, 1.0)]
    avoid = house_avoid + path_pts
    palms = scatter(g, center, 62, 34, 101, 1.3, 9, 0.8, avoid, 5.5)
    place_many("Home_Palm", A["palm"], palms, C["Vegetation"], root, 1, (0.85, 1.25))
    bushes = scatter(g, center, 60, 45, 102, 1.6, 14, 0.75, avoid, 2.5)
    place_many("Home_Bush", A["bush"], bushes, C["Vegetation"], root, 2, (0.7, 1.4))
    trees = scatter(g, (cx - 16, cy + 10), 22, 8, 105, 4, 14, 0.8, avoid, 6)
    place_many("Home_Tree", A["tree"], trees, C["Vegetation"], root, 5, (0.9, 1.3))
    shore_rocks = scatter(g, center, 70, 40, 103, -1.5, 1.0, 0.4, avoid + [(dock.w(12, 0).x, dock.w(12, 0).y, 14)], 2.0)
    place_many("Home_Rock_Shore", A["rock"] + A["rock_warm"][:1], shore_rocks, C["Vegetation"], root, 3, (0.5, 1.3), 0.4)
    cliff_rocks = scatter(g, (cx - 40, cy - 12), 22, 14, 104, -1.0, 8, 0.0, avoid, 3.0)
    place_many("Home_Rock_Cliff", A["rock_warm"], cliff_rocks, C["Vegetation"], root, 4, (1.0, 2.0), 0.6)
    return root
