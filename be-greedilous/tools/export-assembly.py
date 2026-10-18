"""Export the exact slotted module and verify the entire sequential web motion.
Run with Blender --background --python tools/export-assembly.py.
No source images or .blend files are modified.
"""
import bpy, bmesh, math, json
from mathutils import Vector, Matrix
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "assets/assembly-20261018"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
S,W,T,L,GAP,TRAVEL = 100.0,4.9,4.6,15.3,.08,65.0
h=S*math.sqrt(3)/2
top=Vector((0,2*h/3,0));right=Vector((S/2,-h/3,0));left=Vector((-S/2,-h/3,0))
mouth=top.lerp(left,.275)
d=Vector((math.cos(math.radians(-15)),math.sin(math.radians(-15)),0))
e=Vector((-d.y,d.x,0));normal=Vector((0,0,1));edgeNormal=Vector((math.sqrt(3)/2,-.5,0))
end=mouth+d*L
slots=[]
for angle in [0,120,240]:
 R=Matrix.Rotation(math.radians(angle),3,'Z')
 slots.append({'d':R@d,'e':R@e,'c':R@end})
def boundary(p):return p-d*((p-mouth).dot(edgeNormal)/d.dot(edgeNormal))
points=[boundary(mouth-e*W/2),end-e*W/2,end+e*W/2,boundary(mouth+e*W/2)]
outline=[]
for vertex,angle in [(top,240),(right,120),(left,0)]:
 R=Matrix.Rotation(math.radians(angle),3,'Z')
 outline.append(vertex);outline.extend(R@p for p in points)
N=len(outline)
verts=[(p.x,p.y,z) for z in [-T/2,T/2] for p in outline]
faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
for i in range(N):
 j=(i+1)%N;faces.append((i,j,j+N,i+N))
mesh=bpy.data.meshes.new("Slotted triangle")
mesh.from_pydata(verts,[],faces);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bmesh.ops.triangulate(bm,faces=list(bm.faces))
bm.to_mesh(mesh);bm.free()
def attach(port,twist,shift=0):
 a,b=slots[port],slots[0]
 target=Matrix((-a['d'],normal*twist,a['e']*twist)).transposed()
 source=Matrix((b['d'],b['e'],normal)).transposed()
 R=target@source.transposed()
 M=R.to_4x4();M.translation=a['c']-a['d']*(GAP+shift)-R@b['c']
 return M
matrices=[Matrix.Identity(4),attach(0,1),attach(1,-1)]
parts=[]
for i,M in enumerate(matrices):
 o=bpy.data.objects.new(str(i),mesh.copy());bpy.context.collection.objects.link(o);o.matrix_world=M;parts.append(o)
def volume(a,b):
 o=bpy.data.objects.new("_check",a.data.copy());bpy.context.collection.objects.link(o);o.matrix_world=a.matrix_world.copy()
 mod=o.modifiers.new("Intersection","BOOLEAN");mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume(signed=True));bm.free()
 data=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(data)
 return v
control=volume(parts[0],parts[0]);assert control>10000
bm=bmesh.new();bm.from_mesh(mesh);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free();assert nonmanifold==0
checks=[]
# B enters first while C waits 65 mm away. Then C enters with A+B seated.
for phase in [1,2]:
 for step in range(131):
  shift=TRAVEL-step*.5
  parts[1].matrix_world=attach(0,1,shift if phase==1 else 0)
  parts[2].matrix_world=attach(1,-1,TRAVEL if phase==1 else shift)
  bpy.context.view_layer.update()
  for i,j in [(0,1),(0,2),(1,2)]:
   v=volume(parts[i],parts[j]);checks.append(v)
   assert v<.005,(phase,shift,i,j,v)
for o,M in zip(parts,matrices):o.matrix_world=M
bevel=parts[0].modifiers.new("Manufacturing edge bevel","BEVEL");bevel.width=.16;bevel.segments=3
parts[0].modifiers.new("Weighted normals","WEIGHTED_NORMAL")
depsgraph=bpy.context.evaluated_depsgraph_get()
evaluated=parts[0].evaluated_get(depsgraph);outmesh=evaluated.to_mesh();outmesh.calc_loop_triangles()
positions=[];normals=[]
for tri in outmesh.loop_triangles:
 for li in tri.loops:
  loop=outmesh.loops[li]
  positions.extend(round(v,6) for v in outmesh.vertices[loop.vertex_index].co)
  normals.extend(round(v,6) for v in outmesh.corner_normals[li].vector)
evaluated.to_mesh_clear()
data={"positions":positions,"normals":normals,"matrices":[[float(v) for row in M for v in row] for M in matrices],"axes":[[0,0,0],list(-slots[0]['d']),list(-slots[1]['d'])],"travel":TRAVEL,"dimensions":{"side":S,"thickness":T,"slotWidth":W,"slotDepth":L,"endGap":GAP}}
(OUT/"module.json").write_text(json.dumps(data,separators=(',',':')))
report={"method":"Blender EXACT boolean intersections of closed ideal solids; bevel removes material","side_mm":S,"thickness_mm":T,"slot_width_mm":W,"slot_depth_mm":L,"end_clearance_mm":GAP,"travel_mm":TRAVEL,"sample_step_mm":.5,"total_pair_checks":len(checks),"max_intersection_mm3":max(checks),"positive_control_mm3":control,"nonmanifold_edges":nonmanifold,"sequence":"B translates along -slot0 axis with C parked at 65 mm, then C translates along -slot1 axis with B seated. Orientations stay fixed.","limitations":"Ideal geometry and sampled rigid translations. Not a fabricated prototype or a retention/load/material certification."}
(OUT/"validation.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)

