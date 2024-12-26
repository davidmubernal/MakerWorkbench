import FreeCAD
import Part
import DraftVecUtils

from src.vectors import Vectors
from kcomp import LAYER3D_H

def add_box(x, y, z, name, cx= False, cy=False):
    """ Adds a box, centered on the specified axis x and/or y, with its
    Placement and Rotation at zero. So it can be referenced absolutely from
    its given position

    Parameters
    ----------
    x : float
        Length
    y : float
        Width
    z : float
        Height
    name : str
        Object Name
    cx : Boolean
        Centered in axis x
    cy : Boolean
        Centered in axis y
    Returns
    -------
    FreeCAD.Object
        FreeCAD.Object with the shape of a box
    """
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    box =  doc.addObject("Part::Box",name)
    box.Length = x
    box.Width  = y
    box.Height = z
    xpos = 0
    ypos = 0
    # centered 
    if cx == True:
        xpos = -x/2
    if cy == True:
        ypos = -y/2
    box.Placement.Base =FreeCAD.Vector(xpos,ypos,0)
    return box

# adds a box, centered on the specified axis, with its
# Placement and Rotation at zero. So it can be referenced absolutely from
# its given position

def addBox_cen(x, y, z, name, cx= False, cy=False, cz=False):
    """
    Adds a box, centered on the specified axis, with its
    Placement and Rotation at zero. So it can be referenced absolutely from
    its given position

    Parameters
    ----------
    x : float
        Length
    y : float
        Width
    z : float
        Height
    name : str
        Object Name
    cx : Boolean
        Centered in the X axis
    cy : Boolean
        Centered in the Y axis
    cz : Boolean
        Centered in the Z axis

    Returns
    -------
    FreeCAD.Object
        FreeCAD.Object with the shape of a box
    """
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument

    if cx == True:
        x0 = -x/2.0
        x1 =  x/2.0
    else:
        x0 =  0
        x1 =  x
    if cy == True:
        y0 = -y/2.0
        y1 =  y/2.0
    else:
        y0 =  0
        y1 =  y
    if cz == True:
        z0 = - z/2.0
    else:
        z0 = 0

    p00 = FreeCAD.Vector (x0,y0,z0)
    p10 = FreeCAD.Vector (x1,y0,z0)
    p11 = FreeCAD.Vector (x1,y1,z0)
    p01 = FreeCAD.Vector (x0,y1,z0)
    sq_list = [p00, p10, p11, p01]
    square =  doc.addObject("Part::Polygon",name + "_sq")
    square.Nodes =sq_list
    square.Close = True
    square.ViewObject.Visibility = False
    box = doc.addObject ("Part::Extrusion", name)
    box.Base = square
    box.Dir = (0,0, z)
    box.Solid = True
    # we need to recompute if we want to do operations on this object
    doc.recompute()
    
    return box


# Add cylinder r: radius, h: height 
def addCyl (r, h, name):
    """
    Add cylinder 

    Parameters
    ----------
    r : float
        Radius
    h : float
        Height 

    Returns
    --------
    FreeCAD Object
        Cylinder
    """
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    cyl =  doc.addObject("Part::Cylinder",name)
    cyl.Radius = r
    cyl.Height = h
    return cyl

