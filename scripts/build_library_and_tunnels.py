"""
Library + tunnels:
  - Darker book palette + smaller books
  - Wall fill between bookcase back and dome edge (lower section, skips tunnel arcs)
  - Removes leftover single-book debris (BookCorner, BookSpine, etc.)
  - Tunnels: heavy detail (kept from previous run)
  - Real PBR materials so glTF exports colour
"""
import bpy, math, re
from mathutils import Vector

# ---- 0. CLEAN previous library/tunnel-fix attempts + leftover single books ----
PREFIXES = (
    'HH_LibCase_', 'HH_LibBook_', 'HH_LibWall_', 'HH_LibShelf_',
    'HH_LibColumn_', 'HH_Mezz_', 'HH_LibFill_',
    'HH_LibFallen_', 'HH_LibPile_', 'HH_LibDust_', 'HH_LibWeb_', 'HH_LibOpenBook_',
    'HH_Sofa_', 'HH_Rug_', 'HH_TableLamp_',
    'HH_BookF_', 'HH_BookExtra_', 'HH_NewShelf_',
    'HH_Book_', 'HH_BookCorner', 'HH_BookL', 'HH_BookR',
    'HH_BookSpine', 'HH_PageEdge',
    'TunFix_',
)
removed = 0
for o in list(bpy.data.objects):
    if any(o.name.startswith(p) for p in PREFIXES):
        bpy.data.objects.remove(o, do_unlink=True); removed += 1

# Also wipe any DECOR_ items inside the HH dome — VS adds candles/busts/lamps/
# banners/plinths against the bookcases that the user doesn't want.
decor_removed = 0
for o in list(bpy.data.objects):
    if not o.name.startswith('DECOR_'): continue
    r = (o.location.x ** 2 + o.location.y ** 2) ** 0.5
    if r < 9.0 and o.location.z < 6.0:    # inside HH dome
        bpy.data.objects.remove(o, do_unlink=True); decor_removed += 1
print(f'Cleaned {removed} previous + {decor_removed} HH DECOR_ items')

# ---- 1. MATERIALS (real Principled BSDF so glTF gets the colour) ----
def mat(name, rgba, roughness=0.55, metallic=0.0):
    m = bpy.data.materials.get(name)
    if not m: m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = rgba
    if 'Roughness' in bsdf.inputs: bsdf.inputs['Roughness'].default_value = roughness
    if 'Metallic'  in bsdf.inputs: bsdf.inputs['Metallic'].default_value = metallic
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    m.diffuse_color = rgba
    return m

def emit_mat(name, rgb, strength):
    m = bpy.data.materials.get(name)
    if not m: m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs[0].default_value = (*rgb, 1.0); e.inputs[1].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs[0])
    m.diffuse_color = (*rgb, 1.0)
    return m

# Library
WOOD_DARK   = mat('HH_LibWoodDark', (0.14, 0.07, 0.03, 1.0), 0.7)
WOOD_RICH   = mat('HH_LibWoodRich', (0.26, 0.13, 0.06, 1.0), 0.6)
RAILING_MAT = mat('HH_Railing',     (0.16, 0.09, 0.04, 1.0), 0.5)
WALL_FILL   = mat('HH_LibWallFill', (0.10, 0.06, 0.04, 1.0), 0.85)   # very dark wall behind bookcase

# === DARKER BOOK PALETTE ===
DARK_BOOK_COLORS = [
    (0.32, 0.06, 0.06),   # deep ox-blood
    (0.10, 0.20, 0.34),   # deep navy
    (0.10, 0.22, 0.12),   # forest green
    (0.20, 0.10, 0.04),   # dark mahogany
    (0.24, 0.08, 0.24),   # dark plum
    (0.14, 0.08, 0.30),   # midnight purple
    (0.34, 0.22, 0.06),   # tobacco gold
    (0.06, 0.22, 0.22),   # dark teal
    (0.36, 0.16, 0.04),   # russet
    (0.18, 0.10, 0.06),   # dark espresso
    (0.40, 0.12, 0.08),   # blood red
    (0.06, 0.16, 0.10),   # dark moss
]
book_mats = [mat(f'HH_LibBookM_{i}', (*c, 1.0), 0.65) for i, c in enumerate(DARK_BOOK_COLORS)]

