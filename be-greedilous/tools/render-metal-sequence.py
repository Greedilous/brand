"""Physically lit image frames of the verified assembly; run with Blender.
--preview renders opening / both joints / final. No part rotations, morphs or scaling.
"""
import bpy,math,json,sys,time,shutil
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"creative/interlocking-triangle-20261018-v2/verified-assembly.blend"
OUT=ROOT/"creative/metal-closeup-20261018/renders"
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
prefs=bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type="METAL";prefs.get_devices()
for device in prefs.devices:device.use=device.type=="METAL"
scene.render.engine="CYCLES";scene.cycles.device="GPU"
scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.035
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGBA"
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
scene.render.use_persistent_data=True
parts=[bpy.data.objects[n] for n in ["A • primary module","B • slot 0 mate","C • slot 1 mate"]]
bases=[o.matrix_local.copy() for o in parts]
data=json.loads((ROOT/"assets/assembly-20261018/module.json").read_text())
for M,flat in zip(bases,data["matrices"]):
 assert max(abs(M[r][c]-flat[r*4+c]) for r in range(4) for c in range(4))<.0001
axes=[Vector(v) for v in data["axes"]]
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def metal(name,hexcolor,rough,metallic):
 mat=bpy.data.materials.new(name);mat.use_nodes=True
 nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=tuple(linear(int(hexcolor[i:i+2],16)/255) for i in (0,2,4))+(1,)
 p.inputs["Metallic"].default_value=metallic;p.inputs["Roughness"].default_value=rough
 p.inputs["Coat Weight"].default_value=.3;p.inputs["Coat Roughness"].default_value=.2
 p.inputs["Anisotropic"].default_value=.45
 tex=nodes.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=2.0;tex.inputs["Detail"].default_value=2
 coord=nodes.new("ShaderNodeTexCoord");mapping=nodes.new("ShaderNodeVectorMath");mapping.operation="MULTIPLY"
 mapping.inputs[1].default_value=(2,360,2)
 links.new(coord.outputs["Generated"],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs["Vector"])
 bump=nodes.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.12;bump.inputs["Distance"].default_value=.026
 links.new(tex.outputs["Fac"],bump.inputs["Height"]);links.new(bump.outputs["Normal"],p.inputs["Normal"])
 return mat
materials=[metal("Deep red anodized metal","A81731",.23,.88),metal("Brushed warm silver","D8D2C8",.26,1),metal("Polished silver","D5D8DE",.19,1)]
for o,m in zip(parts,materials):
 o.data.materials.clear();o.data.materials.append(m)
# The ground remains a reflection card but is invisible to the camera.
floor=bpy.data.objects["Studio ground"];floor.visible_camera=False
floor.visible_shadow=False
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(.32,.35,.4,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.35
camera=scene.camera
basis=camera.rotation_euler.to_matrix()
right=basis@Vector((1,0,0));up=basis@Vector((0,1,0));front=basis@Vector((0,0,1))
center=Vector((0,0,75))
def area(name,position,power,width,height,target):
 light=bpy.data.lights.new(name,"AREA");light.energy=power;light.shape="RECTANGLE";light.size=width;light.size_y=height
 obj=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(obj);obj.location=position
 obj.rotation_euler=(target-obj.location).to_track_quat("-Z","Y").to_euler()
area("Narrow reflection strip",center+right*(-125)+front*150,280000,26,220,center)
area("Long silver edge",center+right*170+front*80+up*60,350000,35,240,center)
# A black card makes the polished-metal reflections legible without changing geometry.
bpy.ops.mesh.primitive_plane_add(size=1,location=center+front*230-right*40)
card=bpy.context.object;card.name="Black reflection card";card.scale=(70,200,1)
card.rotation_euler=(center-card.location).to_track_quat("Z","Y").to_euler()
black=bpy.data.materials.new("Black studio card");black.diffuse_color=(.004,.004,.004,1);black.use_nodes=True
black.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.004,.004,.004,1)
card.data.materials.append(black);card.visible_camera=False;card.visible_shadow=False
def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
COUNT=144

