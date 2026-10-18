"""Trace the supplied wordmark into editable cubic curves without substituting type."""
from pathlib import Path
from PIL import Image,ImageOps,ImageFilter
import json,re,sys,shutil
import vtracer
from svgpathtools import parse_path,CubicBezier,QuadraticBezier,Line,Arc
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"creative/script-proposal-20261018";OUT.mkdir(parents=True,exist_ok=True)
WEB=ROOT/"proposal-03/assets";WEB.mkdir(parents=True,exist_ok=True)
source=Path(sys.argv[1]);shutil.copyfile(source,OUT/"provided-wordmark.png")
im=Image.open(source).convert("L");mask=im.point(lambda p:255 if p>180 else 0)
bbox=mask.getbbox();mask=ImageOps.expand(mask.crop(bbox),border=2,fill=0);native_w,native_h=mask.size
large=ImageOps.expand(im.crop(bbox),border=2,fill=94).resize((native_w*4,native_h*4),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(1.8)).point(lambda p:255 if p>180 else 0)
w,h=large.size
# Black foreground on white is the tracer's native binary input.
ImageOps.invert(large).save(OUT/"trace-input.png")
mask.save(OUT/"reference-mask.png")
vtracer.convert_image_to_svg_py(str(OUT/"trace-input.png"),str(OUT/"trace.svg"),colormode="binary",hierarchical="stacked",mode="spline",filter_speckle=2,corner_threshold=90,length_threshold=8,max_iterations=10,splice_threshold=45,path_precision=4)
svg=ET.parse(OUT/"trace.svg")
loops=[];paths=[]
for el in svg.getroot().iter():
 if not el.tag.endswith("path"):continue
 d=el.attrib["d"];transform=el.attrib.get("transform","")
 match=re.search(r"translate\(([-\d.]+)[ ,]+([-\d.]+)\)",transform)
 dx,dy=map(float,match.groups()) if match else (0.,0.)
 path=parse_path(d)
 for sub in path.continuous_subpaths():
  assert sub.isclosed()
  segments=[]
  for seg in sub:
   if isinstance(seg,Line):
    segments.append(CubicBezier(seg.start,seg.start+(seg.end-seg.start)/3,seg.start+(seg.end-seg.start)*2/3,seg.end))
   elif isinstance(seg,QuadraticBezier):
    segments.append(CubicBezier(seg.start,seg.start+(seg.control-seg.start)*2/3,seg.end+(seg.control-seg.end)*2/3,seg.end))
   elif isinstance(seg,CubicBezier):segments.append(seg)
   elif isinstance(seg,Arc):segments.extend(seg.as_cubic_curves())
   else:raise ValueError(type(seg))
  loops.append([[[z.real+dx,z.imag+dy] for z in [s.start,s.control1,s.control2,s.end]] for s in segments])
 paths.append('<path fill="#f6f1e9" d="'+d+'"'+(' transform="'+transform+'"' if transform else '')+'/>')
(WEB/"wordmark.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+str(w)+' '+str(h)+'">'+''.join(paths)+'</svg>')
geometry={"source":"User-provided paired script wordmark; entire master traced, no font substitution","width":w,"height":h,"sourceCrop":bbox,"sourceWidth":native_w,"sourceHeight":native_h,"closedContours":len(loops),"segments":sum(len(l) for l in loops),"loops":loops}
(WEB/"wordmark-curves.json").write_text(json.dumps(geometry,separators=(",",":")))
print(json.dumps({k:v for k,v in geometry.items() if k!="loops"}))