# Tunnel materials
T_WALL   = mat('TunFix_Wall',  (0.18, 0.20, 0.18, 1.0), 0.85)
T_FLOOR  = mat('TunFix_Floor', (0.13, 0.13, 0.14, 1.0), 0.80)
T_CEIL   = mat('TunFix_Ceil',  (0.08, 0.08, 0.08, 1.0), 0.90)
T_TILE_L = mat('TunFix_TileLight', (0.20, 0.20, 0.19, 1.0), 0.70)
T_TILE_D = mat('TunFix_TileDark',  (0.10, 0.10, 0.10, 1.0), 0.70)
T_GRATE  = mat('TunFix_Grate', (0.06, 0.06, 0.06, 1.0), 0.50)
T_STAIN  = mat('TunFix_Stain', (0.16, 0.04, 0.04, 1.0), 0.95)
T_PIPE   = mat('TunFix_Pipe',  (0.30, 0.20, 0.10, 1.0), 0.60, 0.3)
T_CABLE  = mat('TunFix_Cable', (0.04, 0.04, 0.04, 1.0), 0.40)
T_JBOX   = mat('TunFix_JBox',  (0.30, 0.18, 0.10, 1.0), 0.55)
T_WARN   = mat('TunFix_Warn',  (0.85, 0.50, 0.10, 1.0), 0.70)
T_DEBRIS = mat('TunFix_Debris',(0.18, 0.14, 0.08, 1.0), 0.85)
T_POSTA  = mat('TunFix_PostA', (0.65, 0.55, 0.40, 1.0), 0.85)
T_POSTB  = mat('TunFix_PostB', (0.40, 0.30, 0.22, 1.0), 0.85)
T_RUST   = mat('TunFix_Rust',  (0.36, 0.16, 0.06, 1.0), 0.85, 0.2)
T_OPAQ   = mat('TunFix_DirtyWindow', (0.10, 0.12, 0.10, 1.0), 0.75)
T_LAMP   = emit_mat('TunFix_Lamp', (1.0, 0.78, 0.45), 4.0)

# ---- 2. HELPER ----
def make_box(name, w, d, h, x, y, z, rot_z, mat_obj):
    verts = [
        (-w/2, -d/2, 0), (w/2, -d/2, 0), (w/2, d/2, 0), (-w/2, d/2, 0),
        (-w/2, -d/2, h), (w/2, -d/2, h), (w/2, d/2, h), (-w/2, d/2, h),
    ]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me = bpy.data.meshes.new(name+'_mesh')
    me.from_pydata(verts, [], faces); me.update()
    if mat_obj: me.materials.append(mat_obj)
    o = bpy.data.objects.new(name, me)
    o.location = (x, y, z); o.rotation_euler.z = rot_z
    bpy.context.collection.objects.link(o)
    return o

# ---- 3. LIBRARY ----
TUNNEL_DEGS  = [0, 45, 135, 180, 225, 270, 315]
TUNNEL_HALF  = 13
TUNNEL_TOP_Z = 2.70
def is_tunnel(deg):
    deg = deg % 360
    for t in TUNNEL_DEGS:
        if min(abs(deg - t), 360 - abs(deg - t)) < TUNNEL_HALF: return True
    return False

# Original working positions (with wall fill behind to close the visible gap).
LOWER_R, LOWER_DEPTH, LOWER_FLOOR_Z, LOWER_TOP_Z = 7.00, 0.32, 0.05, 2.40
UPPER_R, UPPER_DEPTH, UPPER_FLOOR_Z, UPPER_TOP_Z = 5.80, 0.30, 2.85, 5.20
SHELF_THICK = 0.012
N_PANELS    = 56
DOME_FILL_R = 7.65

