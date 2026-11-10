"""World layout, sea placeholder, sun/sky and the asset library."""
import bpy, math
from fg_lib import scene, coll, clear_coll, link, light, MB, palette, srgb
import fg_assets

# Island centres in metres (Blender X/Y; Unity X/-Z after FBX export). Docks face the open
# water in the middle so every island is visible from the sea lanes between them.
ISLANDS = {
    "Home":   {"center": (-185.0, -120.0)},
    "Fish":   {"center": (200.0, -150.0)},
    "Dealer": {"center": (185.0, 200.0)},
    "Rod":    {"center": (-190.0, 170.0)},
    "Cave":   {"center": (-30.0, 340.0)},
}
SEA_SIZE = 900.0          # the world spans roughly -450..450 m on X and Y


def setup_scene():
    sc = scene()
    bpy.context.window.scene = sc
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    sc.frame_start, sc.frame_end = 1, 240
    sc.render.fps = 24
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        pass
    sc.view_settings.view_transform = 'AgX'
    return sc


def setup_sky(sc):
    w = bpy.data.worlds.get("FisherWorld_Sky") or bpy.data.worlds.new("FisherWorld_Sky")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    grad = nt.nodes.new("ShaderNodeValToRGB")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], grad.inputs["Fac"])
    nt.links.new(grad.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs[0])
    cr = grad.color_ramp
    cr.elements[0].position = 0.45
    cr.elements[0].color = (*srgb((0.85, 0.88, 0.90)), 1)
    cr.elements[1].position = 0.75
    cr.elements[1].color = (*srgb((0.42, 0.62, 0.86)), 1)
    bg.inputs["Strength"].default_value = 1.0


def setup_lighting():
    c = coll("90_Lighting")
    clear_coll(c)
    sun = light("Sun_Main", 'SUN', 4.0, (0, 0, 120), c, color=(1.0, 0.95, 0.86),
                rot=(math.radians(48), math.radians(8), math.radians(-35)), angle=math.radians(1.5))
    cam_d = bpy.data.cameras.get("Cam_Overview") or bpy.data.cameras.new("Cam_Overview")
    cam_d.lens = 28
    cam_d.clip_end = 2000
    cam = bpy.data.objects.new("Cam_Overview", cam_d)
    cam.location = (0, -600, 400)
    cam.rotation_euler = (math.radians(53), 0, 0)
    link(cam, c)
    scene().camera = cam
    return sun


def setup_sea(P):
    """Flat stand-in so the islands can be judged in Blender. Not exported:
    in Unity the existing WaterManager/WaterManagement objects provide the sea."""
    c = coll("01_Sea_Placeholder")
    clear_coll(c)
    mb = MB()
    size, n = SEA_SIZE, 90
    pts, faces = [], []
    for i in range(n + 1):
        for j in range(n + 1):
            pts.append((-size / 2 + size * i / n, -size / 2 + size * j / n, 0.0))
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j
            faces.append((a, a + n + 1, a + n + 2, a + 1))
    mb.poly(pts, faces, P["sea_placeholder"])
    o = mb.build("Sea_Placeholder_NotForExport", c)
    o.hide_select = True
    o.visible_shadow = False           # keeps the fish gallery under the map lit
    return o


def setup_seabed(P, cell=20.0, margin=60.0):
    """Low-poly sand floor under the whole sea (the island terrains only cover their own shallows).

    About -13 m between the islands, sloping down to about -20 m at the map edge (The Drop).
    It also hides everything placed below the map, such as the fish gallery.
    """
    import random
    from mathutils import Vector
    from fg_lib import fbm, smoothstep
    c = coll("02_Seabed")
    clear_coll(c)
    half = SEA_SIZE / 2 + margin
    n = int(2 * half / cell)
    rnd = random.Random(5)
    pts, faces, mats = [], [], []
    for i in range(n + 1):
        for j in range(n + 1):
            x = -half + i * cell + (rnd.uniform(-0.3, 0.3) * cell if 0 < i < n else 0)
            y = -half + j * cell + (rnd.uniform(-0.3, 0.3) * cell if 0 < j < n else 0)
            r = math.hypot(x, y)
            z = -13.0 + 1.5 * fbm(x, y, 91, 2, 0.012) - 7.0 * smoothstep(330, 460, r)
            pts.append((x, y, z))
    mb = MB()
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j
            b, cc, d = a + n + 1, a + n + 2, a + 1
            tris = [(a, b, d), (b, cc, d)] if (i + j) % 2 else [(a, b, cc), (a, cc, d)]
            for t in tris:
                faces.append(t)
    sand, dark = P["sand_wet"], P["seabed"]
    for k, t in enumerate(faces):
        zc = sum(pts[v][2] for v in t) / 3
        m = dark if (zc < -15.5 or rnd.random() < 0.18) else sand
        mb.poly([pts[v] for v in t], [(0, 1, 2)], m)
    o = mb.build("Seabed_Sand", c)
    return o


def build_base():
    sc = setup_scene()
    P = palette()
    setup_sky(sc)
    setup_lighting()
    setup_sea(P)
    setup_seabed(P)
    A = fg_assets.build_library(P)
    fg_assets.exclude_library()
    return P, A
