"""Builds Blender/Models/Fish.blend and Export/Fish/*.fbx from fish_data.py.

Run inside Blender (any file open). The fish are built in a temporary scene, written to Fish.blend with
bpy.data.libraries.write, exported one FBX per fish, and then removed again, so the open file is left as it was.
"""
import bpy, os, io, math, contextlib
from mathutils import Vector
import fish_data as D
import fish_models as FM
from fg_lib import mat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(FM.__file__)))
BLEND = os.path.join(ROOT, "Blender", "Models", "Fish.blend")
FBX_DIR = os.path.join(ROOT, "Export", "Fish")
SHEET_PNG = os.path.join(ROOT, "Renders", "Fish_Catalog_Sheet.png")
MUT_PNG = os.path.join(ROOT, "Renders", "Fish_Mutations_Preview.png")
SCENE = "FishCatalog"
MUTATION_BASE = "Red Snapper"


def hexcol(h):
    return FM.hexcol(h)


def mutation_materials():
    """role -> material for every mutation (roles: back, belly, fin, accent, eye)."""
    g = lambda n, c, **k: mat("M_Mut_%s" % n, c, k.pop("rough", 0.5), **k)
    M = {
        "Albino": dict(back=g("Albino_Body", (0.97, 0.95, 0.93)), belly=g("Albino_Body", (0.97, 0.95, 0.93)),
                       fin=g("Albino_Fin", (0.98, 0.82, 0.84)), accent=g("Albino_Accent", (0.95, 0.88, 0.88)),
                       eye=g("Albino_Eye", (0.85, 0.1, 0.15))),
        "Shadow": dict(back=g("Shadow_Body", (0.06, 0.05, 0.08)), belly=g("Shadow_Body", (0.06, 0.05, 0.08)),
                       fin=g("Shadow_Fin", (0.35, 0.12, 0.55)), accent=g("Shadow_Fin", (0.35, 0.12, 0.55)),
                       eye=g("Shadow_Eye", (0.7, 0.3, 1.0), emit=(0.7, 0.3, 1.0), emit_strength=6.0)),
        "Glowing": dict(fin=g("Glow", (0.3, 1.0, 0.95), emit=(0.3, 1.0, 0.95), emit_strength=6.0),
                        accent=g("Glow", (0.3, 1.0, 0.95), emit=(0.3, 1.0, 0.95), emit_strength=6.0)),
        "Golden": dict(back=g("Golden_Body", (1.0, 0.76, 0.25), metal=1.0, rough=0.25), belly=g("Golden_Body", (1.0, 0.76, 0.25), metal=1.0, rough=0.25),
                       fin=g("Golden_Fin", (1.0, 0.86, 0.45), metal=1.0, rough=0.2), accent=g("Golden_Fin", (1.0, 0.86, 0.45), metal=1.0, rough=0.2)),
        "Radioactive": dict(back=g("Radioactive_Body", (0.35, 0.75, 0.15)), belly=g("Radioactive_Body", (0.35, 0.75, 0.15)),
                            fin=g("Radioactive_Fin", (0.15, 0.4, 0.1)),
                            accent=g("Radioactive_Glow", (0.8, 1.0, 0.2), emit=(0.8, 1.0, 0.2), emit_strength=6.0)),
        "Crystal": dict(back=g("Crystal_Body", (0.6, 0.92, 1.0), alpha=0.45, rough=0.05), belly=g("Crystal_Body", (0.6, 0.92, 1.0), alpha=0.45, rough=0.05),
                        fin=g("Crystal_Body", (0.6, 0.92, 1.0), alpha=0.45, rough=0.05),
                        accent=g("Crystal_Glow", (0.5, 1.0, 1.0), emit=(0.5, 1.0, 1.0), emit_strength=4.0)),
        "Ancient": dict(back=g("Ancient_Body", (0.55, 0.42, 0.26), metal=0.4, rough=0.85), belly=g("Ancient_Belly", (0.66, 0.58, 0.44), rough=0.9),
                        fin=g("Ancient_Fin", (0.42, 0.32, 0.2), metal=0.4, rough=0.85), accent=g("Ancient_Fin", (0.42, 0.32, 0.2), metal=0.4, rough=0.85)),
        "Ghost": dict(back=g("Ghost", (0.92, 0.96, 1.0), alpha=0.3, rough=0.2), belly=g("Ghost", (0.92, 0.96, 1.0), alpha=0.3, rough=0.2),
                      fin=g("Ghost", (0.92, 0.96, 1.0), alpha=0.3, rough=0.2), accent=g("Ghost", (0.92, 0.96, 1.0), alpha=0.3, rough=0.2)),
        "Rainbow": dict(back=g("Rainbow_Red", (0.95, 0.2, 0.25)), belly=g("Rainbow_Yellow", (1.0, 0.9, 0.2)),
                        fin=g("Rainbow_Violet", (0.55, 0.3, 0.95)), accent=g("Rainbow_Green", (0.2, 0.85, 0.4))),
        "Celestial": dict(back=g("Celestial_Body", (0.06, 0.08, 0.28)), belly=g("Celestial_Body", (0.06, 0.08, 0.28)),
                          fin=g("Celestial_Fin", (0.45, 0.25, 0.75)),
                          accent=g("Celestial_Star", (1, 1, 1), emit=(1, 1, 1), emit_strength=8.0)),
    }
    return M