# Add cylinder in a position. So it is in a certain position, with its
# Placement and Rotation at zero. So it can be referenced absolutely from
# its given position
#     r: radius,
#     h: height 
#     name 
#     axis: 'x', 'y' or 'z'
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
#     h_disp: displacement on the height. 
#             if 0, the base of the cylinder will be on the plane
#             if -h/2: the plane will be cutting h/2
def addCyl_pos (r, h, name, axis = 'z', h_disp = 0):
    """
    Add cylinder in a position. So it is in a certain position, with its
    Placement and Rotation at zero. So it can be referenced absolutely from
    its given position

    Parameters
    ----------
    r : float
        Radius
    h : float
        Height 
    name : str
        Name 
    axis : str
        'x', 'y' or 'z'
            * 'x' will along the x axis
            * 'y' will along the y axis
            * 'z' will be vertical

    h_disp : int
        Displacement on the height. 
            * if 0, the base of the cylinder will be on the plane
            * if -h/2: the plane will be cutting h/2

    Returns
    --------
    FreeCAD Object
        Cylinder
    """
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    cir =  doc.addObject("Part::Circle", name + "_circ")
    cir.Radius = r

    if axis == 'x':
        rot = FreeCAD.Rotation (Vectors.VY, 90)
        cir.Placement.Base = (h_disp, 0, 0)
        extdir = (h,0,0) # direction for the extrusion
    elif axis == 'y':
        rot = FreeCAD.Rotation (Vectors.VX, -90)
        cir.Placement.Base = (0, h_disp, 0)
        extdir = (0,h,0)
    else: # 'z' or any other
        rot = FreeCAD.Rotation (Vectors.VZ, 0)
        cir.Placement.Base = (0, 0, h_disp)
        extdir = (0,0,h)

    cir.Placement.Rotation = rot

    # to hide the circle
    if cir.ViewObject is not None:
      cir.ViewObject.Visibility = False

    cyl = doc.addObject ("Part::Extrusion", name)
    cyl.Base = cir
    cyl.Dir  = extdir
    cyl.Solid  = True

    return cyl



# same as addCyl_pos, but avoiding the creation of many FreeCAD objects
# Add cylinder
#     r: radius,
#     h: height
#     name
#     normal: FreeCAD.Vector pointing to the normal (if its module is not one,
#             the height will be larger than h
#     pos: position of the cylinder

def addCylPos (r, h, name, normal = Vectors.VZ, pos = Vectors.V0):
    """
    Same as addCyl_pos, but avoiding the creation of many FreeCAD objects
    
    Parameters
    ----------
    r : float
        Radius,
    h : float
        Height 
    name : str
        Object name
    normal : FreeCAD.Vector
        FreeCAD.Vector pointing to the normal (if its module is not one,
        the height will be larger than h
    pos : FreeCAD.Vector
        Position of the cylinder

    Returns
    --------
    FreeCAD Object
        Cylinder
    """
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument

    cir =  Part.makeCircle (r,   # Radius
                            pos,     # Position
                            normal)  # direction

    #print "circle: %", cir_out.Curve

    wire_cir = Part.Wire(cir)
    face_cir = Part.Face(wire_cir)

    dir_extrus = DraftVecUtils.scaleTo(normal, h)
    shp_cyl = face_cir.extrude(dir_extrus)

    cyl = doc.addObject("Part::Feature", name)
    cyl.Shape = shp_cyl

    return cyl


# Add cylinder, with inner hole:
#     r_ext: external radius,
#     r_int: internal radius,
#     h: height
#     name
#     axis: 'x', 'y' or 'z'
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
#     h_disp: displacement on the height.
#             if 0, the base of the cylinder will be on the plane
#             if -h/2: the plane will be cutting h/2

def addCylHole (r_ext, r_int, h, name, axis = 'z', h_disp = 0):
    """
    Add cylinder, with inner hole:
    
    Parameters
    ----------
    r_ext : float
        External radius,
    r_int : float
        Internal radius,
    h : float
        Height 
    name : str
        Object name
    axis : str
        'x', 'y' or 'z'
            * 'x' will along the x axis
            * 'y' will along the y axis
            * 'z' will be vertical

    h_disp : int
        Displacement on the height. 
            * if 0, the base of the cylinder will be on the plane
            * if -h/2: the plane will be cutting h/2
    
    Returns
    -------- 
    FreeCAD.Object
        Cylinder with hole
    """
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    cyl_ext =  addCyl (r_ext, h, name + "_ext")
    cyl_int =  addCyl (r_int, h + 2, name + "_int")

    if axis == 'x':
        rot = FreeCAD.Rotation (Vectors.VY, 90)
        cyl_ext.Placement.Base = (h_disp, 0, 0)
        cyl_int.Placement.Base = (h_disp-1, 0, 0)
    elif axis == 'y':
        rot = FreeCAD.Rotation (Vectors.VX, -90)
        cyl_ext.Placement.Base = (0, h_disp, 0)
        cyl_int.Placement.Base = (0, h_disp-1, 0)
    else: # 'z' or any other
        rot = FreeCAD.Rotation (Vectors.VZ, 0)
        cyl_ext.Placement.Base = (0, 0, h_disp)
        cyl_int.Placement.Base = (0, 0, h_disp-1)

    cyl_ext.Placement.Rotation = rot
    cyl_int.Placement.Rotation = rot

    cylHole = doc.addObject("Part::Cut", name)
    cylHole.Base = cyl_ext
    cylHole.Tool = cyl_int

    return cylHole


