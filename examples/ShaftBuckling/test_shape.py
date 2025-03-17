import os
import sys
import veux
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xara as ops
from shps.shapes import Channel, Rectangle, WideFlange

def _test_opensees(shape, section, center=None):
    model = ops.Model(ndm=3, ndf=6)
    E    = 1 #29000*ksi,
    nu   = -0.5 #.2
    G    = E
    model.material("ElasticIsotropic", 1, E, nu, 0.0)
    model.section("ShearFiber", 1, GJ=0)

    if section == "fiber":
        for fiber in shape.fibers(center=center):
            y, z = fiber.location
            model.fiber(y, z, fiber.area, 1, fiber.warp[0], fiber.warp[1], [0,0,0],  section=1)
#               model.fiber(y, z, fiber.area, mat_tag, section=tag)
    else:
        print("Section = Elastic")
        cnn = shape.torsion.cnn()
        cnm = shape.torsion.cnm()
#       cnw = shape.torsion.cnw()
        cnv = shape.torsion.cnv()
        cmm = shape.torsion.cmm()
        cww = shape.torsion.cww()
        cmv = shape.torsion.cmv()
        cmw = shape.torsion.cmw()
        A = cnn[0,0]
        model.section("ElasticFrame", 1,
                        E=E,
                        G=G,
                        A=A,
                        Ay=1*A,
                        Az=1*A,
                        Qy=cnm[0,1],
                        Qz=cnm[2,0],
                        Iy=cmm[1,1],
                        Iz=cmm[2,2],
#                       Iyz=-cmm[1,2],
                        J =shape.torsion.torsion_constant(),
                        Cw= cww[0,0],
#                       Rw= 0, #cnw[0,0], # this is pretty much always 0.0
                        Ry= cnv[1,0],
                        Rz= cnv[2,0],
                        Sa= cmv[0,0],
                        Sy= cmw[1,0],
                        Sz= cmw[2,0]
        )

    tangent = model.invoke("section", 1, [
                           "update  0 0 0 0 0 0;",
                           "tangent"
            ])

    n = int(np.sqrt(len(tangent)))
    Ks = np.array(tangent).reshape(n,n)
#   plt.spy(Ks)
    plt.imshow(Ks,interpolation='none',cmap='binary')
    plt.show()
    # Ks = np.round(Ks, 4)
    # print(pd.DataFrame(Ks))

    cnn = Ks[:3,:3]
    cmm = Ks[3:6,3:6]
    cnm = Ks[:3,3:6]
    cnw = Ks[:3,6:9]
    cnv = Ks[:3,9:12]
    cmv = Ks[3:6,9:12]
    cww = Ks[6:9,6:9]
    cvv = Ks[9:12,9:12]
    # print(f"{cnm = }")
    # print(f"{cnw = }")
    # print(f"{cnv = }")

    s = ""
    tol=1e-14
    A = cnn[0,0]

    Ay = cnm[0,1] # int z
    Az = cnm[2,0] # int y
    # Compute centroid
    cx, cy = float(Az/A), float(Ay/A)
    cx, cy = map(lambda i: i if abs(i)>tol else 0.0, (cx, cy))


    Ivv = cvv[0,0]
    Irw = cmv[0,0]


    Isv = cmm[0,0] - Ivv

    s += f"""
[nn]  Area                 {A  :>10.4}
[nm]  Centroid             {cx :>10.4},{cy :>10.4}
[mm]  Flexural moments  xx {cmm[0,0] :>10.4}
                        yy {cmm[1,1] :>10.4}
                        zz {cmm[2,2] :>10.4}
                        yz {cmm[1,2] :>10.4}

[mv]                    xx {Irw :>10.4}
[ww]  Warping constant     {cww[0,0] :>10.4}
      Torsion constant     {Isv :>10.4}
[vv]  Bishear           xx {Ivv :>10.4}
    """
    print(s)

if __name__ == "__main__":
    case = "s0002" if len(sys.argv) < 2 else sys.argv[1]

    # shaft-
    benchmarks = dict(
        # B&P, 
        e0010 = dict(
            section=Rectangle(
                d  = 10,
                b  = .5
            ),
            center="centroid"
        ),
        # L&H, Example 1; W21x93
        e0011 = dict(
            section=WideFlange(
                tf = 0.93,
                tw = 0.58,
                d  = 21.62,
                b  = 8.42,
                # saint_venant="linear"
            ),
            center="centroid"
        ),
        # G, S & W, 6.2
        e0012 = dict(
            section=Channel(
                tf =  1.6,
                tw =  1.0,
                b  = 10.0,
                d  = 30.0
            ),
            center = (0,0),
            offset = {
                "A": ( - 3.571, 0),
                "B": (0, 0),
                "C": (2.449, 0),
                "D": (0, 15),
                "E": ( - 5.571, 0),
            }
        ),
        # G, S & W, 6.2
        e0013 = dict(
            section=Channel(
                tf =  1.6,
                tw =  1.0,
                b  = 10.0,
                d  = 30.0
            ),
            center = (0,0),
        ),
        e0014 = dict(
            section=Channel(
        # G, S & W, 6.1
                tf =  0.2,
                tw =  0.2,
                b  = 10.0,
                d  = 10.0
            ),
            center = "centroid"
        ),
        # Plastic hinging, W?x94
        e0030 = dict(
            section=WideFlange(
                tf = 0.93,
                tw = 0.58,
                d  = 21.62,
                b  = 8.42,
                # saint_venant="linear"
            ),
            center="centroid"
        ),
    )

    # 
    # Pilkey ?
#   t =  1.0
#   w = t
#   b = 8.50
#   h = 19.0

#   t =  12.7
#   w = t
#   b = 74.0
#   h = 305.0

    # Lacarbonara, Example 6.4
#   t = 10.5
#   w = 7.5
#   d = 160
#   b = 65
#   o = "centroid"


    shape = benchmarks[case]["section"].create_shape()
    d = benchmarks[case]["section"].d

    offset = os.environ.get("Offset", None)
    if "offset" in benchmarks[case] and offset is not None:
        c = benchmarks[case]["offset"][offset]
    else:
        c = benchmarks[case]["center"]


#   section = section.translate(section.torsion.centroid()).translate([-18.4, 0])
#   print(section.summary())

    if c == "shear-center":
        shape = shape.translate(section.torsion.shear_center())

    elif c == "centroid":
        shape = shape.translate(section.torsion.centroid())

    else:
        shape = shape.translate(c)

    print(shape.summary())

    _test_opensees(shape,
                   section=os.environ.get("Section", "fiber"),
                   center =os.environ.get("Center", None)
    )

    # 1) create basic section
    basic = shape.linearize()

    field = shape.torsion.warping()

    # 3) view warping modes
    artist = veux.create_artist((shape.mesh.nodes, shape.mesh.cells()), ndf=1)

    field = {node: value/100.0 for node, value in enumerate(field)}

    artist.draw_surfaces(field = field, state=field)
    artist.draw_outlines()
    R = artist._plot_rotation

    artist.canvas.plot_vectors([[0,0,0] for i in range(3)], d/5*R.T)
    artist.canvas.plot_vectors([R@[*shape.torsion.shear_center(), 0] for i in range(3)], d/5*R.T)
    artist.draw_outlines()
    veux.serve(artist)

