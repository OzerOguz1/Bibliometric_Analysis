"""Apply the labour and birth display label to a VOSviewer vector export.

Replaces one vector text outline while preserving counts, coordinates, edges and
clusters. Requires matplotlib, fonttools and lxml. The resulting SVG can be
rendered with an SVG renderer."""
from pathlib import Path
import argparse
from lxml import etree
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Affine2D
from matplotlib.path import Path as MPath
parser=argparse.ArgumentParser()
for name in ['source-svg','source-map','output-svg','output-map']:parser.add_argument('--'+name,required=True)
args=parser.parse_args()
# Relabel one vector glyph path in the original VOSviewer export. All other paths,
# node coordinates, weights, colours and links are preserved byte-for-byte in attributes.
source=Path(args.source_svg)
tree=etree.parse(str(source),etree.XMLParser(huge_tree=True));ns={'s':'http://www.w3.org/2000/svg'}
labels=tree.xpath('//s:g[@fill="#000000"]/s:path',namespaces=ns);hits=[]
for el in labels:
 pen=BoundsPen(None);parse_path(el.attrib['d'],pen)
 if pen.bounds and all(abs(x-y)<.1 for x,y in zip(pen.bounds,(370.203125,699.359375,456.5703125,713.359375))):hits.append((el,pen.bounds))
assert len(hits)==1,len(hits)
el,bb=hits[0];old=el.attrib['d'];fp=FontProperties(family='DejaVu Sans')
ref=TextPath((0,0),'preterm birth',size=14,prop=fp);tp=TextPath((0,0),'labour and birth',size=14,prop=fp)
scale=(bb[3]-bb[1])/ref.get_extents().height
path=tp.transformed(Affine2D().scale(scale,-scale));nb=path.get_extents()
path=path.transformed(Affine2D().translate((bb[0]+bb[2])/2-(nb.x0+nb.x1)/2,(bb[1]+bb[3])/2-(nb.y0+nb.y1)/2))
parts=[]
for v,code in path.iter_segments(curves=True,simplify=False):
 if code==MPath.CLOSEPOLY:parts.append('z');continue
 command={MPath.MOVETO:'M',MPath.LINETO:'L',MPath.CURVE3:'Q',MPath.CURVE4:'C'}[code]
 parts.append(command+' '+' '.join(f'{x:.6f}'.rstrip('0').rstrip('.') for x in v))
el.set('d',' '.join(parts));el.set('aria-label','labour and birth');el.set('data-original-label','preterm birth')
dest=Path(args.output_svg);tree.write(str(dest),encoding='utf-8',xml_declaration=True)
# Source display map makes the one-to-one label alias explicit without altering topology.
pmap=Path(args.source_map)
maptext=pmap.read_text(encoding='utf-8-sig');assert maptext.count('\tpreterm birth\t')==1
Path(args.output_map).write_text(maptext.replace('\tpreterm birth\t','\tlabour and birth\t'))

# Flatten redundant Java SVG groups for portable SVG renderers.
import copy
p=dest;tree=etree.parse(str(p),etree.XMLParser(huge_tree=True));root=tree.getroot();ns='http://www.w3.org/2000/svg'
flat=etree.Element('{'+ns+'}svg',nsmap=root.nsmap,attrib=dict(root.attrib));defs=etree.SubElement(flat,'{'+ns+'}defs')
for el in tree.xpath('//s:linearGradient',namespaces={'s':ns}):defs.append(copy.deepcopy(el))
for stop in defs.iter('{'+ns+'}stop'):
 if 'opacity-stop' in stop.attrib:stop.set('stop-opacity',stop.attrib.pop('opacity-stop'))
props=['stroke-dashoffset','stroke-linejoin','stroke-dasharray','stroke-width','stroke-linecap','stroke-miterlimit','stroke-opacity','stroke','fill','fill-rule','fill-opacity','clip-rule','display','visibility']
count=0;maxtrans=0
for el in tree.iter():
 if not isinstance(el.tag,str) or etree.QName(el).localname not in ['path','image']:continue
 ancestors=list(reversed(list(el.iterancestors())))
 if any(etree.QName(x).localname=='defs' for x in ancestors if isinstance(x.tag,str)):continue
 attrs={};trans=[]
 for x in ancestors+[el]:
  for prop in props:
   if prop in x.attrib:attrs[prop]=x.attrib[prop]
  if x.get('transform'):trans.append(x.get('transform'))
 maxtrans=max(maxtrans,len(trans));new=copy.deepcopy(el)
 for k,v in attrs.items():new.set(k,v)
 if trans:new.set('transform',' '.join(trans))
 flat.append(new);count+=1
out=p;etree.ElementTree(flat).write(str(out),encoding='utf-8',xml_declaration=True)
print('Display vector saved:',out,'; visual elements:',count)
