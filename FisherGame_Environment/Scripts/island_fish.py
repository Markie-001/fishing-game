"""Island 2 - Fish Selling Island: harbour with a working lighthouse; the fish vendor is inside it."""
import bpy, math, random
from mathutils import Vector
from fg_lib import (MB, IslandShape, build_terrain, Ground, island_setup, place_many, scatter,
                    instance, light, link, mat, srgb, text_mesh, DOCK_DECK_Z)
from fg_assets import Dock, place_npc

PREFIX = "Fish"
FACING = math.radians(150)                 # harbour side, towards the middle of the world
LH_LOCAL = (-13.0, 7.0)                    # lighthouse on a grassy knoll above the harbour
LH_Z = 6.0
BEAM_SPEED = 0.06                          # radians per frame (~1 turn per 4.4 s at 24 fps)


def shape():
    return IslandShape(
        lobes=[(0, 0, 42), (-18, 16, 24), (24, -20, 27), (8, 30, 18)],
        peaks=[(20, -16, 22, 11.0), (4, 22, 14, 4.0)],
        cliffs=[(math.radians(-35), math.radians(60), 11.0), (math.radians(60), math.radians(25), 6.0)],
        pads=[(LH_LOCAL[0], LH_LOCAL[1], 9.0, LH_Z), (-30, 22, 6.0, 1.9)],
        seed=23, irregular=0.2, beach_h=1.6, bumps=1.4)


def ring_wall(mb, r_out, thick, z0, h, m, segs, door_angle=0.0, door_w=0.5, door_h=2.7,
              windows=(), win_h=(1.2, 2.6), glass=None):
    """Round wall made of segments; leaves a doorway and window openings."""
    for i in range(segs):
        a0 = 2 * math.pi * i / segs
        a1 = 2 * math.pi * (i + 1) / segs
        am = (a0 + a1) / 2
        rm = r_out - thick / 2
        p0 = Vector((math.cos(a0) * rm, math.sin(a0) * rm, 0))
        p1 = Vector((math.cos(a1) * rm, math.sin(a1) * rm, 0))
        chord = (p1 - p0).length + 0.08
        c = (p0 + p1) / 2
        da = abs(math.atan2(math.sin(am - door_angle), math.cos(am - door_angle)))
        is_win = any(abs(math.atan2(math.sin(am - w), math.cos(am - w))) < math.pi / segs for w in windows)
        parts = []
        if da < door_w:
            parts = [(door_h, h)]
        elif is_win:
            parts = [(0, win_h[0]), (win_h[1], h)]
            if glass is not None:
                g = Vector((c.x, c.y, z0 + (win_h[0] + win_h[1]) / 2))
                mb.box((chord * 0.9, 0.06, win_h[1] - win_h[0]), g, glass, rot=(0, 0, am + math.pi / 2))
        else:
            parts = [(0, h)]
        for za, zb in parts:
            mb.box((chord, thick, zb - za), (c.x, c.y, z0 + (za + zb) / 2), m, rot=(0, 0, am + math.pi / 2))