def label(text, loc, rot, size, m, c):
    cu = bpy.data.curves.new("Label_" + text[:20], 'FONT')
    cu.body = text
    cu.size = size
    cu.align_x = 'CENTER'
    o = bpy.data.objects.new("Label_" + text[:28], cu)
    o.location = loc
    o.rotation_euler = rot
    cu.materials.append(m)
    c.objects.link(o)
    return o


def clear_scene(name):
    sc = bpy.data.scenes.get(name)
    if sc is None:
        return
    for o in list(sc.objects):
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and data.users == 0:
            for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
                if data.name in coll and coll[data.name] == data:
                    coll.remove(data)
                    break
    for c in list(sc.collection.children_recursive):
        bpy.data.collections.remove(c)
    bpy.data.scenes.remove(sc)


def build():
    D.validate()
    prev_name = bpy.context.window.scene.name
    if prev_name in (SCENE, "FishTest"):
        prev_name = "FisherWorld" if "FisherWorld" in bpy.data.scenes else bpy.data.scenes[0].name
    bpy.context.window.scene = bpy.data.scenes[prev_name]
    clear_scene(SCENE)
    clear_scene("FishTest")
    sc = bpy.data.scenes.new(SCENE)
    bpy.context.window.scene = sc
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        pass
    sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.get("FishSheet_World") or bpy.data.worlds.new("FishSheet_World")
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs["Color"].default_value = (0.11, 0.15, 0.2, 1)
    bg.inputs["Strength"].default_value = 0.8
    sc.world = w

    rar_colls = {r: bpy.data.collections.new("Fish_%s" % r) for r in D.RARITIES}
    for c in rar_colls.values():
        sc.collection.children.link(c)
    sheet = bpy.data.collections.new("Catalog_Sheet")
    mutc = bpy.data.collections.new("Mutation_Preview")
    misc = bpy.data.collections.new("Preview_Camera_Light")
    for c in (sheet, mutc, misc):
        sc.collection.children.link(c)

    # --- real-size models, one row per rarity (heads to -Y), spaced by size
    objs = {}
    row_y = 0.0
    for r in D.RARITIES:
        x = 0.0
        group = [f for f in D.FISH if f["rarity"] == r]
        depth = max(f["size_avg"] for f in group) / 100.0
        for f in group:
            name = FM_name(f)
            o = FM.fish_object(f, name, real_size=True)
            rar_colls[r].objects.link(o)
            wdt = max(o.dimensions.x, 0.1)
            o.location = (x + wdt / 2, row_y, 0)
            x += wdt + 0.3
            o["fish_id"] = f["id"]
            o["rarity"] = r
            o["avg_length_cm"] = f["size_avg"]
            o["avg_weight_kg"] = round(f["weight_avg"], 3)
            objs[f["id"]] = o
        row_y += depth + 2.0

    # --- normalised catalogue sheet (instances scaled to 1 m), seen from -X
    lab_mats = {r: mat("M_Label_%s" % r, FM.hexcol(D.RARITY[r]["ui"]), 0.5, emit=FM.hexcol(D.RARITY[r]["ui"]), emit_strength=1.5)
                for r in D.RARITIES}
    cols, cw, rh = 12, 1.55, 1.3
    sheet_origin = Vector((-30.0, 0.0, 0.0))
    for i, f in enumerate(D.FISH):
        o = objs[f["id"]]
        s = 100.0 / f["size_avg"] * {"ray": 0.75, "mola": 0.7}.get(f["plan"], 1.0)
        inst = bpy.data.objects.new("Sheet_%03d" % f["id"], o.data)
        inst.scale = (s, s, s)
        if f["plan"] in ("ray", "flatfish"):
            inst.rotation_euler = (0, -math.pi / 2, 0)            # show rays and flatfish from above
        col, row = i % cols, i // cols
        inst.location = sheet_origin + Vector((0, -col * cw, -row * rh))
        sheet.objects.link(inst)
        label("#%03d %s" % (f["id"], f["name"]), sheet_origin + Vector((0, -col * cw, -row * rh - 0.5)),
              (math.pi / 2, 0, -math.pi / 2), 0.085, lab_mats[f["rarity"]], sheet)
    sheet_w, sheet_h = cols * cw, math.ceil(len(D.FISH) / cols) * rh

    # --- mutation preview: the same mesh with object-level material overrides
    base = next(f for f in D.FISH if f["name"] == MUTATION_BASE)
    role_of = {}
    for role, h in zip(("back", "belly", "fin", "accent"), base["look"]["colors"]):
        for prefix in ("M_Fish_", "M_FishGlow_", "M_FishGlass_"):
            role_of.setdefault(prefix + h.lstrip("#").lower(), role)
    MM = mutation_materials()
    names = ["Normal"] + [m["name"] for m in D.MUTATIONS]
    mut_origin = Vector((-30.0, 0.0, -sheet_h - 2.5))
    lab = mat("M_Label_Mutation", (0.95, 0.95, 0.95), 0.5, emit=(0.95, 0.95, 0.95), emit_strength=1.0)
    src = objs[base["id"]]
    for k, mname in enumerate(names):
        inst = bpy.data.objects.new("Mutation_%s_%s" % (mname, FM_name(base)), src.data)
        s = 100.0 / base["size_avg"] * 1.2
        inst.scale = (s, s, s)
        inst.location = mut_origin + Vector((0, -k * 1.65, 0))
        mutc.objects.link(inst)
        if mname != "Normal":
            for slot in inst.material_slots:
                slot.link = 'OBJECT'
                orig = src.data.materials[slot.slot_index]
                role = "eye" if orig.name == "M_FishEye" else role_of.get(orig.name)
                newm = MM[mname].get(role) if role else None
                if newm is not None:
                    slot.material = newm
                elif orig is not None:
                    slot.material = orig
        label(mname, mut_origin + Vector((0, -k * 1.65, -0.55)), (math.pi / 2, 0, -math.pi / 2), 0.14, lab, mutc)

    # --- camera + light for the sheet render
    cd = bpy.data.cameras.new("FishSheet_Cam")
    cd.type = 'ORTHO'
    cam = bpy.data.objects.new("FishSheet_Cam", cd)
    misc.objects.link(cam)
    cam.rotation_euler = (math.pi / 2, 0, -math.pi / 2)
    ld = bpy.data.lights.new("FishSheet_Sun", 'SUN')
    ld.energy = 3.5
    sun = bpy.data.objects.new("FishSheet_Sun", ld)
    sun.rotation_euler = (math.radians(70), 0, math.radians(-110))
    misc.objects.link(sun)
    sc.camera = cam

    def render(path, center, width, height, show):
        for c in list(rar_colls.values()) + [sheet, mutc]:
            c.hide_render = c not in show
        cam.location = (center.x - 20, center.y, center.z)
        cd.ortho_scale = width
        sc.render.resolution_x = 2400
        sc.render.resolution_y = int(round(2400 * height / width))
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        for c in list(rar_colls.values()) + [sheet, mutc]:
            c.hide_render = False

    render(SHEET_PNG, sheet_origin + Vector((0, -(sheet_w - cw) / 2, -(sheet_h - rh) / 2 + 0.05)), sheet_w + 0.6, sheet_h + 0.6, [sheet])
    render(MUT_PNG, mut_origin + Vector((0, -(len(names) - 1) * 1.65 / 2, -0.15)), len(names) * 1.65 + 0.5, 1.9, [mutc])
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    cam.location = (sheet_origin.x - 20, sheet_origin.y - (sheet_w - cw) / 2, sheet_origin.z - (sheet_h - rh) / 2)
    cd.ortho_scale = sheet_w + 0.6

    # --- one FBX per fish, at the origin
    os.makedirs(FBX_DIR, exist_ok=True)
    for f in D.FISH:
        o = objs[f["id"]]
        keep = o.location.copy()
        o.location = (0, 0, 0)
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        with contextlib.redirect_stdout(io.StringIO()):
            bpy.ops.export_scene.fbx(filepath=os.path.join(FBX_DIR, FM_name(f) + ".fbx"), use_selection=True,
                                     object_types={'MESH'}, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                                     bake_space_transform=True, mesh_smooth_type='FACE', add_leaf_bones=False, bake_anim=False)
        o.location = keep

    # --- write Fish.blend (this scene and everything it uses), then remove it from the open file
    os.makedirs(os.path.dirname(BLEND), exist_ok=True)
    bpy.data.libraries.write(BLEND, {sc}, path_remap='RELATIVE_ALL', fake_user=True)
    bpy.context.window.scene = bpy.data.scenes[prev_name]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs.values())
    clear_scene(SCENE)
    return dict(fish=len(objs), tris=tris, blend=BLEND)