# same as addCylHole, but avoiding the creation of many FreeCAD objects
# Add cylinder, with inner hole:
#     r_out: outside radius,
#     r_in : inside radius,
#     h: height 
#     name 
#     normal: FreeCAD.Vector pointing to the normal (if its module is not one,
#             the height will be larger than h
#     pos: position of the cylinder

def addCylHolePos (r_out, r_in, h, name, normal = Vectors.VZ, pos = Vectors.V0):
    """
    Same as addCylHole, but avoiding the creation of many FreeCAD objects

    Add cylinder, with inner hole

    Parameters
    ----------
    r_out : float
        Outside radius
    r_in : float
        Inside radius
    h : float
        Height 
    name : str
        Object name
    normal : FreeCAD.Vector
        FreeCAD.Vector pointing to the normal (if its module is not one,
        the height will be larger than h
    pos : FreeCAD.Vector
        Position of the cylinder

    Returns
    -------- 
    Shape
        FreeCAD Shape of a cylinder with hole
    """

    # we have to bring the active document
    doc = FreeCAD.ActiveDocument

    cir_out =  Part.makeCircle (r_out,   # Radius
                                pos,     # Position
                                normal)  # direction
    cir_in =  Part.makeCircle (r_in,   # Radius
                                pos,     # Position
                                normal)  # direction

    #print "in: %", cir_in.Curve
    #print "out: %", cir_out.Curve

    wire_cir_out = Part.Wire(cir_out)
    wire_cir_in  = Part.Wire(cir_in)
    face_cir_out = Part.Face(wire_cir_out)
    face_cir_in  = Part.Face(wire_cir_in)

    face_cir_hole = face_cir_out.cut(face_cir_in)
    dir_extrus = DraftVecUtils.scaleTo(normal, h)
    shp_cyl_hole = face_cir_hole.extrude(dir_extrus)

    cyl_hole = doc.addObject("Part::Feature", name)
    cyl_hole.Shape = shp_cyl_hole

    return cyl_hole


