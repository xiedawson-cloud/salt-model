import bpy
import math
from mathutils import Vector

# ============================================================
# CONCEPTUAL MOLTEN SALT REACTOR — AUTOMATIC SCENE BUILDER
# Educational visualization only. Not an engineering design.
# Run this script in Blender's Scripting workspace.
# ============================================================

# ---------- Scene setup ----------
# Keep the user's existing objects. All generated objects go
# into a clearly named collection so the scene is easy to manage.
COLLECTION_NAME = "MSR_Concept_Model"
old = bpy.data.collections.get(COLLECTION_NAME)
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)

col = bpy.data.collections.new(COLLECTION_NAME)
bpy.context.scene.collection.children.link(col)

def move_to_collection(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

def mat(name, color, metallic=0.0, roughness=0.4, alpha=1.0, transmission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, alpha)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, alpha)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    if "Alpha" in bs.inputs:
        bs.inputs["Alpha"].default_value = alpha
    if "Transmission" in bs.inputs:
        bs.inputs["Transmission"].default_value = transmission
    if alpha < 1:
        m.surface_render_method = 'DITHERED'
    return m

steel = mat("Vessel | brushed stainless steel", (0.34, 0.42, 0.49), 0.82, 0.26)
vessel_shell = mat("Vessel shell | semi-transparent cutaway", (0.30, 0.40, 0.48), 0.65, 0.28, 0.24, 0.25)
dark_steel = mat("Structural steel | dark", (0.075, 0.10, 0.13), 0.75, 0.3)
graphite = mat("Graphite moderator", (0.12, 0.15, 0.17), 0.15, 0.65)
salt = mat("Molten fluoride salt | amber", (0.95, 0.30, 0.035), 0.25, 0.22, 0.88, 0.12)
pipe_mat = mat("Primary loop | nickel alloy", (0.55, 0.62, 0.68), 0.8, 0.23)
ceramic = mat("Insulation | ceramic", (0.72, 0.70, 0.61), 0.05, 0.8)
blue = mat("Coolant | blue", (0.035, 0.28, 0.72), 0.2, 0.25)
gold = mat("Instrumentation | brass", (0.72, 0.43, 0.12), 0.72, 0.25)
floor_mat = mat("Studio floor", (0.025, 0.035, 0.05), 0.15, 0.7)

def bevel(obj, width=0.06, segments=3):
    mod = obj.modifiers.new("Soft machined edges", "BEVEL")
    mod.width = width
    mod.segments = segments
    obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj

def cylinder(name, radius, depth, loc, material, vertices=96, bevel_width=0.03):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = move_to_collection(bpy.context.object)
    o.name = name
    o.data.materials.append(material)
    if bevel_width:
        bevel(o, bevel_width)
    return o

def torus(name, major, minor, loc, material, rotation=None):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major, minor_radius=minor,
        major_segments=96, minor_segments=16, location=loc
    )
    o = move_to_collection(bpy.context.object)
    o.name = name
    if rotation:
        o.rotation_euler = rotation
    o.data.materials.append(material)
    return o