def FM_name(f):
    return "Fish_%03d_%s" % (f["id"], "".join(ch if ch.isalnum() else "_" for ch in f["name"]).strip("_"))


GALLERY_COLL = "85_Fish_Gallery"
GALLERY_CENTER = Vector((0.0, 0.0, -60.0))     # under the open sea in the middle of the world, far below the seabed
GALLERY_SCALE = 2.0                            # display size compared with the real model (1 = real size)
GALLERY_MIN_LEN = 0.4                          # tiny fish are shown at least this long (m)
LABEL_SIZE = 0.22                              # name label text height (m)
LABEL_GAP = 1.2                                # free space between two name labels (m)


def build_gallery():
    """All 122 fish (appended from Fish.blend) on a floor under the world map, one row per rarity.

    Every fish gets a slot at least as wide as its name label, so the labels never overlap.

    Text labels are curve objects, so they show in Blender but are not part of the FBX export.
    """
    from fg_lib import coll, clear_coll, link, MB, scene
    sc = scene()
    c = coll(GALLERY_COLL)
    clear_coll(c)
    names = [FM_name(f) for f in D.FISH]
    with bpy.data.libraries.load(BLEND, link=False) as (src, dst):
        dst.meshes = [n for n in src.meshes if n in names]
    meshes = {m.name.split(".")[0]: m for m in dst.meshes}
    root = bpy.data.objects.new("Fish_Gallery_Root", None)
    root.empty_display_type = 'CUBE'
    root.empty_display_size = 3
    root.location = GALLERY_CENTER
    c.objects.link(root)
    bpy.context.view_layer.update()

    rows, gap, per_row = [], LABEL_GAP, 12
    for r in D.RARITIES:
        group = [f for f in D.FISH if f["rarity"] == r]
        for ci in range(0, len(group), per_row):
            add_row(rows, r, group[ci:ci + per_row], ci == 0, len(group), meshes, gap)
    total_d = sum(row[3] for row in rows) + 3.0 * (len(rows) - 1)
    max_w = max(row[2] for row in rows)
    x0 = GALLERY_CENTER.x - max_w / 2                 # every row starts at the same left edge

    y = GALLERY_CENTER.y + total_d / 2
    floor_mat = mat("M_Gallery_Floor", (0.16, 0.2, 0.26), 0.8)
    stripe_mat = {r: mat("M_Gallery_%s" % r, FM.hexcol(D.RARITY[r]["ui"]), 0.5, emit=FM.hexcol(D.RARITY[r]["ui"]), emit_strength=0.6)
                  for r in D.RARITIES}
    mb = MB()
    mb.box((max_w + 16, total_d + 8, 0.4), GALLERY_CENTER - Vector((4, 0, 0.2)), floor_mat)
    for r, items, w, depth, first, count in rows:
        y -= depth / 2
        mb.box((w + 2, 0.15, 0.05), (x0 + w / 2, y - depth / 2 - 1.0, GALLERY_CENTER.z + 0.02), stripe_mat[r])
        if first:
            label = bpy.data.curves.new("GalleryTitle_%s" % r, 'FONT')
            label.body = "%s (%d)" % (r.upper(), count)
            label.size = 1.2
            label.align_x = 'RIGHT'
            label.materials.append(stripe_mat[r])
            lo = bpy.data.objects.new("Gallery_Title_%s" % r, label)
            lo.location = (x0 - 1.5, y - 0.5, GALLERY_CENTER.z + 0.05)
            link(lo, c, root)
        for f, me, xc, sc_f in items:
            zmin = min(v.co.z for v in me.vertices) * sc_f
            o = bpy.data.objects.new(FM_name(f), me)
            o.location = (x0 + xc, y, GALLERY_CENTER.z + 0.3 - zmin)
            o.rotation_euler = (0, 0, -math.pi / 2)          # side view from the front of the row, head to the left
            o.scale = (sc_f, sc_f, sc_f)
            o["display_scale"] = round(sc_f, 2)
            o["fish_id"] = f["id"]
            o["rarity"] = r
            link(o, c, root)
            cu = bpy.data.curves.new("GalleryLabel_%03d" % f["id"], 'FONT')
            cu.body = "#%03d %s" % (f["id"], f["name"])
            cu.size = LABEL_SIZE
            cu.align_x = 'CENTER'
            cu.materials.append(stripe_mat[r])
            lo = bpy.data.objects.new("Gallery_Label_%03d" % f["id"], cu)
            lo.location = (x0 + xc, y - depth / 2 - 0.6, GALLERY_CENTER.z + 0.05)
            lo.rotation_euler = (0, 0, 0)
            link(lo, c, root)
        y -= depth / 2 + 3.0
    mb.build("Fish_Gallery_Floor", c, root)
    from fg_lib import light
    for k in range(3):
        light("Fish_Gallery_Light_%d" % (k + 1), 'AREA', 20000, (GALLERY_CENTER.x + (k - 1) * max_w / 3, GALLERY_CENTER.y, GALLERY_CENTER.z + 25),
              c, root, color=(1.0, 0.97, 0.92), size=max_w / 3, use_shadow=False)
    return root


def add_row(rows, rarity, group, first, count, meshes, gap):
    """One gallery row: each fish gets a slot as wide as its length or its name label, whichever is wider."""
    items, x = [], 0.0
    for f in group:
        me = meshes[FM_name(f)]
        length = max(v.co.y for v in me.vertices) - min(v.co.y for v in me.vertices)   # fish length (head is -Y)
        sc_f = max(GALLERY_SCALE, GALLERY_MIN_LEN / max(length, 0.01))
        label_w = len("#%03d %s" % (f["id"], f["name"])) * LABEL_SIZE * 0.55
        slot = max(length * sc_f, label_w)
        items.append((f, me, x + slot / 2, sc_f))
        x += slot + gap
    depth = max(max((max(v.co.x for v in me.vertices) - min(v.co.x for v in me.vertices)) * sc_f for _, me, _, sc_f in items), 1.0)
    rows.append((rarity, items, x - gap, depth, first, count))