def addBolt (r_shank, l_bolt, r_head, l_head,
             hex_head = 0, extra=1, support=1, headdown = 1, name="bolt"):
    """ 
    Creates the hole for the bolt shank and the head or the nut
    Tolerances have to be included

    Parameters
    ----------
    r_shank : float
        Radius of the shank (tolerance included)
    l_bolt : float
        Total length of the bolt: head & shank
    r_head : float
        Radius of the head (tolerance included)
    l_head : float
        Length of the head
    hex_head : int
        Indicates if the head is hexagonal or rounded      
            * 1: hexagonal
            * 0: rounded

    h_layer3d : float
        Height of the layer for printing, if 0, means that the
        support is not needed
    extra : int
        1 if you want 1 mm on top and bottom to avoid cutting on the same
        plane pieces after making cuts (boolean difference) 
    support : int
        1 if you want to include a triangle between the shank and the
        head to support the shank and not building the head on the
        air using LAYER3D_H
    headdown : int
        * 1 if the head is down. 
        * 0 if it is up


    Returns
    --------
    FreeCAD Object
        FreeCAD Object of a bolt
    """

    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    elements = []
    # shank
    shank =  doc.addObject("Part::Cylinder", name + "_shank")
    shank.Radius = r_shank
    shank.Height = l_bolt + 2*extra
    pos = FreeCAD.Vector(0,0,-extra)
    shank.Placement = FreeCAD.Placement(pos, Vectors.V0ROT, Vectors.V0)
    elements.append (shank)
    # head:
    if hex_head == 0:
        head =  doc.addObject("Part::Cylinder", name + "_head")
        head.Radius = r_head
    else:
        head =  doc.addObject("Part::Prism", name + "_head")
        head.Polygon = 6
        head.Circumradius = r_head

    head.Height = l_head + extra
    if headdown == 1:
        zposhead = -extra
    else:
        zposhead = l_bolt - l_head
    poshead =  FreeCAD.Vector(0,0,zposhead)
    head.Placement.Base = poshead
    elements.append (head)
    # support for the shank:
    if support==1 and LAYER3D_H > 0:
        sup1 = doc.addObject("Part::Prism", name + "_sup1")
        sup1.Polygon = 3
        sup1.Circumradius = r_shank * 2
        # we could put it just on top of the head, but since we are going to 
        # make an union, we put it from the bottom (no need to include extra)
        # sup1.Height = LAYER3D_H
        # pos1 = FreeCAD.Vector(0,0,l_head)
        # rot30z = FreeCAD.Rotation(VZ,30)
        # sup1.Placement = FreeCAD.Placement(pos1, rot30z, Vectors.V0)
        sup1.Height = l_head + LAYER3D_H
        # rotation make only make sense for hexagonal head, but it doesn't
        # matter for rounded head
        rot30z = FreeCAD.Rotation(Vectors.VZ,30)
        if headdown == 1:
            zposheadsup1 = 0
        else:
            zposheadsup1 = l_bolt - l_head - LAYER3D_H
        sup1.Placement.Base = FreeCAD.Vector(0,0,zposheadsup1)
        sup1.Placement.Rotation = rot30z
        # take vertex away:
        if hex_head == 0:
            sup1away = doc.addObject("Part::Cylinder", name + "_sup1away")
            sup1away.Radius = r_head
        else:
            sup1away = doc.addObject("Part::Prism", name + "_sup1away")
            sup1away.Polygon = 6
            sup1away.Circumradius = r_head
        # again, we take all the height
        sup1away.Height =  l_head + LAYER3D_H
        sup1away.Placement.Base = sup1.Placement.Base
        sup1cut = doc.addObject("Part::Common", "sup1cut")
        sup1cut.Base = sup1
        sup1cut.Tool = sup1away
        elements.append (sup1cut)
        # another support
        # 1.15 is the relationship between the Radius and the Apothem
        # of the hexagon: sqrt(3)/2 . I make it slightly smaller
        sup2 = doc.addObject("Part::Prism", name + "_sup2")
        sup2.Polygon = 6
        sup2.Circumradius = r_shank * 1.15
        sup2.Height = l_head + 2* LAYER3D_H
        zposheadsup2 = 0 if headdown == 1 else l_bolt - l_head - 2* LAYER3D_H
        sup2.Placement.Base = FreeCAD.Vector(0,0,zposheadsup2)
        elements.append (sup2)

    # union of elements
    bolt =  doc.addObject("Part::MultiFuse", name)
    bolt.Shapes = elements
    return bolt

    # bolt =  doc.addObject("Part::Fuse", name)
    # bolt.Base = shank
    # bolt.Tool = head


