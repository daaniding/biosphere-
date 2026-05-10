"""Headless export of biosphere_zero.blend → web/scene.glb.

Run with: python3 scripts/export_glb.py
Requires: pip install bpy
"""
import os
import sys
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(ROOT, "blend", "biosphere_zero.blend")
OUT = os.path.join(ROOT, "web", "scene.glb")

if not os.path.exists(BLEND):
    sys.exit(f"missing: {BLEND}")

bpy.ops.wm.open_mainfile(filepath=BLEND)

os.makedirs(os.path.dirname(OUT), exist_ok=True)

bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    export_apply=True,
    export_cameras=False,
    export_lights=True,
    export_yup=True,
    export_extras=False,
    export_animations=False,
    export_skins=False,
    export_morph=False,
    export_draco_mesh_compression_enable=False,
    use_selection=False,
)

size_mb = os.path.getsize(OUT) / (1024 * 1024)
print(f"wrote {OUT} ({size_mb:.1f} MB)")
