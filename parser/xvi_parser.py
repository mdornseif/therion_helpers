
# converts XVI Files to PNG
# pip install gizeh lark

from __future__ import unicode_literals

from lark import Lark, Token

# parser = Lark(open('xvi.lark'), parser="earley", debug=True)
parser = Lark(open('therion_helpers/parser/xvi.lark'), parser="lalr", debug=False, propagate_positions=True)
tree = parser.parse(open("topodroid/zip/g25/g25-1p.xvi").read().decode('utf-8'))
print tree.pretty()

allx = []
ally = []
shots = []
sketchlines = []
dimensions = {}
colors = {
    'black': (0,0,0),
    'brown': (0xA5/255.0, 0x2A/255.0, 0x2A/255.0),
    'green': (0,1,0),
    'blue': (0,0,1),
    'red': (1,0,0),
    'orange': (1, 0xA5/255.0, 0),
    'connect': (1, 0, 1),

}

def handle_tree(children):
    for tok in children:
        if tok.data == 'grids':
            pass # tok.children
        elif tok.data == 'shots':
            for child in tok.children:
                frm = get_coords(child.children.pop())
                to = get_coords(child.children.pop())
                shots.append((frm, to))
        elif tok.data == 'stations':
            pass # tok.children
        elif tok.data == 'sketchlines':
            for sketchline in tok.children:
                sketchlines.append((unicode(sketchline.children[0]), [get_coords(p) for p in sketchline.children[1:]]))
        elif tok.data == 'grid':
            for child in tok.children:
                if hasattr(child, 'data') and child.data in ['minx', 'miny', 'gridsize', 'xdim', 'ydim']:
                    dimensions[child.data] = float(child.children.pop())
            dimensions['maxx'] = dimensions['minx'] + (dimensions['gridsize'] * dimensions['xdim'])
            dimensions['maxy'] = dimensions['miny'] + (dimensions['gridsize'] * dimensions['ydim'])
        else:
            print 'unknown', tok


def export_png():
    print dimensions
    import gizeh
    width = int(dimensions['maxx'] - dimensions['minx'])
    height = int(dimensions['maxy'] - dimensions['miny'])
    print width, height
    surface = gizeh.Surface(width=width, height=height) # in pixels
    for shot in shots:
        line = gizeh.polyline(
            points=[fix_coord(shot[0]), fix_coord(shot[1])], 
            stroke_width=2,
            stroke=(0.5,0.5,0.5))
        line.draw(surface)
    for sketchl in sketchlines:
        color = sketchl[0]
        points = sketchl[1]
        line = gizeh.polyline(
            points=[fix_coord(x) for x in points], 
            stroke_width=1,
            stroke=colors[color])
        line.draw(surface)
    # gizeh.rectangle(lx=60.3, ly=45, xy=(60,70), fill=(0,1,0), angle=Pi/8)
    surface.write_to_png("test.png") # export the surface as a PNG


def get_coords(tok):
    x = float(tok.children[0])
    y = float(tok.children[1])
    allx.append(x)
    ally.append(y)
    return (x, y)
    
def fix_coords(coords):
    print "zzz", coords
    return (fix_coord(coords[0]), fix_coord(coords[1]))

def fix_coord(coords):
    return (coords[0]-dimensions['minx'], dimensions['maxy']-coords[1])

handle_tree(tree.children)
export_png()
print min(allx), max(allx)
print min(ally), max(ally)