def addBoltNut_hole (r_shank,        l_bolt, 
                     r_head,         l_head,
                     r_nut,          l_nut,
                     hex_head = 0,   extra=1,
                     supp_head=1,    supp_nut=1,
                     headdown=1,     name="bolt"):

    """
    Creates the hole for the bolt shank, the head and the nut.
    The bolt head will be at the bottom, and the nut will be on top
    Tolerances have to be already included in the arguments values

    Parameters
    ----------
    r_shank : float
        Radius of the shank (tolerance included)
    l_bolt : float
        Total length of the bolt: head & shank
    r_head : float
        Radius of the head (tolerance included)
    l_head : float
        Length of the head
    r_nut : float
        Radius of the nut (tolerance included)
    l_nut : float
        Length of the nut. It doesn't have to be the length of the nut
        but how long you want the nut to be inserted
    hex_head : int
        Indicates if the head is hexagonal or rounded         
            * 1: hexagonal
            * 0: rounded

    zpos_nut : float
        Indicates the height position of the nut, the lower part     
    h_layer3d : float
        Height of the layer for printing,
        if 0, means that the support is not needed
    extra : int
        1 if you want 1 mm on top and bottom to avoid cutting on the same
        plane pieces after making differences 
    support : int
        1 if you want to include a triangle between the shank and the
        head to support the shank and not building the head on the air
        using LAYER3D_H
    
    Returns
    --------
    FreeCAD Object
        FreeCAD Object of a Nut Hole
    """
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    elements = []
    bolt = addBolt  (r_shank  = r_shank,
                     l_bolt   = l_bolt,
                     r_head   = r_head,
                     l_head   = l_head,
                     hex_head = hex_head,
                     extra    = extra,
                     support  = supp_head,
                     headdown = headdown,
                     name     = name + "_bolt")

    nut = doc.addObject("Part::Prism", name + "_nut")
    nut.Polygon = 6
    nut.Circumradius = r_nut
    nut.Height = l_nut + extra
    if headdown == 1:
        pos = FreeCAD.Vector (0, 0, l_bolt - l_nut)
    else:
        pos = FreeCAD.Vector (0, 0, -extra)
    nut.Placement = FreeCAD.Placement(pos, Vectors.V0ROT, Vectors.V0)
    elements.append (bolt)
    elements.append (nut)
    # support for the nut
    if supp_nut == 1 and LAYER3D_H > 0:
        supnut1 = doc.addObject("Part::Prism", name + "_nutsup1")
        supnut1.Polygon = 3
        supnut1.Circumradius = r_shank * 2
        supnut1.Height = l_nut + LAYER3D_H
        if headdown == 1:
            pos_supnut1 = FreeCAD.Vector (0, 0,
                                          l_bolt - l_nut - LAYER3D_H)
        else:
            pos_supnut1 = Vectors.V0
        rot30z = FreeCAD.Rotation(Vectors.VZ,30)
        supnut1.Placement = FreeCAD.Placement(pos_supnut1, rot30z, Vectors.V0)
        # take vertex away:
        supnut1away = doc.addObject("Part::Prism", name + "_supnut1away")
        supnut1away.Polygon = 6
        supnut1away.Circumradius = r_nut
        supnut1away.Height =  supnut1.Height
        supnut1away.Placement = FreeCAD.Placement(pos_supnut1, Vectors.V0ROT, Vectors.V0)
        supnut1cut = doc.addObject("Part::Common", "supnut1_cut")
        supnut1cut.Base = supnut1
        supnut1cut.Tool = supnut1away
        elements.append (supnut1cut)
        # the other support
        # 1.15 is the relationship between the Radius and the Apothem
        # of the hexagon: sqrt(3)/2 . I make it slightly smaller
        supnut2 = doc.addObject("Part::Prism", name + "_supnut2")
        supnut2.Polygon = 6
        supnut2.Circumradius = r_shank * 1.15
        supnut2.Height = l_nut + 2* LAYER3D_H
        if headdown == 1:
            pos_supnut2 = FreeCAD.Vector(0,0,
                                         l_bolt - l_nut - 2*LAYER3D_H)
        else:
            pos_supnut2 = Vectors.V0
        supnut2.Placement = FreeCAD.Placement(pos_supnut2, Vectors.V0ROT, Vectors.V0)
        elements.append (supnut2)

    boltnut = doc.addObject("Part::MultiFuse", "boltnut")
    boltnut.Shapes = elements
    return boltnut


