"""Proposal 02: exact slotted ellipse, verified perpendicular insertions and Cycles frames.
Blender --background --python tools/render-oval-sequence.py -- --preview
Use --render-all after the preview; validation is retained with a geometry fingerprint.
Dimensions are design study values in mm, not a manufactured prototype.
"""
import bpy,bmesh,math,json,sys,time,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"creative/oval-proposal-20261018";OUT.mkdir(parents=True,exist_ok=True)
ASSETS=ROOT/"proposal-02/assets";ASSETS.mkdir(parents=True,exist_ok=True)
RENDERS=OUT/"renders";RENDERS.mkdir(exist_ok=True)
A,B,W,D,T,GAP,TRAVEL=50.,21.65,4.5,10.5,4.2,.08,50.
COUNT=144
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
alpha=math.asin(W/(2*B));beta=math.acos(W/(2*A))
outline=[]
def arc(start,end):
 for i in range(49):
  angle=start+(end-start)*i/48
  outline.append((A*math.cos(angle),B*math.sin(angle)))
arc(alpha,beta)
outline.extend([(W/2,B-D),(-W/2,B-D)])
arc(math.pi-beta,math.pi-alpha)
outline.extend([(-A+D,W/2),(-A+D,-W/2)])
arc(math.pi+alpha,math.pi+beta)
outline.extend([(-W/2,-B+D),(W/2,-B+D)])
arc(2*math.pi-beta,2*math.pi-alpha)
outline.extend([(A-D,-W/2),(A-D,W/2)])
N=len(outline)
verts=[(x,y,z) for z in [-T/2,T/2] for x,y in outline]
faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
for i in range(N):
 j=(i+1)%N;faces.append((i,j,j+N,i+N))
mesh=bpy.data.meshes.new("Exact four-slot ellipse");mesh.from_pydata(verts,[],faces);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
bases=[Matrix.Identity(4),Matrix.Rotation(math.pi/2,4,"X"),Matrix.Rotation(math.pi/2,4,"Y")]
bases[1].translation=Vector((2*(A-D)+GAP,0,0))
bases[2].translation=Vector((0,2*(B-D)+GAP,0))
axes=[Vector((0,0,0)),Vector((1,0,0)),Vector((0,1,0))]
parts=[]
for name,M in zip(["A • ellipse","B • horizontal connection","C • vertical connection"],bases):
 obj=bpy.data.objects.new(name,mesh.copy());bpy.context.collection.objects.link(obj);obj.matrix_world=M;parts.append(obj)
def positions(offsets):
 for o,M,axis,offset in zip(parts,bases,axes,offsets):
  o.matrix_world=M.copy();o.location+=axis*offset
 bpy.context.view_layer.update()
def volume(a,b):
 obj=bpy.data.objects.new("_intersection",a.data.copy());bpy.context.collection.objects.link(obj);obj.matrix_world=a.matrix_world.copy()
 mod=obj.modifiers.new("Exact intersection","BOOLEAN");mod.operation="INTERSECT";mod.solver="EXACT";mod.object=b
 bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
 bm=bmesh.new();bm.from_mesh(obj.data);v=abs(bm.calc_volume(signed=True));bm.free()
 data=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(data)
 return v
