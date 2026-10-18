"""Render the exact supplied symmetric emblem as one rigid metallic identity.
Blender --background --python tools/render-symmetry-sequence.py -- --preview
The movement is a camera/material reveal, not a mechanical slot assembly.
"""
import bpy,math,json,sys,time
from pathlib import Path
from mathutils import Vector,Euler
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"creative/symmetry-proposal-20261018";OUT.mkdir(parents=True,exist_ok=True)
RENDERS=OUT/"renders";RENDERS.mkdir(exist_ok=True)
WEB=ROOT/"proposal-04/assets"
data=json.loads((WEB/"symbol-curves.json").read_text())
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
W,H=data["width"],data["height"];SCALE=160/W
def xy(v):return ((v[0]-W/2)*SCALE,(H/2-v[1])*SCALE,0)
curve=bpy.data.curves.new("Exact symmetric emblem","CURVE");curve.dimensions="2D";curve.fill_mode="BOTH";curve.resolution_u=12;curve.render_resolution_u=16
curve.extrude=1.2;curve.bevel_depth=.3;curve.bevel_resolution=3
for loop in data["loops"]:
 spline=curve.splines.new("BEZIER");spline.bezier_points.add(len(loop)-1);spline.use_cyclic_u=True
 for i,seg in enumerate(loop):
  point=spline.bezier_points[i];point.co=xy(seg[0]);point.handle_left_type="FREE";point.handle_right_type="FREE"
  point.handle_left=xy(loop[i-1][2]);point.handle_right=xy(seg[1])
logo=bpy.data.objects.new("GREEDILOUS • exact symmetric emblem",curve);bpy.context.collection.objects.link(logo)
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mat=bpy.data.materials.new("Polished warm platinum");mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value=tuple(linear(int("D8D1C4"[i:i+2],16)/255) for i in (0,2,4))+(1,)
p.inputs["Metallic"].default_value=1;p.inputs["Roughness"].default_value=.22;p.inputs["Anisotropic"].default_value=0
p.inputs["Coat Weight"].default_value=.25;p.inputs["Coat Roughness"].default_value=.18
coord=nodes.new("ShaderNodeTexCoord");mapping=nodes.new("ShaderNodeVectorMath");mapping.operation="MULTIPLY";mapping.inputs[1].default_value=(2,320,2)
tex=nodes.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=2;tex.inputs["Detail"].default_value=2
links.new(coord.outputs["Generated"],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs["Vector"])
bump=nodes.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.1;bump.inputs["Distance"].default_value=.018
links.new(tex.outputs["Fac"],bump.inputs["Height"]);links.new(bump.outputs["Normal"],p.inputs["Normal"]);curve.materials.append(mat)
scene=bpy.context.scene
prefs=bpy.context.preferences.addons["cycles"].preferences;prefs.compute_device_type="METAL";prefs.get_devices()
for device in prefs.devices:device.use=device.type=="METAL"
scene.render.engine="CYCLES";scene.cycles.device="GPU";scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.035
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGBA";scene.render.use_persistent_data=True
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
world=bpy.data.worlds.new("Warm photographic studio");scene.world=world;world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.36,.33,.29,1);world.node_tree.nodes["Background"].inputs[1].default_value=.5
camera_data=bpy.data.cameras.new("Camera");camera=bpy.data.objects.new("Camera",camera_data);bpy.context.collection.objects.link(camera);scene.camera=camera
camera.rotation_euler=(0,0,0);camera.data.type="ORTHO"
def area(name,position,power,width,height,target=(0,0,0),color=(1,1,1)):
 light=bpy.data.lights.new(name,"AREA");light.energy=power;light.shape="RECTANGLE";light.size=width;light.size_y=height;light.color=color
 obj=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(obj);obj.location=position;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
area("Broad softbox",(-120,110,200),650000,180,220)
area("Left silver strip",(-160,-50,120),400000,26,200)
area("Right bright strip",(160,20,150),480000,24,220)
area("Red edge reflection",(10,-130,100),120000,130,80,color=(1,.12,.18))
# A black reflection card gives silver its distinct bright/dark contrast.
bpy.ops.mesh.primitive_plane_add(size=1,location=(30,0,220));card=bpy.context.object;card.name="Black studio card";card.scale=(65,190,1);card.rotation_euler=(math.pi,0,0)
black=bpy.data.materials.new("Black card");black.use_nodes=True;black.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.004,.004,.004,1)
card.data.materials.append(black);card.visible_camera=False;card.visible_shadow=False
def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def weight(p,a,b,c,d):return ease((p-a)/(b-a))*(1-ease((p-c)/(d-c)))
targets=[Vector(xy((W*.28,H*.28))),Vector(xy((W*.5,H*.5)))]
COUNT=144
frames=[0,43,107,143] if "--preview" in sys.argv else range(COUNT)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"symmetric-symbol.blend"))
started=time.time();timeline=[]
for index in frames:
 progress=index/(COUNT-1)
 # All contours keep the same positions relative to each other throughout the sequence.
 settle=ease((progress-.88)/.12)
 rx=(-13+18*math.sin(progress*math.pi))*(1-settle)
 ry=(18-32*ease(progress))*(1-settle)
 rz=(-7+12*ease(progress))*(1-settle)
 logo.rotation_euler=Euler(tuple(math.radians(v) for v in (rx,ry,rz)),"XYZ")
 bpy.context.view_layer.update()
 w0=weight(progress,.08,.22,.43,.49);w1=weight(progress,.52,.66,.88,1);w=max(w0,w1);detail=0 if w0>=w1 else 1
 focus=(logo.matrix_world@targets[detail])*w
 camera.location=focus+Vector((0,0,500));camera.data.ortho_scale=205+(64-205)*w
 scene.render.filepath=str(RENDERS/f"frame-{index:03d}.png")
 bpy.ops.render.render(write_still=True)
 timeline.append({"frame":index,"progress":progress,"closeup":w,"detail":detail,"rotation_degrees":[rx,ry,rz],"camera_scale":camera.data.ortho_scale})
 print("FRAME_DONE",index,round(time.time()-started,2),flush=True)
(OUT/"render-manifest.json").write_text(json.dumps({"frames":COUNT,"width":1400,"height":1400,"renderer":"Blender Cycles Metal","samples":40,"source":"Exact traced user-provided symmetric emblem","closedContours":data["closedContours"],"width_mm":160,"alpha":True,"motion":"Rigid rotation and camera detail reveal; no contour deformation or simulated joint assembly","timeline":timeline},indent=2))