def build_section(prefix, R, DEPTH, Z_LO, Z_HI, N_LV, skip_tunnels, add_wall_fill):
    arc = 360 / N_PANELS
    cr = R - DEPTH/2
    panel_w = 2*cr*math.sin(math.radians(arc/2))*1.02
    sec_h = (Z_HI - Z_LO - SHELF_THICK) / N_LV
    for i in range(N_PANELS):
        deg = i * arc; rad = math.radians(deg)
        ca, sa = math.cos(rad), math.sin(rad)
        cx, cy = cr*ca, cr*sa
        rot_z = rad - math.pi/2
        levels = list(range(N_LV))
        skipped = skip_tunnels and is_tunnel(deg)
        if skipped:
            levels = [lv for lv in levels if Z_LO + lv*sec_h >= TUNNEL_TOP_Z]

        # WALL FILL behind this panel — fills the gap from bookcase back to dome edge.
        # Skipped at tunnel arcs in the lower section so doorways stay open.
        if add_wall_fill and not (skip_tunnels and is_tunnel(deg)):
            fill_thick = DOME_FILL_R - R          # ~0.65
            fill_center_r = R + fill_thick/2
            fx = fill_center_r * ca
            fy = fill_center_r * sa
            fill_w = panel_w * 1.06
            fill_h = Z_HI - Z_LO
            make_box(f'HH_LibFill_{prefix}_{i}', fill_w, fill_thick, fill_h,
                     fx, fy, Z_LO, rot_z, WALL_FILL)

        if not levels: continue
        z_lo = Z_LO + min(levels) * sec_h
        z_hi = Z_LO + (max(levels)+1) * sec_h
        h    = z_hi - z_lo
        bx = cx + (DEPTH/2 - 0.02) * ca
        by = cy + (DEPTH/2 - 0.02) * sa
        make_box(f'{prefix}_{i}_back', panel_w, 0.04, h, bx, by, z_lo, rot_z, WOOD_DARK)
        for side in (-1, 1):
            off = side * (panel_w/2 - 0.02)
            ex, ey = cx + off*sa, cy - off*ca
            make_box(f'{prefix}_{i}_side{side}', 0.04, DEPTH, h, ex, ey, z_lo, rot_z, WOOD_DARK)
        make_box(f'{prefix}_{i}_bot', panel_w, DEPTH, SHELF_THICK, cx, cy, z_lo, rot_z, WOOD_DARK)
        make_box(f'{prefix}_{i}_top', panel_w, DEPTH, SHELF_THICK, cx, cy, z_hi-SHELF_THICK, rot_z, WOOD_DARK)
        for k in range(1, len(levels)):
            zd = z_lo + k * sec_h
            make_box(f'{prefix}_{i}_shelf{k}', panel_w, DEPTH, SHELF_THICK, cx, cy, zd, rot_z, WOOD_DARK)

        # === BOOKS — smaller (denser) ===
        for lv in levels:
            zf = Z_LO + lv*sec_h + SHELF_THICK
            h_av  = sec_h - SHELF_THICK*2
            book_h = h_av * 0.86            # was 0.92  (a bit shorter)
            n_bk = max(11, int(panel_w / 0.058))   # was 0.075 → ~30% more books
            sp = (panel_w * 0.96) / n_bk
            xs = -panel_w/2 + 0.02 + sp/2
            book_d = DEPTH * 0.50           # was 0.55  (slightly thinner)
            ly = (DEPTH/2 - book_d/2 - 0.012)
            for b in range(n_bk):
                lx = xs + b * sp
                wx = cx + lx*sa + ly*ca
                wy = cy - lx*ca + ly*sa
                m = book_mats[(b + lv*5 + i*3) % len(book_mats)]
                make_box(f'{prefix}_book_{i}_{lv}_{b}',
                         sp*0.94, book_d, book_h,
                         wx, wy, zf, rot_z, m)

print('Building lower (with wall fill) / upper / mezzanine / columns...')
build_section('HH_LibWall_L', LOWER_R, LOWER_DEPTH, LOWER_FLOOR_Z, LOWER_TOP_Z, 3, True,  True)
build_section('HH_LibWall_U', UPPER_R, UPPER_DEPTH, UPPER_FLOOR_Z, UPPER_TOP_Z, 3, False, False)