def lighthouse(P):
    """Origin = ground. Ground floor (r 4.6) is the fish shop, door faces +X."""
    mb = MB()
    white, red = P["white"], P["red"]
    mb.cyl(5.4, 5.6, 0.7, (0, 0, 0.0), P["rock"], seg=12)
    ring_wall(mb, 4.7, 0.45, 0.35, 4.2, white, 20, door_angle=0.0, door_w=0.2, door_h=2.8,
              windows=(math.radians(70), math.radians(-70), math.radians(140), math.radians(-140)),
              glass=P["glass"])
    mb.cyl(4.3, 4.3, 0.1, (0, 0, 0.4), P["wood"], seg=20)
    mb.cyl(4.8, 4.8, 0.35, (0, 0, 4.7), red, seg=20)                       # band above the shop
    # tapered tower with a red middle band
    segs = [(4.9, 4.2, 4.2), (13.0, 3.3, 3.25), (15.0, 3.0, 3.0), (22.5, 2.6, 2.6)]
    z = 4.7
    prev_r = 4.4
    for z_top, r_top, _ in segs:
        m = red if z_top == 15.0 else white
        mb.cyl(prev_r, r_top, z_top - z, (0, 0, (z + z_top) / 2), m, seg=20)
        z, prev_r = z_top, r_top
    # small tower windows
    for k, zz in enumerate((8.5, 12.0, 17.5, 20.0)):
        a = k * 1.7 + 0.4
        r = 4.0 - (zz - 4.7) * 0.075
        mb.box((0.15, 0.7, 1.1), (math.cos(a) * r, math.sin(a) * r, zz), P["navy"], rot=(0, 0, a))
    # gallery, railing
    mb.cyl(3.7, 3.7, 0.3, (0, 0, 22.6), P["metal_dark"], seg=20)
    for i in range(24):
        a = 2 * math.pi * i / 24
        mb.box((0.06, 0.06, 1.05), (math.cos(a) * 3.55, math.sin(a) * 3.55, 23.25), P["metal_dark"])
    mb.torus(3.55, 0.05, (0, 0, 23.8), P["metal_dark"], seg=24, rseg=4)
    # lantern room
    mb.cyl(2.0, 2.0, 0.6, (0, 0, 23.05), red, seg=16)
    mb.cyl(1.85, 1.85, 2.6, (0, 0, 24.65), P["glass"], seg=16, cap=False)
    for i in range(8):
        a = 2 * math.pi * i / 8
        mb.box((0.08, 0.08, 2.6), (math.cos(a) * 1.87, math.sin(a) * 1.87, 24.65), P["metal_dark"])
    mb.cyl(2.05, 2.05, 0.2, (0, 0, 26.0), P["metal_dark"], seg=16)
    mb.cyl(2.1, 0.25, 1.6, (0, 0, 26.9), red, seg=16)
    mb.ico(0.32, (0, 0, 27.8), P["metal_dark"], sub=1)
    mb.cyl(0.03, 0.03, 1.4, (0, 0, 28.6), P["metal"], seg=4)
    # lamp + lens
    mb.cyl(0.45, 0.45, 0.9, (0, 0, 23.75), P["metal_dark"], seg=8)
    mb.ico(0.55, (0, 0, 24.65), P["lamp_glow"], sub=2)
    lens = mat("M_FresnelLens", (1.0, 0.9, 0.6), 0.05, alpha=0.45)
    mb.cyl(0.95, 0.95, 1.3, (0, 0, 24.65), lens, seg=12)

    # ---------- fish shop interior (ground floor)
    f = 0.45
    wood, dark = P["wood"], P["wood_dark"]
    # counter facing the door
    mb.box((0.7, 4.2, 1.0), (-1.0, 0, f + 0.5), dark)
    mb.box((0.85, 4.4, 0.08), (-1.0, 0, f + 1.04), P["wood_light"])
    # ice display at the front of the counter
    mb.box((0.9, 3.4, 0.7), (-0.2, 0, f + 0.35), P["white"])
    mb.box((0.8, 3.3, 0.12), (-0.2, 0, f + 0.72), P["ice"])
    rnd = random.Random(7)
    for k in range(10):
        y = -1.45 + k * 0.32
        mb.ico(0.09, (-0.2 + rnd.uniform(-0.2, 0.2), y, f + 0.82), P["fish"], scale=(3.2, 1.0, 0.8), rot=(0, 0, rnd.uniform(-0.4, 0.4)))
    # scale and till on the counter
    mb.box((0.35, 0.35, 0.05), (-1.0, 1.3, f + 1.12), P["metal"])
    mb.box((0.08, 0.3, 0.35), (-1.12, 1.3, f + 1.3), P["metal_dark"])
    mb.box((0.35, 0.45, 0.25), (-1.0, -1.4, f + 1.2), P["metal_dark"])
    # shelves and price board on the back wall
    for z in (1.5, 2.2, 2.9):
        mb.box((0.4, 3.0, 0.06), (-3.7, 0, f + z), wood)
        for k in range(5):
            mb.box((0.25, 0.25, 0.3), (-3.7, -1.2 + k * 0.6, f + z + 0.18), P["blue"] if k % 2 else P["yellow"])
    mb.box((0.06, 1.8, 1.1), (-4.12, 0, f + 3.55), P["black"])
    mb.box((0.07, 1.95, 1.25), (-4.15, 0, f + 3.55), wood)
    # big fish trophy above the door
    mb.ico(0.35, (3.9, 0, f + 3.3), P["fish"], scale=(0.4, 3.0, 1.0))
    mb.box((0.05, 1.8, 0.4), (4.1, 0, f + 3.3), wood)
    # spiral stairs to the upper tower along the wall
    for k in range(12):
        a = math.radians(100) + k * math.radians(17)
        r = 3.5
        mb.box((1.2, 0.5, 0.12), (math.cos(a) * r, math.sin(a) * r, f + 0.3 + k * 0.32), wood, rot=(0, 0, a))
    # hanging lamp
    mb.cyl(0.02, 0.02, 0.8, (0, 0, f + 3.6), P["metal_dark"], seg=4)
    mb.cyl(0.45, 0.15, 0.35, (0, 0, f + 3.05), P["metal_dark"], seg=8)
    mb.ico(0.15, (0, 0, f + 2.9), P["lamp_glow"])
    # entrance: steps, awning, frame
    for k in range(3):
        mb.box((0.45, 2.4, 0.15), (5.0 + k * 0.45, 0, 0.3 - k * 0.15), P["rock"])
    for y in (-1.25, 1.25):
        mb.box((0.25, 0.25, 3.0), (4.7, y, 1.85), P["navy"])
    mb.box((0.3, 2.75, 0.3), (4.7, 0, 3.35), P["navy"])
    stripes = [P["red"], P["white"]]
    for k in range(6):
        y = -1.6 + k * 0.64 + 0.32
        mb.box((1.9, 0.64, 0.06), (5.5, y, 3.25), stripes[k % 2], rot=(0, 0.3, 0))
    return mb


