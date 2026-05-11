# Biosphere Zero — Build Scripts

Python scripts that rebuild Heart Hall's 2-story library + heavy tunnel detail
on top of the source `.blend`. Run them headless from the repo root.

## Run

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
    --background blend/biosphere_zero.blend \
    --python scripts/build_library_and_tunnels.py
```

Output is written to `/tmp/biosphere.glb` (configurable in the script).

## What it does

### Heart Hall library
- Removes leftover single-book debris (`HH_BookCorner_*`, `HH_BookL/RCover`,
  `HH_BookL/RPage`, `HH_BookSpine`, `HH_PageEdge_*`).
- Removes any `DECOR_*` items inside the HH dome (busts / candles / floor
  lamps / banners / plinths) that the user does not want by the bookcases.
- Builds 56-panel **lower bookcases** at radius 7.0 (3 levels) with a wall fill
  to the dome edge so no gap is visible.
- Builds **upper bookcases** at radius 5.8 (3 levels), top z = 5.20.
- Adds **carved columns** between every 4 panels.
- Adds an **annular mezzanine floor** (z = 2.42, inner r = 5.60, outer r = 7.05)
  with railing + balusters; gaps left at every tunnel direction.
- 12 deep "library" book colours cycled deterministically (no patchwork).
- All materials use **Principled BSDF nodes** (so glTF export carries colour).

### Tunnels (all 14)
- Replaces short floor stubs with full **door-to-door tile floors** (alternating
  light/dark squares), so the gap to each dome edge is closed.
- Adds solid walls + ceiling so Mars is no longer visible through the gaps.
- Makes existing window panels opaque (dirty grime).
- Heavy detail props per tunnel (~80):
  segmented wall paneling with rivet rows, vertical pipes with valve wheels,
  breaker boxes with indicator lights, floor cracks, floor drains with grates,
  caution chevrons, wall signs, PA speakers, hanging chains, debris piles,
  ceiling cage lights (one alive, one dead), baseboard trim, crate stack.
- Dims the existing `TunLight` lamps to a warm 40 % energy.

## Re-runs are safe

The script's first step strips its own previous additions
(`HH_LibWall_*`, `HH_LibFill_*`, `HH_LibColumn_*`, `HH_Mezz_*`, `TunFix_*`,
plus the leftover book-debris and HH `DECOR_*` items), so you can re-run after
modifying the source `.blend` without leftover ghost objects.