fingerprint=hashlib.sha256(json.dumps([A,B,W,D,T,GAP,TRAVEL,outline]).encode()).hexdigest()
validation_path=ASSETS/"validation.json"
if "--render-all" not in sys.argv or not validation_path.exists():
 control=volume(parts[0],parts[0]);assert control>10000
 bm=bmesh.new();bm.from_mesh(mesh);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free();assert nonmanifold==0
 checks=[]
 for phase in [1,2]:
  for step in range(101):
   shift=TRAVEL-step*.5
   positions([0,shift if phase==1 else 0,TRAVEL if phase==1 else shift])
   for i,j in [(0,1),(0,2),(1,2)]:
    v=volume(parts[i],parts[j]);checks.append(v);assert v<.005,(phase,shift,i,j,v)
  print("VALIDATED_PHASE",phase,flush=True)
 report={"geometry_hash":fingerprint,"method":"Exact Boolean intersections of closed solids at 0.5 mm insertion increments; fixed perpendicular orientations.","dimensions_mm":{"width":2*A,"height":2*B,"thickness":T,"slot_width":W,"slot_depth":D,"end_clearance":GAP},"nonmanifold_edges":nonmanifold,"positive_control_mm3":control,"pair_checks":len(checks),"maximum_intersection_mm3":max(checks),"limitations":"Ideal geometric study, not a fabricated prototype or material/retention certification."}
 validation_path.write_text(json.dumps(report,indent=2))
else:
 assert json.loads(validation_path.read_text())["geometry_hash"]==fingerprint
positions([0,0,0])
# Exact vector master, same vertices and four slots as the 3D plate.
svgpath="M "+" L ".join(f"{x:.5f},{-y:.5f}" for x,y in outline)+" Z"
(ASSETS/"symbol.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-55 -27 110 54"><path fill="#f6f1e9" d="'+svgpath+'"/></svg>')
(ASSETS/"geometry.json").write_text(json.dumps({"dimensions":{"width":2*A,"height":2*B,"thickness":T,"slotWidth":W,"slotDepth":D,"gap":GAP},"matrices":[[float(v) for row in M for v in row] for M in bases],"axes":[list(v) for v in axes],"travel":TRAVEL,"geometry_hash":fingerprint},indent=2))
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def metal(name,hexcolor,rough):
 mat=bpy.data.materials.new(name);mat.use_nodes=True
 nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=tuple(linear(int(hexcolor[i:i+2],16)/255) for i in (0,2,4))+(1,)
 p.inputs["Metallic"].default_value=1;p.inputs["Roughness"].default_value=rough
 p.inputs["Coat Weight"].default_value=.25;p.inputs["Coat Roughness"].default_value=.18;p.inputs["Anisotropic"].default_value=.5
 tex=nodes.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=2;tex.inputs["Detail"].default_value=2
 coord=nodes.new("ShaderNodeTexCoord");mapping=nodes.new("ShaderNodeVectorMath");mapping.operation="MULTIPLY";mapping.inputs[1].default_value=(2,300,2)
 links.new(coord.outputs["Generated"],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs["Vector"])
 bump=nodes.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.13;bump.inputs["Distance"].default_value=.025
 links.new(tex.outputs["Fac"],bump.inputs["Height"]);links.new(bump.outputs["Normal"],p.inputs["Normal"])
 return mat
materials=[metal("Burgundy anodised metal","AC1736",.23),metal("Brushed warm silver","DAD5CA",.25),metal("Polished silver","D5D9DF",.20)]
for o,m in zip(parts,materials):
 o.data.materials.clear();o.data.materials.append(m)
 mod=o.modifiers.new("Precision edge bevel","BEVEL");mod.width=.15;mod.segments=3
 o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
 for poly in o.data.polygons:poly.use_smooth=True
scene=bpy.context.scene
prefs=bpy.context.preferences.addons["cycles"].preferences;prefs.compute_device_type="METAL";prefs.get_devices()
for device in prefs.devices:device.use=device.type=="METAL"
scene.render.engine="CYCLES";scene.cycles.device="GPU";scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.03
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGBA";scene.render.film_transparent=True
scene.render.use_persistent_data=True
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
world=bpy.data.worlds.new("Grey studio");scene.world=world;world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.32,.35,.4,1);world.node_tree.nodes["Background"].inputs[1].default_value=.4
camera_data=bpy.data.cameras.new("Camera");camera=bpy.data.objects.new("Camera",camera_data);bpy.context.collection.objects.link(camera);scene.camera=camera
front=Vector((160,-210,230)).normalized()
camera.rotation_euler=(-front).to_track_quat("-Z","Y").to_euler()
basis=camera.rotation_euler.to_matrix();right=basis@Vector((1,0,0));up=basis@Vector((0,1,0))
center=Vector((30,10,0))
def area(name,position,power,width,height,target):
 light=bpy.data.lights.new(name,"AREA");light.energy=power;light.shape="RECTANGLE";light.size=width;light.size_y=height
 obj=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(obj);obj.location=position;obj.rotation_euler=(target-obj.location).to_track_quat("-Z","Y").to_euler()