def cube(name, loc, scale, material, bevel_width=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = move_to_collection(bpy.context.object)
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel_width:
        bevel(o, bevel_width)
    return o

def pipe_curve(name, points, radius, material):
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
    col.objects.link(obj)
    obj.data.materials.append(material)
    return obj

def text_obj(body, name, loc, size, material, rotation=(0,0,0)):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.size = size
    curve.extrude = 0.002
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    return obj

# ---------- Reactor vessel ----------
# Main vessel is represented as a dark metallic cylindrical shell.
cylinder("Reactor vessel | outer shell", 2.05, 5.25, (0, 0, 2.95), vessel_shell, bevel_width=0.10)
cylinder("Vessel lower head", 1.98, 0.35, (0, 0, 0.30), dark_steel, bevel_width=0.12)
cylinder("Vessel top flange", 2.28, 0.28, (0, 0, 5.62), dark_steel, bevel_width=0.05)
torus("Flange gasket", 2.12, 0.045, (0, 0, 5.78), gold)

# Front viewing window/cutaway: a translucent inset panel gives a readable
# impression of the internal region without implying a real pressure boundary.
window_mat = mat("Cutaway window | translucent", (0.10, 0.20, 0.25), 0.15, 0.2, 0.20, 0.35)
cube("Cutaway viewing panel", (0, -1.93, 3.0), (2.85, 0.055, 4.65), window_mat, 0.08)
# Dark rim around the cutaway panel
for x in (-1.48, 1.48):
    cube("Cutaway frame | vertical", (x, -1.99, 3.0), (0.10, 0.12, 4.85), dark_steel, 0.025)
for z in (0.58, 5.42):
    cube("Cutaway frame | horizontal", (0, -1.99, z), (3.05, 0.12, 0.10), dark_steel, 0.025)

# Internal salt volume and core
cylinder("Molten salt inventory | visual volume", 1.72, 2.55, (0, 0, 2.35), salt, bevel_width=0.06)
cylinder("Core support plenum", 1.55, 0.28, (0, 0, 0.95), dark_steel, bevel_width=0.04)

# Graphite moderator columns arranged in rings
for ring_radius, count, rod_radius in ((0.48, 8, 0.13), (0.98, 14, 0.12), (1.40, 18, 0.105)):
    for i in range(count):
        a = 2 * math.pi * i / count
        x, y = ring_radius * math.cos(a), ring_radius * math.sin(a)
        rod = cylinder("Graphite moderator column", rod_radius, 2.45,
                       (x, y, 2.35), graphite, vertices=48, bevel_width=0.025)
# Central core channel
cylinder("Central fuel-salt channel", 0.22, 2.5, (0, 0, 2.35), gold, vertices=64, bevel_width=0.025)

# Top penetrations / instrumentation
for x, y in ((-0.95, 0), (0.95, 0), (0, 0.95), (0, -0.95)):
    cylinder("Top penetration nozzle", 0.16, 0.55, (x, y, 5.95), pipe_mat, vertices=48)
    torus("Nozzle collar", 0.17, 0.035, (x, y, 6.18), gold)

# External vessel support legs
for x in (-1.35, 1.35):
    for y in (-1.15, 1.15):
        cube("Vessel support leg", (x, y, -0.05), (0.28, 0.28, 1.0), dark_steel, 0.06)
        cube("Support foot", (x, y, -0.53), (0.55, 0.48, 0.12), steel, 0.025)

# ---------- Primary loop piping ----------
# Pipe runs leave the upper side of the vessel, pass through pump/heat exchanger,
# and return at a lower elevation. The path is schematic.
pipe_curve("Primary hot-leg pipe", [
    (1.65, 0.0, 4.25), (2.45, 0.0, 4.25), (3.0, 0.0, 4.25),
    (3.45, 0.0, 3.85), (4.25, 0.0, 3.85)
], 0.13, pipe_mat)
pipe_curve("Primary cold-leg pipe", [
    (4.25, 0.0, 1.65), (3.55, 0.0, 1.65), (3.0, 0.0, 1.65),
    (2.45, 0.0, 1.35), (1.65, 0.0, 1.35)
], 0.13, pipe_mat)

# Pump body and motor
cylinder("Primary circulation pump | casing", 0.58, 0.72, (3.65, 0, 2.75), dark_steel, bevel_width=0.10)
cylinder("Pump motor", 0.42, 0.95, (3.65, 0, 3.55), steel, bevel_width=0.08)
torus("Pump casing seam", 0.50, 0.045, (3.65, 0, 2.75), gold, rotation=(math.pi/2,0,0))
cube("Pump mounting skid", (3.65, 0, 1.95), (1.25, 1.0, 0.16), dark_steel, 0.04)

# Heat exchanger bundle at the right
cube("Heat exchanger shell", (5.35, 0, 2.75), (1.35, 1.15, 2.25), steel, 0.18)
for z in (1.78, 3.72):
    cube("Heat exchanger end plate", (5.35, 0, z), (1.48, 1.25, 0.16), dark_steel, 0.06)
# visible tube bundle on front face
for x in (4.92, 5.20, 5.48, 5.76):
    for z in (2.25, 2.60, 2.95, 3.30):
        cylinder("Heat exchanger tube end", 0.075, 0.08, (x, -0.61, z),
                 gold, vertices=32, bevel_width=0.01)
# Secondary coolant connections
pipe_curve("Secondary coolant inlet", [
    (5.35, 0.0, 3.92), (5.35, 0.0, 4.55), (6.1, 0.0, 4.55)
], 0.09, blue)
pipe_curve("Secondary coolant outlet", [
    (5.35, 0.0, 1.58), (5.35, 0.0, 0.95), (6.1, 0.0, 0.95)
], 0.09, blue)

# Pipe flanges and joints
for x, z in ((2.55,4.25), (2.55,1.35), (4.25,3.85), (4.25,1.65)):
    torus("Primary loop pipe flange", 0.19, 0.045, (x, 0, z), gold, rotation=(math.pi/2,0,0))

# ---------- Instrumentation and structural details ----------
# Thermowell/instrument stems
for x, z in ((-1.95,4.55), (-1.95,2.0), (1.95,3.2)):
    pipe_curve("Instrument probe", [(x,0,z), (x*1.18,0,z+0.12), (x*1.18,0,z+0.55)],
               0.045, gold)
    cylinder("Instrument transmitter", 0.12, 0.18, (x*1.18,0,z+0.62), gold, vertices=48)

# A few external stiffening bands
for z in (1.0, 1.45, 4.75, 5.05):
    torus("Vessel stiffening band", 2.04, 0.045, (0,0,z), dark_steel)

# ---------- Labels ----------
# Labels are positioned in the presentation plane, facing the camera.
label_rot = (math.radians(90), 0, 0)
text_obj("MOLTEN SALT REACTOR", "Title", (-2.2, -3.0, 7.0), 0.34, steel, label_rot)
text_obj("CONCEPTUAL CUTAWAY  |  NOT TO SCALE", "Subtitle", (-2.2, -3.0, 6.62), 0.15, gold, label_rot)

# ---------- Ground, camera, lighting ----------
cube("Display plinth", (1.8, 0, -0.72), (9.0, 5.8, 0.28), dark_steel, 0.12)
cube("Studio ground", (1.8, 0, -0.95), (200, 200, 0.12), floor_mat, 0.0)

def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.camera_add(location=(10.8, -16.5, 10.2))
camera = move_to_collection(bpy.context.object)
camera.name = "Presentation Camera"
aim(camera, (1.8, 0, 2.75))
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 12.7
bpy.context.scene.camera = camera

def area_light(name, loc, energy, size, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l = move_to_collection(bpy.context.object)
    l.name = name
    l.data.energy = energy
    l.data.shape = 'DISK'
    l.data.size = size
    l.data.color = color
    aim(l, target)

area_light("Key | large softbox", (1, -8, 11), 1800, 8, (0.78,0.86,1.0), (1,0,2.5))
area_light("Rim | warm", (5, 4, 8), 2200, 6, (1.0,0.55,0.25), (1,0,3))
area_light("Fill | cool", (-7, -1, 4), 1200, 5, (0.35,0.58,1.0), (0,0,2.5))

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, "SceneEEVEE") else 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.world.color = (0.025, 0.025, 0.025)

# Set viewport to material preview and frame the generated assembly.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_distance = 13
            area.spaces.active.region_3d.view_location = (1.7, 0, 2.7)
            area.spaces.active.region_3d.view_perspective = 'CAMERA'

# Select the reactor vessel to make the collection easy to find.
bpy.ops.object.select_all(action='DESELECT')
vessel = bpy.data.objects.get("Reactor vessel | outer shell")
if vessel:
    vessel.select_set(True)
    bpy.context.view_layer.objects.active = vessel

print("Conceptual MSR scene created. Save this file as a new .blend project.")
