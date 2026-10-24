# Adobe After Effects ExtendScript (JSX) Cheatsheet

After Effects can be fully scripted using JavaScript / ExtendScript (`.jsx`).

## 1. Composition Creation & Properties
```javascript
app.beginUndoGroup("Create Project & Comp");

var project = app.project;
// Width, Height, PixelAspect, Duration (sec), FrameRate
var comp = project.items.addComp("Master_VFX_Comp", 1920, 1080, 1.0, 10.0, 30.0);
comp.openInViewer();
```

## 2. Importing Footage / 3D Render Sequences
```javascript
// Import Image Sequence (e.g. from Blender)
var importOpt = new ImportOptions();
importOpt.file = new File("C:/renders/frame_0001.png");
importOpt.sequence = true;

var footageItem = project.importFile(importOpt);
var footageLayer = comp.layers.add(footageItem);
footageLayer.name = "Blender_3D_Pass";
```

## 3. Adding 3D Camera, Lights & Nulls
```javascript
// Add Camera
var camera = comp.layers.addCamera("CinemaCamera", [comp.width/2, comp.height/2]);
camera.autoOrient = AutoOrientType.NO_AUTO_ORIENT;

// Add 3D Light
var light = comp.layers.addLight("PointLight", [comp.width/2, comp.height/2]);
light.lightType = LightType.POINT;
light.property("Intensity").setValue(120);

// Add 3D Null for Tracking Anchor
var trackerNull = comp.layers.addNull();
trackerNull.name = "3D_Anchor_Null";
trackerNull.threeDLayer = true;
```

## 4. Applying VFX, Adjustments & Glow
```javascript
// Add Adjustment Layer for Color Grading & Glow
var adjLayer = comp.layers.addSolid([1,1,1], "Adjustment_VFX", comp.width, comp.height, 1.0);
adjLayer.adjustmentLayer = true;

// Add Deep Glow / Standard Glow
var glow = adjLayer.property("Effects").addProperty("ADBE Glow");
glow.property("Glow Threshold").setValue(60);
glow.property("Glow Radius").setValue(45);
glow.property("Glow Intensity").setValue(1.5);

// Add Curves / Color Correction
var curves = adjLayer.property("Effects").addProperty("ADBE CurvesCustom");
```

## 5. Adding Motion Graphics Text & Expressions
```javascript
var textLayer = comp.layers.addText("CYBERPUNK TITLE");
var textProp = textLayer.property("Source Text");
var textDoc = textProp.value;
textDoc.fontSize = 80;
textDoc.font = "Arial-BoldMT";
textDoc.fillColor = [1.0, 0.8, 0.2]; // Neon Gold
textProp.setValue(textDoc);

// Make Text 3D and parent to 3D tracker
textLayer.threeDLayer = true;
textLayer.parent = trackerNull;
```

## 6. Automating Render via aerender CLI
```powershell
& "C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\aerender.exe" -project "C:\project.aep" -comp "Master_VFX_Comp" -output "C:\renders\final_video.mov"
```