area("Large warm softbox",center+front*160+up*180-right*130,700000,190,260,center)
area("Silver edge strip",center+front*160+right*150,450000,30,240,center)
area("Left long strip",center+front*100-right*180,320000,28,210,center)
area("Rim behind",center-front*150+up*180,550000,160,220,center)
# Invisible cards create legible metallic reflections.
for name,pos,size,color in [("Black card",center+front*220-right*35,(65,200,1),(.005,.005,.005,1)),("Cream card",center-front*200,(240,200,1),(.65,.6,.52,1))]:
 bpy.ops.mesh.primitive_plane_add(size=1,location=pos);card=bpy.context.object;card.name=name;card.scale=size
 card.rotation_euler=(center-card.location).to_track_quat("Z","Y").to_euler()
 mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=color
 card.data.materials.append(mat);card.visible_camera=False;card.visible_shadow=False
def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def segment(p,start,end,a,b):return a+(b-a)*ease((p-start)/(end-start))
def distance(p,start):
 if p<start+.13:return segment(p,start,start+.13,TRAVEL,16)
 if p<start+.19:return segment(p,start+.13,start+.19,16,10)
 return segment(p,start+.19,start+.38,10,0)
def weight(p,a,b,c,d):return ease((p-a)/(b-a))*(1-ease((p-c)/(d-c)))
joints=[Vector((A-D+GAP/2,0,0)),Vector((0,B-D+GAP/2,0))]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"verified-oval.blend"))
frames=[0,43,107,143] if "--preview" in sys.argv else range(COUNT)
timeline=[];started=time.time()
for index in frames:
 p=index/(COUNT-1);offsets=[0,distance(p,.03),distance(p,.47)]
 assert offsets[1]<.00001 or abs(offsets[2]-TRAVEL)<.00001
 positions(offsets)
 points=[o.matrix_world@v.co for o in parts for v in o.data.vertices]
 xs=[v.dot(right) for v in points];ys=[v.dot(up) for v in points];zs=[v.dot(front) for v in points]
 wide=right*((min(xs)+max(xs))/2)+up*((min(ys)+max(ys))/2)+front*((min(zs)+max(zs))/2)
 wide_scale=max(max(xs)-min(xs),max(ys)-min(ys))*1.1
 w0=weight(p,.08,.22,.43,.49);w1=weight(p,.52,.66,.88,1);w=max(w0,w1);j=0 if w0>=w1 else 1
 joint=joints[j]+axes[j+1]*offsets[j+1]/2
 focus=wide.lerp(joint,w);camera.location=focus+front*500;camera.data.type="ORTHO";camera.data.ortho_scale=wide_scale+(53-wide_scale)*w
 scene.render.filepath=str(RENDERS/f"frame-{index:03d}.png")
 if not ("--resume" in sys.argv and Path(scene.render.filepath).exists()):bpy.ops.render.render(write_still=True)
 timeline.append({"frame":index,"progress":p,"offsets":offsets,"closeup":w,"joint":j,"camera_scale":camera.data.ortho_scale})
 print("FRAME_DONE",index,round(time.time()-started,1),flush=True)
(OUT/"render-manifest.json").write_text(json.dumps({"frames":COUNT,"width":1400,"height":1400,"samples":40,"renderer":"Blender Cycles Metal","geometry_hash":fingerprint,"alpha":True,"timeline":timeline},indent=2))
