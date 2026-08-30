#!/usr/bin/env python3
"""Render a painted mini glb WITHOUT its base, producing:
  <slug>-standing.png  — full body, no base, front view
  <slug>-portrait.png  — face close-up
Usage: blender --background --python char_ref.py -- <glb> <out_dir>
"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
glb = argv[0]
out_dir = argv[1] if len(argv) > 1 else "/tmp"
slug = os.path.basename(glb).replace("-painted.glb", "").replace(".glb", "")
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

world = bpy.data.worlds.new('W'); world.use_nodes = True
nt = world.node_tree; bg = nt.nodes.get('Background')
env = nt.nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load('/Applications/Blender.app/Contents/Resources/5.2/datafiles/studiolights/world/studio.exr')
nt.links.new(env.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 1.2
scene.world = world

def area(name, loc, size, energy, color=(1,1,1)):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = energy; d.size = size; d.color = color
    ob = bpy.data.objects.new(name, d); ob.location = loc
    scene.collection.objects.link(ob)
    ob.rotation_euler = (Vector((0,0.5,0)) - loc).to_track_quat('-Z','Y').to_euler()
area('Key', Vector((3,-3,4)), 1.5, 300)
area('Fill', Vector((-3,1.5,2)), 2.0, 90, (0.85,0.9,1))
area('Rim', Vector((-1.5,3,3)), 1.5, 220, (0.7,0.8,1))

cam_data = bpy.data.cameras.new('Cam'); cam_data.lens = 50
cam = bpy.data.objects.new('Cam', cam_data)
scene.collection.objects.link(cam); scene.camera = cam

bpy.ops.import_scene.gltf(filepath=glb)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
obj = meshes[0]
me = obj.data

V = np.array([obj.matrix_world @ v.co for v in me.vertices])
fn = np.array([obj.matrix_world.to_3x3() @ p.normal for p in me.polygons])
fn = fn / (np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9)
face_area = np.array([p.area for p in me.polygons])

# ---- up axis = axis with the most flat-face AREA (the base disc is big + flat) ----
flat_area = [float(face_area[abs(fn[:, a]) > 0.9].sum()) for a in range(3)]
up = int(np.argmax(flat_area))

c = V[:, up]
cmin, cmax = c.min(), c.max(); h = cmax - cmin

# ---- base top: FIXED cut at 13% of height above the bottom (base is a consistent fraction) ----
base_top = cmin + 0.13 * h
# (optional refine: skip — the flat-face detection was unreliable)

# ---- delete base ----
cut = base_top - 0.015 * h
del_idx = [i for i in range(len(V)) if c[i] < cut]
if del_idx:
    bpy.ops.object.mode_set(mode='OBJECT')
    for i in del_idx:
        me.vertices[i].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')

# ---- recompute bounds (no base) ----
V2 = np.array([obj.matrix_world @ v.co for v in me.vertices])
minv = Vector(V2.min(0)); maxv = Vector(V2.max(0))
center = (minv + maxv) / 2
height = (maxv - minv).length if False else (maxv[up] - minv[up])
ext = maxv - minv
maxdim = max(ext.x, ext.y, ext.z) or 1.0

def aim(pos, target):
    cam.location = Vector(pos)
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z','Y').to_euler()

# ---- standing (front = -Y) ----
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
dist = maxdim * 1.7
mid = center[up] if False else (minv[up] + maxv[up]) / 2
aim((center.x, center.y - dist, mid + 0.1*maxdim), (center.x, center.y, mid + 0.1*maxdim))
scene.render.filepath = os.path.join(out_dir, slug + "-standing.png")
bpy.ops.render.render(write_still=True)

# ---- face portrait (head = top ~12% of height) ----
head_c = maxv[up] - 0.10 * height
# face is at the front of the head; frame tight
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
pdist = height * 0.30
aim((center.x, center.y - pdist, head_c), (center.x, center.y, head_c))
scene.render.filepath = os.path.join(out_dir, slug + "-portrait.png")
bpy.ops.render.render(write_still=True)

print(f"{slug}: up_axis={up} height={h:.2f} base_top={base_top:.2f} -> done")
