"""Island 3 - Boat Dealer Island: the largest island, a modern glass showroom with a marina."""
import bpy, math, random
from mathutils import Vector
from fg_lib import (MB, IslandShape, build_terrain, Ground, island_setup, place_many, scatter,
                    instance, light, link, mat, text_mesh, DOCK_DECK_Z)
from fg_assets import Dock, boat_mesh, place_npc

PREFIX = "Dealer"
FACING = math.radians(-135)                 # marina faces the middle of the world
SHOWROOM_LOCAL = (-24.0, -22.0)
PLAZA_Z = 2.4


def shape():
    return IslandShape(
        lobes=[(0, 0, 58), (-28, -26, 34), (34, -6, 34), (8, 40, 30), (-38, 18, 24)],
        peaks=[(22, 26, 30, 9.0), (36, -4, 18, 5.0), (-34, 24, 16, 4.0)],
        cliffs=[(math.radians(40), math.radians(35), 7.0)],
        pads=[(SHOWROOM_LOCAL[0], SHOWROOM_LOCAL[1], 16.0, PLAZA_Z)],
        seed=37, irregular=0.14, beach_h=1.6, bumps=0.9, seabed_slope=0.3)


def showroom(P):
    """Modern showroom: concrete deck, glass curtain walls, cantilevered roof. Front = +X."""
    mb = MB()
    L, Wd, H = 22.0, 14.0, 5.2
    conc, dark, glass = P["concrete"], P["metal_dark"], P["glass"]
    mb.box((L + 6, Wd + 6, 0.5), (1.5, 0, 0.0), conc)                 # plinth incl. front terrace
    mb.box((L, Wd, 0.1), (0, 0, 0.3), P["white"])                      # polished floor
    # back wall (solid, with offices) and side walls of glass
    mb.box((0.4, Wd, H), (-L / 2, 0, 0.25 + H / 2), P["navy"])
    mb.box((6.0, 0.3, H), (-L / 2 + 3.0, -Wd / 2 + 0.15, 0.25 + H / 2), P["navy"])
    for x in [(-L / 2 + 6) + i * ((L - 6) / 5) for i in range(6)]:
        mb.box((0.18, 0.18, H), (x, -Wd / 2, 0.25 + H / 2), dark)
        mb.box((0.18, 0.18, H), (x, Wd / 2, 0.25 + H / 2), dark)
    mb.box((L - 6, 0.06, H), (3.0, -Wd / 2, 0.25 + H / 2), glass)
    mb.box((L, 0.06, H), (0, Wd / 2, 0.25 + H / 2), glass)
    # front glass facade with a wide sliding opening in the middle
    for y in [-Wd / 2 + i * (Wd / 6) for i in range(7)]:
        mb.box((0.18, 0.18, H), (L / 2, y, 0.25 + H / 2), dark)
    for y0, y1 in ((-Wd / 2, -2.5), (2.5, Wd / 2)):
        mb.box((0.06, y1 - y0, H), (L / 2, (y0 + y1) / 2, 0.25 + H / 2), glass)
    mb.box((0.06, 5.0, H - 3.2), (L / 2, 0, 0.25 + 3.2 + (H - 3.2) / 2), glass)
    mb.box((0.25, 5.2, 0.2), (L / 2, 0, 0.25 + 3.2), dark)
    # roof slab with deep overhang + fascia
    mb.box((L + 5, Wd + 3, 0.45), (1.8, 0, 0.25 + H + 0.22), P["white"])
    mb.box((L + 5.1, Wd + 3.1, 0.12), (1.8, 0, 0.25 + H + 0.5), dark)
    for y in (-Wd / 2 - 1.2, Wd / 2 + 1.2):
        mb.box((0.25, 0.25, H), (L / 2 + 3.6, y, 0.25 + H / 2), dark)
    # display platforms (boats placed on top as separate objects)
    for x, y in ((-3.5, -3.2), (-3.5, 3.4), (5.0, 0.0)):
        mb.cyl(2.6, 2.8, 0.3, (x, y, 0.45), P["white"], seg=16)
        mb.cyl(2.85, 2.85, 0.05, (x, y, 0.32), P["blue"], seg=16)
    # sales desk, lounge, plants
    mb.box((0.8, 3.6, 1.05), (-L / 2 + 2.2, -3.5, 0.8), P["white"])
    mb.box((1.0, 3.8, 0.06), (-L / 2 + 2.2, -3.5, 1.35), P["wood_light"])
    mb.box((0.06, 3.0, 1.0), (-L / 2 + 0.25, -3.5, 3.0), P["window_lit"])
    for k, (x, y) in enumerate(((-L / 2 + 3, 4.0), (-L / 2 + 3, 5.5))):
        mb.box((1.6, 0.8, 0.45), (x, y, 0.55), P["fabric_blue"])
        mb.box((1.6, 0.2, 0.5), (x, y + 0.4, 0.9), P["fabric_blue"])
    mb.box((0.9, 0.9, 0.4), (-L / 2 + 4.6, 4.8, 0.5), P["wood_light"])
    for x, y in ((L / 2 - 0.8, -Wd / 2 + 0.8), (L / 2 - 0.8, Wd / 2 - 0.8), (-L / 2 + 0.8, Wd / 2 - 0.8)):
        mb.cyl(0.4, 0.3, 0.6, (x, y, 0.6), P["roof_dark"], seg=8)
        mb.ico(0.6, (x, y, 1.4), P["leaf"], scale=(1, 1, 1.4), jitter=0.2, seed=int(x * 3))
    # ceiling lights
    for x in (-6, 0, 6):
        for y in (-4, 0, 4):
            mb.box((1.4, 0.25, 0.08), (x, y, 0.25 + H - 0.08), P["lamp_glow"])
    return mb