# Carved columns (lower section)
for col_i in range(0, N_PANELS, 4):
    rad = math.radians(col_i * (360/N_PANELS))
    if is_tunnel(math.degrees(rad)): continue
    cx, cy = (LOWER_R - LOWER_DEPTH/2) * math.cos(rad), (LOWER_R - LOWER_DEPTH/2) * math.sin(rad)
    rot_z = rad - math.pi/2
    make_box(f'HH_LibColumn_{col_i}', 0.10, LOWER_DEPTH+0.04, LOWER_TOP_Z + 0.10,
             cx, cy, LOWER_FLOOR_Z, rot_z, WOOD_RICH)
    make_box(f'HH_LibColumn_cap_{col_i}', 0.18, LOWER_DEPTH+0.06, 0.10,
             cx, cy, LOWER_TOP_Z, rot_z, WOOD_RICH)
    make_box(f'HH_LibColumn_base_{col_i}', 0.18, LOWER_DEPTH+0.06, 0.10,
             cx, cy, LOWER_FLOOR_Z, rot_z, WOOD_RICH)

# Mezzanine ring + railing
MEZZ_OUTER, MEZZ_INNER, MEZZ_Z, MEZZ_THICK = 7.05, 5.60, 2.42, 0.12
for i in range(N_PANELS):
    deg = i * (360/N_PANELS); rad = math.radians(deg)
    if is_tunnel(deg): continue
    ca, sa = math.cos(rad), math.sin(rad)
    arc_step = 2*math.pi/N_PANELS
    panel_w = (MEZZ_OUTER + MEZZ_INNER)/2 * arc_step * 1.05
    cr2 = (MEZZ_OUTER + MEZZ_INNER)/2
    cx, cy = cr2*ca, cr2*sa
    rot_z = rad - math.pi/2
    make_box(f'HH_Mezz_floor_{i}', panel_w, MEZZ_OUTER - MEZZ_INNER, MEZZ_THICK, cx, cy, MEZZ_Z, rot_z, WOOD_RICH)
    rx, ry = MEZZ_INNER * ca, MEZZ_INNER * sa
    make_box(f'HH_Mezz_rail_{i}', panel_w, 0.03, 0.95, rx, ry, MEZZ_Z + MEZZ_THICK, rot_z, RAILING_MAT)
    make_box(f'HH_Mezz_railtop_{i}', panel_w, 0.10, 0.06, rx, ry, MEZZ_Z + MEZZ_THICK + 0.95, rot_z, WOOD_RICH)
    for b in range(3):
        t = -0.4 + b*0.4
        bx = rx + t * sa
        by = ry - t * ca
        make_box(f'HH_Mezz_baluster_{i}_{b}', 0.04, 0.04, 0.95, bx, by, MEZZ_Z + MEZZ_THICK, rot_z, RAILING_MAT)

# ---- 4. TUNNELS ----
print('Detailing tunnels...')
for o in bpy.data.objects:
    if o.name.startswith('TunnelWindow_'):
        o.data.materials.clear(); o.data.materials.append(T_OPAQ)
    if o.type == 'LIGHT' and 'TunLight' in o.name:
        o.data.color = (1.0, 0.78, 0.45)
        o.data.energy = max(15, o.data.energy * 0.4)

# Discover tunnels via DoorTop anchors (those always exist; TunnelFloor_ may
# already be replaced by TunFix_tile_* from a previous run).
tunnel_names = set()
for o in bpy.data.objects:
    m = re.match(r'TunnelDoorTop_Tunnel_(.+)_-?\d+$', o.name)
    if m: tunnel_names.add(m.group(1))
# Strip any short stub floors so we can drop our own door-to-door floor.
for o in list(bpy.data.objects):
    if o.name.startswith('TunnelFloor_'):
        bpy.data.objects.remove(o, do_unlink=True)

