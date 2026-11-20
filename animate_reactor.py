import bpy
import math
from mathutils import Vector

# ============================================================
# SCHEMATIC PRIMARY-LOOP ANIMATION FOR THE CONCEPTUAL MSR SCENE
# Run AFTER build_conceptual_reactor.py in Blender.
# This is a visual explanation, NOT a CFD/fluid-dynamics solution.
# ============================================================

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 240
scene.render.fps = 30

collection_name = "MSR_Animation"
old = bpy.data.collections.get(collection_name)
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
anim_col = bpy.data.collections.new(collection_name)
scene.collection.children.link(anim_col)

def put_in_anim_collection(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    anim_col.objects.link(obj)
    return obj

def emission_material(name, color, strength):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    mat.node_tree.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat

hot_glow = emission_material("Animation | hot salt tracer glow", (1.0, 0.19, 0.025), 3.0)
cold_glow = emission_material("Animation | return salt tracer glow", (0.08, 0.42, 1.0), 2.2)
cr_glow = emission_material("Animation | chromium release glow", (0.65, 1.0, 0.18), 2.5)

# Schematic flow path from vessel outlet through the primary loop and back.
# The path is a communication device; its geometry is not a hydraulic design.
path = [
    (1.62, 0.0, 4.25),
    (2.35, 0.0, 4.25),
    (3.10, 0.0, 4.05),
    (3.65, 0.0, 3.55),
    (4.25, 0.0, 3.85),
    (4.85, 0.0, 3.85),
    (5.35, 0.0, 3.65),
    (5.35, 0.0, 2.75),
    (5.35, 0.0, 1.85),
    (4.85, 0.0, 1.65),
    (4.20, 0.0, 1.65),
    (3.40, 0.0, 1.55),
    (2.55, 0.0, 1.35),
    (1.62, 0.0, 1.35),
    (1.35, 0.0, 2.10),
    (1.35, 0.0, 3.20),
    (1.62, 0.0, 4.25),
]

def make_pipe(name, points, radius, material):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 24
    curve.bevel_depth = radius
    curve.bevel_resolution = 8
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new(name, curve)
    anim_col.objects.link(obj)
    obj.data.materials.append(material)
    return obj

# Add connecting schematic pipe segments to visually complete the circuit.
pipe_mat = bpy.data.materials.get("Primary loop | nickel alloy")
if pipe_mat is None:
    pipe_mat = emission_material("Animation | schematic pipe", (0.35, 0.48, 0.60), 0.35)
make_pipe("Animation | hot-side connection", path[:7], 0.105, pipe_mat)
make_pipe("Animation | heat-exchanger downcomer", path[6:10], 0.105, pipe_mat)
make_pipe("Animation | cold-side return", path[9:], 0.105, pipe_mat)

# Arc-length interpolation lets each tracer move at a nearly constant visual speed.
def path_lengths(points):
    lengths = [0.0]
    for a, b in zip(points[:-1], points[1:]):
        lengths.append(lengths[-1] + (Vector(b)-Vector(a)).length)
    return lengths

lengths = path_lengths(path)
total = lengths[-1]

def point_at_fraction(f):
    d = (f % 1.0) * total
    for i in range(len(lengths)-1):
        if lengths[i] <= d <= lengths[i+1]:
            span = lengths[i+1] - lengths[i]
            q = 0 if span == 0 else (d-lengths[i])/span
            return Vector(path[i]).lerp(Vector(path[i+1]), q)
    return Vector(path[-1])

def add_flow_bead(name, material, radius, phase, frames=240):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=radius)
    obj = put_in_anim_collection(bpy.context.object)
    obj.name = name
    obj.data.materials.append(material)
    obj.location = point_at_fraction(phase)
    obj.keyframe_insert(data_path="location", frame=1)
    obj.location = point_at_fraction(phase + 1.0)
    obj.keyframe_insert(data_path="location", frame=frames+1)
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'
            fc.modifiers.new('CYCLES')
    return obj

# Several tracer markers make direction and circulation visible in the render.
for i in range(12):
    add_flow_bead(f"Salt circulation tracer {i+1:02d}",
                  hot_glow if i % 2 == 0 else cold_glow,
                  0.075 if i % 3 else 0.095, i/12.0)

# Small visual chromium-release markers drift from the inner vessel wall
# toward the salt volume. They represent the model's release concept only.
for i in range(7):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.045)
    dot = put_in_anim_collection(bpy.context.object)
    dot.name = f"Illustrative chromium release marker {i+1:02d}"
    dot.data.materials.append(cr_glow)
    start = Vector((1.25 + 0.10*math.sin(i), -0.95, 1.55 + i*0.36))
    end = Vector((0.55 + 0.12*math.cos(i), -0.55, 1.95 + i*0.31))
    dot.location = start
    dot.keyframe_insert(data_path="location", frame=1 + i*7)
    dot.location = end
    dot.keyframe_insert(data_path="location", frame=90 + i*7)
    dot.location = start
    dot.keyframe_insert(data_path="location", frame=180 + i*7)
    if dot.animation_data and dot.animation_data.action:
        for fc in dot.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'

# Animated explanatory labels.
def add_label(body, name, loc, size, material):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.size = size
    curve.extrude = 0.001
    obj = bpy.data.objects.new(name, curve)
    anim_col.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (math.radians(90), 0, 0)
    obj.data.materials.append(material)
    return obj

label_mat = bpy.data.materials.get("Instrumentation | brass") or hot_glow
add_label("SCHEMATIC SALT CIRCULATION", "Animation label | circulation",
          (2.2, -2.35, 5.45), 0.19, label_mat)
add_label("ILLUSTRATIVE CHROMIUM RELEASE", "Animation label | chromium",
          (-2.1, -2.35, 0.45), 0.15, cr_glow)

scene.frame_set(1)
print("Animation added: 240 frames at 30 fps. Scrub the timeline or render an animation.")
print("Reminder: moving markers are schematic; no CFD or physical flow field is solved.")