def keeper_cottage(P):
    mb = MB()
    w, d, h = 7.0, 5.0, 2.8
    mb.box((w + 0.4, d + 0.4, 0.4), (0, 0, 0.0), P["rock"])
    mb.box((w, d, h), (0, 0, 0.2 + h / 2), P["white"])
    mb.gable_roof(d, w, 1.9, (0, 0, 0.2 + h), P["roof_red"], rot=(0, 0, math.pi / 2), overhang=0.4)
    mb.box((1.0, 0.8, 2.6), (2.2, 0.0, 0.2 + h + 1.2), P["white"])
    for x in (-2.3, 0.0, 2.3):
        mb.box((1.0, 0.08, 1.1), (x, d / 2 + 0.03, 1.7), P["window_lit"] if x == 0.0 else P["glass"])
        mb.box((1.2, 0.12, 0.12), (x, d / 2 + 0.05, 2.3), P["navy"])
    mb.box((0.08, 1.0, 2.0), (w / 2 + 0.04, 0, 1.2), P["navy"])
    mb.box((1.6, 1.6, 0.15), (w / 2 + 0.8, 0, 0.1), P["wood"])
    return mb


def beam_material(lamp_pos, length):
    """Faint additive glow that fades out with distance from the lamp."""
    m = bpy.data.materials.get("M_LighthouseBeam") or bpy.data.materials.new("M_LighthouseBeam")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dist = nt.nodes.new("ShaderNodeVectorMath")
    dist.operation = 'DISTANCE'
    dist.inputs[1].default_value = tuple(lamp_pos)
    fade = nt.nodes.new("ShaderNodeMapRange")
    fade.inputs["From Min"].default_value = 0.0
    fade.inputs["From Max"].default_value = length
    fade.inputs["To Min"].default_value = 0.06
    fade.inputs["To Max"].default_value = 0.0
    nt.links.new(geo.outputs["Position"], dist.inputs[0])
    nt.links.new(dist.outputs["Value"], fade.inputs["Value"])
    nt.links.new(fade.outputs["Result"], mix.inputs["Fac"])
    em.inputs["Color"].default_value = (*srgb((1.0, 0.93, 0.72)), 1)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    try:
        m.surface_render_method = 'BLENDED'
    except Exception:
        pass
    m.use_backface_culling = False
    m.diffuse_color = (1.0, 0.93, 0.72, 0.15)
    return m