def segment(p,start,end,a,b):
 return a+(b-a)*ease((p-start)/(end-start))
def distance(p,start):
 if p<start+.13:return segment(p,start,start+.13,65,18)
 if p<start+.19:return segment(p,start+.13,start+.19,18,12)
 return segment(p,start+.19,start+.38,12,0)
def close_weight(p,a,b,c,d):return ease((p-a)/(b-a))*(1-ease((p-c)/(d-c)))
# These are the exact blind-end centers from the verified module, not hand-placed camera targets.
h=100*math.sqrt(3)/2
mouth=Vector((-13.75,2*h/3-h*.275,0))
direction=Vector((math.cos(math.radians(-15)),math.sin(math.radians(-15)),0))
end=mouth+direction*15.3
joint_local=[end,Matrix.Rotation(math.radians(120),3,'Z')@end]
frames=[0,43,107,143] if "--preview" in sys.argv else range(COUNT)
started=time.time()
rendered={};timeline=[]
for index in frames:
 progress=index/(COUNT-1)
 offsets=[0,distance(progress,.03),distance(progress,.47)]
 # The validated first insertion must finish before the second can begin.
 assert offsets[1]<.0001 or abs(offsets[2]-65)<.0001
 for obj,M,axis,offset in zip(parts,bases,axes,offsets):
  obj.matrix_local=M.copy();obj.location+=axis*offset
 bpy.context.view_layer.update()
 points=[obj.matrix_world@v.co for obj in parts for v in obj.data.vertices]
 xs=[p.dot(right) for p in points];ys=[p.dot(up) for p in points];zs=[p.dot(front) for p in points]
 wide_focus=right*((min(xs)+max(xs))/2)+up*((min(ys)+max(ys))/2)+front*((min(zs)+max(zs))/2)
 wide_scale=max(max(xs)-min(xs),max(ys)-min(ys))*1.08
 w0=close_weight(progress,.08,.22,.43,.49)
 w1=close_weight(progress,.52,.66,.88,1)
 weight=max(w0,w1);joint_index=0 if w0>=w1 else 1
 # Track the midpoint of the two opposing slot ends during their final insertion.
 joint=parts[0].matrix_world@joint_local[joint_index]
 root_rotation=parts[0].matrix_world.to_3x3()
 joint+=root_rotation@axes[joint_index+1]*(offsets[joint_index+1]/2)
 focus=wide_focus.lerp(joint,weight)
 camera.location=focus+front*500
 camera.data.type="ORTHO";camera.data.ortho_scale=wide_scale+(58-wide_scale)*weight
 scene.render.filepath=str(OUT/f"frame-{index:03d}.png")
 key=tuple(round(v,7) for v in offsets)+tuple(round(v,7) for v in focus)+(round(camera.data.ortho_scale,7),)
 if "--resume" in sys.argv and Path(scene.render.filepath).exists():pass
 elif key in rendered:shutil.copyfile(rendered[key],scene.render.filepath)
 else:bpy.ops.render.render(write_still=True)
 rendered[key]=scene.render.filepath
 timeline.append({"frame":index,"progress":progress,"offsets":offsets,"closeup":weight,"joint":joint_index,"camera_scale":camera.data.ortho_scale})
 print("FRAME_DONE",index,round(time.time()-started,2),flush=True)
(OUT.parent/"render-manifest.json").write_text(json.dumps({"frames":COUNT,"width":1400,"height":1400,"samples":40,"renderer":"Blender Cycles Metal","source":"verified-assembly.blend","geometry":"Same fixed orientations and straight insertion translations as validated module.json","materials":["deep red anodized metal","brushed warm silver","polished silver"],"alpha":True,"macro_span_mm":58,"timeline":timeline},indent=2))