def build(P, A, center):
    cx, cy = center
    root_c, C, root = island_setup("30_BoatDealer_Island", PREFIX, center)
    W = lambda lx, ly: Vector((cx + lx, cy + ly, 0))

    terrain = build_terrain("Dealer_Terrain", center, shape(), P, C["Terrain"], root, cell=3.0, kind="tropical")
    g = Ground([terrain])
    fwd = Vector((math.cos(FACING), math.sin(FACING), 0))
    side = Vector((-fwd.y, fwd.x, 0))

    # --- showroom
    sp = W(*SHOWROOM_LOCAL)
    sz = g.z(sp.x, sp.y, PLAZA_Z)
    sr = showroom(P).build("Dealer_Showroom", C["Buildings"], root)
    sr.location = (sp.x, sp.y, sz)
    sr.rotation_euler = (0, 0, FACING)
    text_mesh("Dealer_Sign_Roof", "ISLAND BOATS", 1.6, tuple(sp + fwd * 14.5 + Vector((0, 0, sz + 6.45))),
              (math.pi / 2, 0, FACING + math.pi / 2), P["navy"], C["Buildings"], root, extrude=0.12)
    showroom_boats = [((-3.5, -3.2), 6.5, "white", "navy", "cruiser"), ((-3.5, 3.4), 5.5, "red", "white", "motor"),
                      ((5.0, 0.0), 6.0, "navy", "white", "motor")]
    for k, ((lx, ly), L, hull, stripe, style) in enumerate(showroom_boats):
        p = sp + fwd * lx + side * ly
        name = "Dealer_Showroom_Boat_%d" % (k + 1)
        instance(name, boat_mesh(name, P, L, L * 0.38, hull, stripe, style), (p.x, p.y, sz + 1.55), C["Props"], root,
                 rot=(0, 0, FACING + 0.5 + k * 0.6))
    # Emre, the boat dealer, behind the sales desk facing the entrance
    p = sp - fwd * 9.7 - side * 3.5
    place_npc("Emre", P, (p.x, p.y, sz + 0.35), FACING, C["NPCs"], root)
    for k, (x, y) in enumerate(((-6, -4), (0, 0), (6, 4))):
        p = sp + fwd * x + side * y
        light("Dealer_Showroom_Light_%d" % (k + 1), 'AREA', 400, (p.x, p.y, sz + 5.0), C["Lights"], root,
              color=(1.0, 0.97, 0.92), size=3.0)

    # --- marina: main pier from the showroom terrace with four finger berths and a fuel berth
    front = sp + fwd * 15.0
    shore = g.shore((front.x, front.y), FACING)
    start = shore - fwd * 3.0
    dock = Dock("Dealer_Marina", (start.x, start.y, 0), FACING, g, P, plank_m="wood_light", pile_m="concrete")
    fingers = (18, 28, 38, 48)
    dock.rect(0, 54, -1.6, 1.6, rail=False)
    for u in fingers:
        dock.rect(u, u + 1.6, 1.6, 13.0, posts=True)       # finger berths on the left
        dock.rect(u, u + 1.6, -13.0, -1.6, posts=True)     # and on the right
    dock.rect(54, 58, -8.0, 8.0)                           # fuel berth head
    dock.cleats([(57.6, -7.5), (57.6, 7.5), (57.6, 0)] + [(u + 0.8, s * 12.5) for u in fingers for s in (-1, 1)])
    dock.build(C["Dock"], root)
    instance("Dealer_FuelPump_A", A["fuel_yellow"], dock.w(56.2, -6.5), C["Dock"], root, rot=(0, 0, FACING + math.pi / 2))
    instance("Dealer_FuelPump_B", A["fuel_yellow"], dock.w(56.2, 6.5), C["Dock"], root, rot=(0, 0, FACING + math.pi / 2))
    mb = MB()                                               # canopy over the fuel berth
    for v in (-7.5, 7.5):
        for u in (54.4, 57.6):
            mb.box((0.2, 0.2, 3.6), dock.w(u, v, DOCK_DECK_Z + 1.8), P["metal"])
    c0 = dock.w(56.0, 0, DOCK_DECK_Z + 3.7)
    mb.box((4.4, 17.0, 0.3), c0, P["white"], rot=(0, 0, FACING))
    mb.box((4.5, 17.1, 0.12), c0 + Vector((0, 0, 0.2)), P["yellow"], rot=(0, 0, FACING))
    mb.build("Dealer_FuelCanopy", C["Dock"], root)
    text_mesh("Dealer_Sign_Fuel", "FUEL", 0.9, tuple(dock.w(58.25, 0, DOCK_DECK_Z + 3.75)),
              (math.pi / 2, 0, FACING + math.pi / 2), P["navy"], C["Dock"], root, extrude=0.06)
    light("Dealer_FuelCanopy_Light", 'AREA', 600, tuple(dock.w(56.0, 0, DOCK_DECK_Z + 3.5)), C["Lights"], root,
          rot=(0, 0, FACING), size=4.0, color=(1.0, 0.97, 0.9))
    for k, u in enumerate((5, 15, 25, 35, 45, 53)):
        for s in (-1, 1):
            instance("Dealer_Marina_Lamp_%d%s" % (k + 1, "LR"[s > 0]), A["lamp"], dock.w(u, s * 1.4), C["Dock"], root)
    for k, u in enumerate((22, 42)):
        instance("Dealer_Marina_LifeRing_%d" % (k + 1), A["life_ring"], dock.w(u, -1.45), C["Dock"], root, rot=(0, 0, FACING))


    # --- plaza between showroom and marina, palms in planters, flag poles, benches
    mb = MB()
    plaza_c = sp + fwd * 16.0
    for i in range(-3, 4):
        for j in range(-2, 3):
            p = plaza_c + side * (i * 3.0) + fwd * (j * 3.0)
            z = g.z(p.x, p.y, PLAZA_Z)
            mb.box((2.9, 2.9, 0.2), (p.x, p.y, z + 0.05), P["concrete"] if (i + j) % 2 else P["white"], rot=(0, 0, FACING))
    mb.build("Dealer_Plaza", C["Props"], root)
    for k, s in enumerate((-9.5, 9.5)):
        p = plaza_c + side * s
        z = g.z(p.x, p.y, PLAZA_Z)
        instance("Dealer_Plaza_Palm_%d" % (k + 1), A["palm"][2], (p.x, p.y, z), C["Vegetation"], root, rot=(0, 0, k))
        instance("Dealer_Plaza_Bench_%d" % (k + 1), A["bench"], tuple(p + fwd * 3.0 + Vector((0, 0, z))), C["Props"], root,
                 rot=(0, 0, FACING + math.pi / 2))
    flag_mats = [P["red"], P["blue"], P["yellow"]]
    mb = MB()
    for k in range(3):
        p = plaza_c - side * 12.0 + fwd * (-4.0 + k * 3.0)
        z = g.z(p.x, p.y, PLAZA_Z)
        mb.cyl(0.08, 0.06, 9.0, (p.x, p.y, z + 4.5), P["metal"], seg=6)
        mb.box((0.04, 1.8, 1.1), tuple(p + side * 0.9 + Vector((0, 0, z + 8.3))), flag_mats[k], rot=(0, 0, FACING))
    mb.build("Dealer_FlagPoles", C["Props"], root)

    # --- boat yard: a boat on a trailer stand and a travel-lift frame beside the showroom
    yard = sp - side * 17.0 + fwd * 4.0
    yz = g.z(yard.x, yard.y, PLAZA_Z)
    mb = MB()
    for s in (-1, 1):
        for f in (-1, 1):
            p = yard + side * (s * 2.4) + fwd * (f * 3.5)
            mb.box((0.35, 0.35, 6.0), (p.x, p.y, yz + 3.0), P["blue"])
            mb.cyl(0.35, 0.35, 0.3, (p.x, p.y, yz + 0.3), P["black"], rot=(0, math.pi / 2, FACING), seg=10)
        a, b = yard + side * (s * 2.4) + fwd * -3.5, yard + side * (s * 2.4) + fwd * 3.5
        mb.box_between((a.x, a.y, yz + 6.0), (b.x, b.y, yz + 6.0), 0.4, 0.5, P["blue"])
    for f in (-1, 1):
        a, b = yard - side * 2.4 + fwd * (f * 3.5), yard + side * 2.4 + fwd * (f * 3.5)
        mb.box_between((a.x, a.y, yz + 6.0), (b.x, b.y, yz + 6.0), 0.4, 0.5, P["blue"])
        for s in (-1, 1):
            q = yard + side * (s * 1.2) + fwd * (f * 2.0)
            mb.cyl_between((q.x, q.y, yz + 6.0), (q.x, q.y, yz + 1.6), 0.02, 0.02, P["metal_dark"], seg=4)
    mb.build("Dealer_TravelLift", C["Props"], root)
    instance("Dealer_Yard_Boat", boat_mesh("Dealer_Yard_Boat", P, 7.0, 2.6, "white", "teal", "motor"),
             (yard.x, yard.y, yz + 1.5), C["Props"], root, rot=(0, 0, FACING))

    # --- vegetation, rocks
    avoid = [(sp.x, sp.y, 18.0), (plaza_c.x, plaza_c.y, 13.0), (yard.x, yard.y, 6.0), (start.x, start.y, 5.0)]
    palms = scatter(g, center, 85, 45, 301, 1.4, 12, 0.82, avoid, 6.0)
    place_many("Dealer_Palm", A["palm"], palms, C["Vegetation"], root, 1, (0.9, 1.3))
    trees = scatter(g, W(22, 26), 26, 12, 302, 4.0, 20, 0.8, avoid, 6.0)
    place_many("Dealer_Tree", A["tree"], trees, C["Vegetation"], root, 2, (0.9, 1.4))
    bushes = scatter(g, center, 80, 60, 303, 1.8, 20, 0.78, avoid, 2.5)
    place_many("Dealer_Bush", A["bush"], bushes, C["Vegetation"], root, 3, (0.7, 1.4))
    cliff = scatter(g, W(40, 34), 30, 25, 304, -2.0, 9, 0.0, avoid, 3.0)
    place_many("Dealer_Rock_Cliff", A["rock_warm"] + A["rock"][2:], cliff, C["Vegetation"], root, 4, (1.0, 2.2), 0.6)
    shore = scatter(g, center, 100, 30, 305, -1.5, 1.0, 0.3, avoid + [(dock.w(25, 0).x, dock.w(25, 0).y, 30)], 3.0)
    place_many("Dealer_Rock_Shore", A["rock"], shore, C["Vegetation"], root, 5, (0.6, 1.4), 0.4)
    return root