W_TUN, WALL_T, CEIL_Z, FLOOR_Z = 2.90, 0.08, 2.86, 0.0
added = 0
for tn in sorted(tunnel_names):
    door_tops = [o for o in bpy.data.objects if o.name.startswith(f'TunnelDoorTop_Tunnel_{tn}_')]
    if len(door_tops) < 2: continue
    p1, p2 = Vector(door_tops[0].location), Vector(door_tops[1].location)
    d = p2 - p1; d.z = 0; L = d.length
    if L < 0.1: continue
    d.normalize(); mid = (p1 + p2) / 2
    rot_z = math.atan2(d.y, d.x)
    cr, sr = math.cos(rot_z), math.sin(rot_z)
    L2 = L + 0.30

    tn_long = max(6, int(L2 / 0.75)); tn_wide = 4
    tw_l = L2 / tn_long; tw_w = (W_TUN + WALL_T) / tn_wide
    for ti in range(tn_long):
        for tj in range(tn_wide):
            lx = -L2/2 + (ti + 0.5) * tw_l
            ly = -(W_TUN+WALL_T)/2 + (tj + 0.5) * tw_w
            wx = mid.x + lx*cr - ly*sr
            wy = mid.y + lx*sr + ly*cr
            tm = T_TILE_L if (ti + tj) % 2 == 0 else T_TILE_D
            make_box(f'TunFix_tile_{tn}_{ti}_{tj}', tw_l*0.96, tw_w*0.96, 0.04, wx, wy, FLOOR_Z, rot_z, tm)
            added += 1

    make_box(f'TunFix_ceil_{tn}', L2, W_TUN + WALL_T*2, 0.06, mid.x, mid.y, CEIL_Z, rot_z, T_CEIL); added += 1
    for side in (-1, 1):
        ly = side * (W_TUN/2 + WALL_T/2 + 0.07)
        wx = mid.x - ly*sr; wy = mid.y + ly*cr
        make_box(f'TunFix_wall_{tn}_{side}', L2, WALL_T, CEIL_Z, wx, wy, FLOOR_Z, rot_z, T_WALL); added += 1

    for side in (-1, 1):
        for q in (-0.35, -0.15, 0.15, 0.35):
            lx = q * L; ly = side * (W_TUN/2 - 0.02)
            wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
            vh = 0.45 if abs(q) < 0.25 else 0.30
            vz = 0.35 if abs(q) < 0.25 else 1.55
            make_box(f'TunFix_vent_{tn}_{side}_{q}', 0.45, 0.04, vh, wx, wy, vz, rot_z, T_GRATE); added += 1

    for side in (-1, 1):
        ly = side * (W_TUN/2 - 0.06)
        wx = mid.x - ly*sr; wy = mid.y + ly*cr
        make_box(f'TunFix_cable_{tn}_{side}', L*0.94, 0.06, 0.04, wx, wy, CEIL_Z - 0.10, rot_z, T_CABLE); added += 1
        make_box(f'TunFix_cable2_{tn}_{side}', L*0.85, 0.05, 0.05, wx, wy, CEIL_Z - 0.20, rot_z, T_RUST); added += 1

    for jj, qx in enumerate([-0.30, 0.0, 0.30]):
        lx = qx * L; ly = -1 * (W_TUN/2 - 0.04)
        wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
        make_box(f'TunFix_jbox_{tn}_{jj}', 0.30, 0.10, 0.22, wx, wy, 1.95, rot_z, T_JBOX); added += 1

    for hi, qx in enumerate([-0.20, 0.10]):
        lx = qx * L; ly = (1 if hi % 2 else -1) * 0.20
        wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
        make_box(f'TunFix_droploop_{tn}_{hi}', 0.04, 0.04, 0.55, wx, wy, 2.30, rot_z, T_CABLE); added += 1

    for si, (lxp, lyo, ssz) in enumerate([(-0.25, 0.32, 0.40), (0.05, -0.45, 0.55), (0.30, 0.22, 0.35), (-0.10, -0.18, 0.30)]):
        lx = lxp * L
        wx = mid.x + lx*cr - lyo*sr; wy = mid.y + lx*sr + lyo*cr
        make_box(f'TunFix_stain_{tn}_{si}', ssz, ssz*0.7, 0.005, wx, wy, 0.045, rot_z + si*0.4, T_STAIN); added += 1

    for pi, qx in enumerate([-0.18, 0.22]):
        lx = qx * L; ly = 1 * (W_TUN/2 - 0.02)
        wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
        post = T_POSTA if pi == 0 else T_POSTB
        make_box(f'TunFix_poster_{tn}_{pi}', 0.40, 0.02, 0.55, wx, wy, 1.55, rot_z, post); added += 1

    for di, (lxp, lyo, dsz) in enumerate([(-0.32, -0.40, 0.28), (0.30, 0.35, 0.20)]):
        lx = lxp * L
        wx = mid.x + lx*cr - lyo*sr; wy = mid.y + lx*sr + lyo*cr
        make_box(f'TunFix_debris_{tn}_{di}', dsz, dsz*0.8, dsz*0.6, wx, wy, 0.04, rot_z + di*0.3, T_DEBRIS); added += 1

    for ei, dist in enumerate([-L*0.42, L*0.42]):
        wx = mid.x + dist*cr; wy = mid.y + dist*sr
        make_box(f'TunFix_warn_{tn}_{ei}', 0.08, W_TUN*0.85, 0.005, wx, wy, 0.05, rot_z, T_WARN); added += 1

    make_box(f'TunFix_lamp_{tn}', 0.55, 0.30, 0.04, mid.x, mid.y, CEIL_Z - 0.04, rot_z, T_LAMP); added += 1
    for side in (-1, 1):
        ly = side * (W_TUN/2 - 0.05)
        wx = mid.x - ly*sr; wy = mid.y + ly*cr
        make_box(f'TunFix_pipeR_{tn}_{side}', L*0.85, 0.10, 0.10, wx, wy, 0.55, rot_z, T_PIPE); added += 1

    # ============================================================
    # ===== HEAVY DETAIL PASS — ~80 extra props per tunnel ======
    # ============================================================

    # WALL PANELING — segmented metal panels both sides, with rivet-row highlights
    panel_n = max(5, int(L / 1.10))
    panel_w_seg = L / panel_n
    for side in (-1, 1):
        ly = side * (W_TUN/2 + 0.005)        # just inside the wall
        for pi in range(panel_n):
            lx = -L/2 + (pi + 0.5) * panel_w_seg
            wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
            # main panel (slightly recessed)
            make_box(f'TunFix_wpan_{tn}_{side}_{pi}', panel_w_seg*0.92, 0.012, 1.55,
                     wx, wy, 0.65, rot_z, T_WALL); added += 1
            # rivet row top + bottom
            for rr_z in (0.70, 2.18):
                make_box(f'TunFix_wpanRiv_{tn}_{side}_{pi}_{int(rr_z*10)}',
                         panel_w_seg*0.85, 0.018, 0.025,
                         wx, wy, rr_z, rot_z, T_RUST); added += 1

    # VERTICAL PIPES (3 per tunnel running floor → ceiling, alternating sides)
    n_vp = 4
    for vp in range(n_vp):
        side = 1 if vp % 2 == 0 else -1
        lx = -L*0.4 + vp * (L*0.8 / max(1, n_vp - 1))
        ly = side * (W_TUN/2 - 0.07)
        wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
        make_box(f'TunFix_vpipe_{tn}_{vp}', 0.10, 0.10, CEIL_Z - 0.05, wx, wy, 0.05, rot_z, T_PIPE); added += 1
        # collar at midpoint
        make_box(f'TunFix_vpipeColl_{tn}_{vp}', 0.16, 0.16, 0.08,
                 wx, wy, 1.40, rot_z, T_RUST); added += 1
        # valve wheel approximated as flat disc
        make_box(f'TunFix_vpipeValve_{tn}_{vp}', 0.30, 0.04, 0.30,
                 wx, wy, 0.95, rot_z + math.pi/2, T_RUST); added += 1

    # BREAKER BOXES — 4 per tunnel on alternating sides
    for bb in range(4):
        side = 1 if bb % 2 == 0 else -1
        lx = -L*0.35 + bb * (L*0.7 / 3)
        ly = side * (W_TUN/2 - 0.04)
        wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
        # main box
        make_box(f'TunFix_brk_{tn}_{bb}', 0.26, 0.10, 0.36, wx, wy, 1.40, rot_z, T_JBOX); added += 1
        # door panel highlight
        make_box(f'TunFix_brkDoor_{tn}_{bb}', 0.20, 0.025, 0.30, wx, wy, 1.44, rot_z, T_RUST); added += 1
        # tiny indicator light dot
        wx2 = wx - 0.08*sr; wy2 = wy + 0.08*cr
        make_box(f'TunFix_brkLight_{tn}_{bb}', 0.04, 0.018, 0.04,
                 wx + 0.04*sr*-side, wy - 0.04*cr*-side, 1.65, rot_z, T_WARN); added += 1

    # FLOOR CRACKS — thin dark lines breaking up the tile pattern
    for ci in range(8):
        lxp = -0.45 + ci * 0.115
        lx = lxp * L
        lyo = ((ci * 37) % 100 - 50) / 100 * 0.9
        wx = mid.x + lx*cr - lyo*sr; wy = mid.y + lx*sr + lyo*cr
        crack_l = 0.25 + (ci % 3) * 0.12
        make_box(f'TunFix_crack_{tn}_{ci}', crack_l, 0.008, 0.002,
                 wx, wy, 0.05, rot_z + (ci % 5) * 0.4, T_CABLE); added += 1

    # FLOOR DRAINS — 2 small grate insets per tunnel
    for di_d in range(2):
        lxp = -0.20 if di_d == 0 else 0.25
        lx = lxp * L
        lyo = (-1 if di_d == 0 else 1) * 0.55
        wx = mid.x + lx*cr - lyo*sr; wy = mid.y + lx*sr + lyo*cr
        make_box(f'TunFix_drain_{tn}_{di_d}', 0.30, 0.30, 0.012,
                 wx, wy, 0.045, rot_z, T_GRATE); added += 1
        # 4 grate bars
        for gb in range(4):
            offy = -0.10 + gb * 0.066
            wx2 = wx + offy * cr
            wy2 = wy + offy * sr
            make_box(f'TunFix_drainBar_{tn}_{di_d}_{gb}', 0.005, 0.30, 0.018,
                     wx2, wy2, 0.046, rot_z, T_RUST); added += 1

    # FLOOR CAUTION CHEVRONS — yellow diagonal stripe set near each door
    for ci_c, dist in enumerate([-L*0.45, L*0.45]):
        for sj in range(4):
            lx = dist + (sj - 1.5) * 0.16 * (1 if ci_c == 0 else -1)
            wx = mid.x + lx*cr; wy = mid.y + lx*sr
            make_box(f'TunFix_chev_{tn}_{ci_c}_{sj}', 0.08, W_TUN*0.7, 0.005,
                     wx, wy, 0.052, rot_z, T_WARN); added += 1

    # WALL SIGNS — numbered/exit-style plates at varied positions
    for si_w, (qx, side, sw, sh) in enumerate([
        (-0.40, -1, 0.30, 0.20), (0.40,  1, 0.30, 0.20),
        (-0.05, -1, 0.20, 0.36), (0.10,  1, 0.20, 0.36),
    ]):
        lx = qx * L; ly = side * (W_TUN/2 - 0.02)
        wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
        sign_mat = T_WARN if si_w < 2 else T_POSTA
        make_box(f'TunFix_sign_{tn}_{si_w}', sw, 0.015, sh,
                 wx, wy, 2.00, rot_z, sign_mat); added += 1

    # SPEAKERS / PA — small wall boxes high up
    for sp_i, qx in enumerate([-0.30, 0.30]):
        side = 1 if sp_i % 2 == 0 else -1
        lx = qx * L; ly = side * (W_TUN/2 - 0.04)
        wx = mid.x + lx*cr - ly*sr; wy = mid.y + lx*sr + ly*cr
        make_box(f'TunFix_speaker_{tn}_{sp_i}', 0.22, 0.10, 0.26,
                 wx, wy, 2.40, rot_z, T_JBOX); added += 1
        make_box(f'TunFix_speakerCone_{tn}_{sp_i}', 0.18, 0.025, 0.22,
                 wx, wy, 2.42, rot_z, T_GRATE); added += 1

    # DEBRIS — varied scattered junk (broken tile pieces, cans, paper)
    for db, (lxp, lyo, w, d, h, mt) in enumerate([
        (-0.40, -0.55, 0.10, 0.10, 0.10, T_DEBRIS),
        (-0.18, 0.50, 0.20, 0.06, 0.06, T_RUST),
        ( 0.05, -0.60, 0.32, 0.18, 0.04, T_DEBRIS),
        ( 0.32, 0.55, 0.12, 0.12, 0.16, T_DEBRIS),
        ( 0.18, -0.05, 0.06, 0.06, 0.18, T_RUST),
        (-0.32, 0.20, 0.22, 0.10, 0.06, T_POSTB),
    ]):
        lx = lxp * L
        wx = mid.x + lx*cr - lyo*sr; wy = mid.y + lx*sr + lyo*cr
        make_box(f'TunFix_debrisX_{tn}_{db}', w, d, h,
                 wx, wy, 0.05, rot_z + db*0.7, mt); added += 1

    # HANGING CHAINS / DROP CABLES — vertical thin lines from ceiling
    for hc in range(3):
        lxp = -0.30 + hc * 0.30
        lyo = (-1 if hc % 2 else 1) * 0.30
        lx = lxp * L
        wx = mid.x + lx*cr - lyo*sr; wy = mid.y + lx*sr + lyo*cr
        make_box(f'TunFix_chain_{tn}_{hc}', 0.025, 0.025, 0.85,
                 wx, wy, 1.95, rot_z, T_CABLE); added += 1
        # tiny attachment box on ceiling
        make_box(f'TunFix_chainAtt_{tn}_{hc}', 0.10, 0.10, 0.04,
                 wx, wy, CEIL_Z - 0.05, rot_z, T_RUST); added += 1

    # EXTRA CEILING CAGE LIGHTS (2 per tunnel — one at each quarter, mostly off)
    for cl_i, qx in enumerate([-0.30, 0.30]):
        lx = qx * L
        wx = mid.x + lx*cr; wy = mid.y + lx*sr
        # bracket / housing
        make_box(f'TunFix_clHouse_{tn}_{cl_i}', 0.30, 0.20, 0.06,
                 wx, wy, CEIL_Z - 0.06, rot_z, T_RUST); added += 1
        # lamp itself — only one of the two lights (50%) emits
        m = T_LAMP if cl_i == 0 else T_GRATE
        make_box(f'TunFix_clLamp_{tn}_{cl_i}', 0.22, 0.16, 0.04,
                 wx, wy, CEIL_Z - 0.10, rot_z, m); added += 1
        # 3 cage bars under the light
        for cb in range(3):
            offy = -0.07 + cb * 0.07
            wx2 = wx + offy * cr; wy2 = wy + offy * sr
            make_box(f'TunFix_clBar_{tn}_{cl_i}_{cb}', 0.005, 0.16, 0.10,
                     wx2, wy2, CEIL_Z - 0.16, rot_z, T_RUST); added += 1

    # FLOOR EDGE TRIM (thin baseboard along both walls)
    for side in (-1, 1):
        ly = side * (W_TUN/2 - 0.02)
        wx = mid.x - ly*sr; wy = mid.y + ly*cr
        make_box(f'TunFix_baseboard_{tn}_{side}', L, 0.04, 0.08,
                 wx, wy, 0.05, rot_z, T_RUST); added += 1

    # CRATE STACK at one corner near a door
    sx_corner = mid.x + L*0.40*cr - (W_TUN/2 - 0.30)*sr
    sy_corner = mid.y + L*0.40*sr + (W_TUN/2 - 0.30)*cr
    for ci_st in range(3):
        make_box(f'TunFix_crate_{tn}_{ci_st}', 0.45, 0.40, 0.34,
                 sx_corner + ci_st*0.04, sy_corner + ci_st*0.02,
                 0.05 + ci_st * 0.34, rot_z + ci_st*0.06, T_DEBRIS); added += 1

print(f'Added {added} tunnel objects')

print('EXPORTING...')
bpy.ops.export_scene.gltf(filepath='/tmp/biosphere.glb', export_format='GLB', export_apply=True)
# Persist the changes back into the .blend so VS sees them in Blender's GUI.
bpy.ops.wm.save_mainfile()
print('EXPORT + .BLEND SAVED')
