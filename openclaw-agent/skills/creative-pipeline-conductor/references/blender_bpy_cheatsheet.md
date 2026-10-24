# Blender (bpy) Scripting Cheatsheet for Automated Pipelines

When operating Blender via Python (`bpy`) in headless or interactive mode:

## 1. Scene Reset & Basics
```python
import bpy

# Clear existing objects
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Set Render Engine & Settings
scene.render.engine = 'BLENDER_EEVEE_NEXT' # Or 'CYCLES'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 120
```

## 2. Camera Setup & Animation
```python
# Create Camera
cam_data = bpy.data.cameras.new("MainCamera")
cam_data.lens = 35 # 35mm focal length
cam_obj = bpy.data.objects.new("MainCamera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Animate Camera Position
cam_obj.location = (0, -10, 3)
cam_obj.rotation_euler = (1.3, 0, 0)
cam_obj.keyframe_insert(data_path="location", frame=1)
cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

cam_obj.location = (0, -5, 1.5)
cam_obj.keyframe_insert(data_path="location", frame=120)
```

## 3. Lighting & World
```python
# Sun Light
light_data = bpy.data.lights.new(name="KeySun", type='SUN')
light_data.energy = 5.0
light_obj = bpy.data.objects.new(name="KeySun", object_data=light_data)
scene.collection.objects.link(light_obj)
light_obj.rotation_euler = (0.7, 0.2, 0.5)
```

## 4. Multi-Pass Rendering Setup (Compositor EXR)
```python
scene.use_nodes = True
tree = scene.node_tree
links = tree.links

# Enable Render Passes
view_layer = scene.view_layers["ViewLayer"]
view_layer.use_pass_z = True
view_layer.use_pass_normal = True
view_layer.use_pass_ambient_occlusion = True
view_layer.use_pass_shadow = True

# Set Output to OpenEXR MultiLayer
scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
scene.render.image_settings.color_depth = '16'
scene.render.filepath = "//renders/frame_"
```

## 5. Headless Execution
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P generate_scene.py
```
