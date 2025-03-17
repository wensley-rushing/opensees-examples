import xara
from opensees.units.fps import foot, inch
import veux
from shps.shapes import WideFlange, Angle
from veux.utility.alpha_shape import alpha_shape

def create_angle(vertical = 2):

    # shape = WideFlange(d=8*inch, b=6.5*inch, t=0.28*inch)
    shape = WideFlange(d=8*inch, b=6.5*inch, tw=0.5*inch, tf=0.5*inch)

    height = 6*foot
    width =  8*foot

    model = xara.Model(ndm=3, ndf=6)

    model.material("ElasticIsotropic", 1, 29e3, 0.3)

    model.section("ShearFiber", 1)
    for fiber in shape.create_fibers(origin="centroid"):
        model.fiber(**fiber, material=1, section=1)

    if vertical == 2:
        model.node(1, (    0,      0, 0))
        model.node(2, (width,      0, 0))
        model.node(3, (width, height, 0))
        model.node(4, (    0, height, 0))

        model.geomTransf("Linear", 1, (1, 0, 0))
        model.geomTransf("Linear", 2, (0, 1, 0))
        model.geomTransf("Linear", 3, (0, 0, 1))
    else:
        model.node(1, (    0, 0,      0))
        model.node(2, (width, 0,      0))
        model.node(3, (width, 0, height))
        model.node(4, (    0, 0, height))

        model.geomTransf("Linear", 1, (1, 0, 0))
        model.geomTransf("Linear", 2, (0, 0, 1))
        model.geomTransf("Linear", 3, (0,-1, 0))

    model.element("MixedFrame", 2, (2,3), section=1, transform=1) # column
    model.element("MixedFrame", 3, (3,4), section=1, transform=2) # girder
    model.element("MixedFrame", 4, (4,1), section=1, transform=3) # column

    artist = veux.create_artist(model, vertical=vertical)
    artist.draw_origin()
    artist.draw_sections()

    artist.draw_axes(extrude=True)
    artist.save("orient.glb")
    veux.serve(artist, viewer="three-170", port=8080)

if __name__ == "__main__":
    create_angle(vertical=3)