def build(P, A, center):
    cx, cy = center
    root_c, C, root = island_setup("20_FishMarket_Island", PREFIX, center)
    W = lambda lx, ly: (cx + lx, cy + ly)

    terrain = build_terrain("Fish_Terrain", center, shape(), P, C["Terrain"], root, cell=2.6, kind="meadow")
    g = Ground([terrain])

    # --- lighthouse (door faces the harbour)
    lx, ly = W(*LH_LOCAL)
    lz = g.z(lx, ly, LH_Z)
    lh = lighthouse(P).build("Fish_Lighthouse", C["Buildings"], root)
    lh.location = (lx, ly, lz)
    lh.rotation_euler = (0, 0, FACING)
    fwd = Vector((math.cos(FACING), math.sin(FACING), 0))
    side = Vector((-fwd.y, fwd.x, 0))
    text_mesh("Fish_Sign_FishMarket", "FISH MARKET", 0.55, tuple(Vector((lx, ly, lz + 4.15)) + fwd * 4.82),
              (math.pi / 2, 0, FACING + math.pi / 2), P["white"], C["Buildings"], root, extrude=0.04)
    # Ruben, the fish buyer, behind the counter facing the door
    place_npc("Ruben", P, tuple(Vector((lx, ly, lz + 0.5)) - fwd * 1.9), FACING, C["NPCs"], root)
    light("Fish_Shop_InteriorLight", 'POINT', 150, (lx, ly, lz + 3.4), C["Lights"], root,
          color=(1.0, 0.85, 0.65), shadow_soft_size=0.3)

    # --- working lamp: rotating rig with two spot lights and visible beams
    lamp_z = lz + 24.65
    rig = bpy.data.objects.new("Fish_Lighthouse_BeamRig", None)
    rig.empty_display_type = 'ARROWS'
    rig.location = (lx, ly, lamp_z)
    link(rig, C["Lights"], root)
    drv = rig.driver_add("rotation_euler", 2).driver
    drv.type = 'SCRIPTED'
    drv.expression = "frame*%s" % BEAM_SPEED
    bpy.context.view_layer.update()
    beam_m = beam_material((lx, ly, lamp_z), 70.0)
    for k, ang in enumerate((0.0, math.pi)):
        s = light("Fish_Lighthouse_Spot_%d" % (k + 1), 'SPOT', 400000, (lx, ly, lamp_z), C["Lights"], rig,
                  color=(1.0, 0.93, 0.75), rot=(math.pi / 2 - 0.04, 0, ang - math.pi / 2),
                  spot_size=math.radians(9), spot_blend=0.4, shadow_soft_size=0.3, use_shadow=True)
        mb = MB()
        L = 70.0
        d = Vector((math.cos(ang), math.sin(ang), -0.04)).normalized()
        mb.cyl_between(Vector((lx, ly, lamp_z)) + d * 0.6, Vector((lx, ly, lamp_z)) + d * L, 0.5, 4.5, beam_m, seg=12)
        bm = mb.build("Fish_Lighthouse_Beam_%d" % (k + 1), C["Lights"], rig)
        bm.visible_shadow = False
    light("Fish_Lighthouse_LampGlow", 'POINT', 3000, (lx, ly, lamp_z), C["Lights"], root,
          color=(1.0, 0.9, 0.7), shadow_soft_size=0.6, use_shadow=False)

    # --- keeper's cottage beside the lighthouse
    kp = Vector((lx, ly, 0)) - side * 11.0 - fwd * 2.0
    kz = g.z(kp.x, kp.y, LH_Z)
    cot = keeper_cottage(P).build("Fish_KeeperCottage", C["Buildings"], root)
    cot.location = (kp.x, kp.y, kz)
    cot.rotation_euler = (0, 0, FACING - math.pi / 2)

    # --- harbour: wide working pier with an unloading platform
    door = Vector((lx, ly, 0)) + fwd * 6.5
    shore = g.shore((door.x, door.y), FACING)
    start = shore - fwd * 4.0
    dock = Dock("Fish_Harbour_Dock", (start.x, start.y, 0), FACING, g, P, plank_m="wood_grey")
    dock.rect(0, 30, -1.8, 1.8)
    dock.rect(14, 22, 1.8, 8.5)                          # unloading platform
    dock.rect(30, 34, -9.0, 4.0)                         # pier head
    dock.rect(4, 26, -5.0, -1.8, posts=True)             # low side berth
    dock.cleats([(33.6, -8.5), (33.6, 3.5), (21.6, 8.0), (14.4, 8.0), (10, -4.6), (20, -4.6)])
    dock.tires([(34.1, -6.0), (34.1, -2.0), (34.1, 2.0), (22.1, 5.0)])
    dock.build(C["Dock"], root)
    instance("Fish_FuelPump", A["fuel_blue"], dock.w(32.5, -7.6), C["Dock"], root, rot=(0, 0, FACING + math.pi / 2))
    for k, (u, v) in enumerate([(31.0, 3.4), (0.8, 1.5), (0.8, -1.5)]):
        instance("Fish_Dock_Lamp_%d" % (k + 1), A["lamp"], dock.w(u, v), C["Dock"], root)
        light("Fish_Dock_LampLight_%d" % (k + 1), 'POINT', 90, tuple(dock.w(u, v, DOCK_DECK_Z + 3.4)), C["Lights"], root,
              color=(1.0, 0.85, 0.6))
    instance("Fish_Dock_LifeRing", A["life_ring"], dock.w(29.5, -1.65), C["Dock"], root, rot=(0, 0, FACING))

    # unloading crane (davit) on the platform
    mb = MB()
    base = dock.w(20.5, 7.4)
    mb.cyl(0.35, 0.35, 0.4, base + Vector((0, 0, 0.2)), P["yellow"], seg=8)
    top = base + Vector((0, 0, 4.2))
    mb.cyl_between(base + Vector((0, 0, 0.3)), top, 0.16, 0.13, P["yellow"], seg=8)
    tip = top + dock.dv * 3.2 - Vector((0, 0, 0.4))
    mb.cyl_between(top, tip, 0.1, 0.08, P["yellow"], seg=6)
    mb.cyl_between(tip, tip - Vector((0, 0, 2.6)), 0.015, 0.015, P["metal_dark"], seg=4)
    mb.box((0.25, 0.15, 0.3), tip - Vector((0, 0, 2.75)), P["metal_dark"])
    mb.build("Fish_Dock_Crane", C["Dock"], root)

    # crates, barrels and nets on the platform and quay
    rnd = random.Random(31)
    props = [(15.0, 3.0), (15.9, 3.0), (15.4, 3.8), (17.5, 6.8), (18.3, 6.8), (16.0, 7.6)]
    for k, (u, v) in enumerate(props):
        instance("Fish_Dock_FishCrate_%02d" % (k + 1), A["fish_crate"], dock.w(u, v, DOCK_DECK_Z + (0.32 if k == 2 else 0)),
                 C["Props"], root, rot=(0, 0, FACING + rnd.uniform(-0.2, 0.2)))
    for k, (u, v) in enumerate([(21.3, 2.4), (21.3, 3.1), (20.6, 2.6)]):
        instance("Fish_Dock_Barrel_%d" % (k + 1), A["barrel"], dock.w(u, v), C["Props"], root)
    instance("Fish_Dock_NetRack", A["net"], dock.w(18.0, 8.2), C["Props"], root, rot=(0, 0, FACING))
    for k, t in enumerate((0.25, 0.6)):
        p = Vector((start.x, start.y, 0)).lerp(door, t) + side * 3.0
        instance("Fish_Bench_%d" % (k + 1), A["bench"], (p.x, p.y, g.z(p.x, p.y, 2)), C["Props"], root, rot=(0, 0, FACING + math.pi / 2))
    for k in range(5):
        p = door - fwd * 0.5 + side * (3.0 + (k % 3) * 0.75) + fwd * (1.2 * (k // 3))
        instance("Fish_Shop_FishCrate_%d" % (k + 1), A["fish_crate"], (p.x, p.y, g.z(p.x, p.y, LH_Z)), C["Props"], root,
                 rot=(0, 0, FACING + rnd.uniform(-0.2, 0.2)))

    # gravel path from the pier to the lighthouse door
    mb = MB()
    a, b = Vector((start.x, start.y, 0)), door
    n = int((b - a).length / 1.0)
    for k in range(n + 1):
        p = a.lerp(b, k / n)
        for s in (-0.7, 0.7):
            q = p + side * (s + rnd.uniform(-0.15, 0.15))
            mb.cyl(0.45, 0.45, 0.1, (q.x, q.y, g.z(q.x, q.y, 2) + 0.02), P["concrete"], seg=6, rot=(0, 0, rnd.random()))
    for k in range(n + 1):
        if k % 4 == 0:
            p = a.lerp(b, k / n)
            for s in (-1.6, 1.6):
                q = p + side * s
                mb.cyl(0.06, 0.06, 1.0, (q.x, q.y, g.z(q.x, q.y, 2) + 0.5), P["wood_grey"], seg=4)
    mb.build("Fish_Path", C["Props"], root)

    # --- vegetation & rocks (northern-ish coast: grass, dark bushes, a few pines)
    avoid = [(lx, ly, 10.0), (kp.x, kp.y, 7.0), (start.x, start.y, 4.0),
             (a.lerp(b, 0.5).x, a.lerp(b, 0.5).y, 6.0)]
    bushes = scatter(g, center, 60, 45, 201, 2.0, 30, 0.8, avoid, 2.5)
    place_many("Fish_Bush", A["bush_dark"] + A["bush"][:1], bushes, C["Vegetation"], root, 1, (0.7, 1.5))
    pines = scatter(g, W(14, -8), 30, 14, 202, 4.0, 30, 0.82, avoid, 6.0)
    place_many("Fish_Pine", A["pine"], pines, C["Vegetation"], root, 2, (0.7, 1.1))
    trees = scatter(g, W(4, 20), 16, 5, 205, 2.5, 20, 0.85, avoid, 6.0)
    place_many("Fish_Tree", A["tree"], trees, C["Vegetation"], root, 5, (0.9, 1.2))
    cliff = scatter(g, W(26, -22), 38, 40, 203, -2.0, 12, 0.0, avoid, 2.5)
    place_many("Fish_Rock_Cliff", A["rock"] + A["rock_dark"], cliff, C["Vegetation"], root, 3, (1.0, 2.4), 0.6)
    shore = scatter(g, center, 75, 35, 204, -1.5, 1.2, 0.3, avoid + [(dock.w(17, 0).x, dock.w(17, 0).y, 20)], 2.0)
    place_many("Fish_Rock_Shore", A["rock"] + A["rock_dark"][:1], shore, C["Vegetation"], root, 4, (0.6, 1.4), 0.4)
    return root