def filletchamfer (fco, e_len, name, fillet = 1, radius=1, axis='x', 
                   xpos_chk = 0, ypos_chk = 0, zpos_chk=0,
                   xpos = 0, ypos = 0, zpos = 0,
                    ):
    """
    Fillet or chamfer edges of a certain length, on a certain axis
    and a certain coordinate
    
    Parameters
    ----------
    fco : FreeCAD Object
        Original FreeCAD object we want to fillet or chamfer
    fillet : int
        * 1 if we are doing a fillet
        * 0 if it is a chamfer

    e_len : float
        Length of the edges that we want to fillet or chamfer
        if e_len == 0, chamfer/fillet any length
    radius : float 
        Radius of the fillet or chamfer
    axis : str
        Axis where the fillet will be
    xpos_chk : int
        If the X position will be checked
    ypos_chk : int
        If the Y position will be checked
    zpos_chk : int
        If the Z position will be checked
    xpos : float
        The X position
    ypos : float
        The Y position
    zpos : float
        The Z position
    name : str
        Name of the fco we want to create

    Notes
    -----
    If axis = 'x', x_pos_check will not make sense

    Returns
    --------
    FreeCAD Object
        FreeCAD Object with fillet/chamfer made
    """

    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    doc.recompute()  # you may have problems if you don't do it
    edgelist = []
    #logger.debug('filletchamfer: elen: %s',  e_len)
    for edge_ind, edge in enumerate(fco.Shape.Edges):
        #logger.debug('filletchamfer: edge Length: %s ind %s',
        #             edge.Length, edge_ind)
        # using equ because float number can be not exactly the same
        if (e_len == 0 or equ(edge.Length, e_len)): # same length
            if edge_on_axis (edge, axis) == True:
                #logger.debug('edgeonaxis: Length: %s' % str(edge.Length))
                v0 = edge.Vertexes[0]
                v1 = edge.Vertexes[1]
                if axis == 'x' or axis == '-x':
                    if ypos_chk == True and zpos_chk == True:
                        # its on the axis, so just checking one edge
                        if equ(v0.Y, ypos) and equ(v0.Z, zpos):
                            edgelist.append((edge_ind+1,radius,radius))
                    elif ypos_chk == True:
                        if equ(v0.Y, ypos):
                            edgelist.append((edge_ind +1,radius,radius))
                    elif zpos_chk == True:
                        if equ(v0.Z, zpos):
                            edgelist.append((edge_ind+1,radius,radius))
                    else: # all the edges on axis x with e_len are appended
                        edgelist.append((edge_ind+1,radius,radius))
                elif axis == 'y' or axis == '-y':
                    if xpos_chk == True and zpos_chk == True:
                        if equ(v0.X, xpos) and equ(v0.Z, zpos):
                            edgelist.append((edge_ind+1,radius,radius))
                    elif xpos_chk == True:
                        if equ(v0.X, xpos):
                            edgelist.append((edge_ind+1,radius,radius))
                    elif zpos_chk == True:
                        if equ(v0.Z, zpos):
                            edgelist.append((edge_ind+1,radius,radius))
                    else:
                        edgelist.append((edge_ind+1,radius,radius))
                elif axis == 'z' or axis == '-z':
                    if xpos_chk == True and ypos_chk == True:
                        if equ(v0.X, ypos) and equ(v0.Y, ypos):
                            edgelist.append((edge_ind+1,radius,radius))
                    elif xpos_chk == True:
                        if equ(v0.X, xpos):
                            edgelist.append((edge_ind+1,radius,radius))
                    elif ypos_chk == True:
                        if equ(v0.Y, ypos):
                            edgelist.append((edge_ind+1,radius,radius))
                    else:
                        edgelist.append((edge_ind+1,radius,radius))

    if len(edgelist) != 0:
        if fillet == 1:
            fco_fillcham = doc.addObject ("Part::Fillet", name)
        else:
            fco_fillcham = doc.addObject ("Part::Chamfer", name)
        fco_fillcham.Base = fco
        fco_fillcham.Edges = edgelist
        if fco.ViewObject != None:
            fco.ViewObject.Visibility=False
        doc.recompute()
        return fco_fillcham
    else:
        logger.debug('No edge to fillet or chamfer')
        return

