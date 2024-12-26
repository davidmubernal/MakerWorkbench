# ----------------------------------------------------------------------------
# -- FreeCad Functions
# -- comps library
# -- Python functions for FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import os
import math
import sys
import logging

import FreeCAD
import DraftVecUtils

from src.vectors import Vectors
from src.enumerates import COS30
#from FreeCAD import Base

# ---------------------- can be taken away after debugging
# directory this file is
filepath = os.getcwd()
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)
# ---------------------- can be taken away after debugging

from kcomp import D912_HEAD_D, NUT_D934_2A


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



def path_of_module():
    """ Returns the path of the module """
    return os.path.dirname(__file__)

def rotate_view(axis_x = 1.0, axis_y = 0.0, axis_z = 0.0, angle = 45.0):
    """ Rotate the camara """
    from pivy import coin
    try:
        cam = Gui.ActiveDocument.ActiveView.getCameraNode()
        rot = coin.SbRotation()
        rot.setValue(coin.SbVec3f(axis_x,axis_y,axis_z),math.radians(angle))
        nrot = cam.orientation.getValue() * rot
        cam.orientation = nrot
        print(axis_x," ",axis_y," ",axis_z," ",angle)
    except Exception:
        print("Not ActiveView ")



# to compare numbers that they are almost the same, but because of
# floating point calculations they are not exactly the same
def equ (x,y):
    """Compare numbers that are the same but not exactly the same"""

    p = DraftVecUtils.precision()
    return round(x,p) == round(y,p)


def get_fc_perpend1(fcv):
    """ Gets a 'random' perpendicular FreeCAD.Vector

    Parameters
    ----------
    fcv : FreeCAD.Vector
        Vector from which to get perpendicular vector
    
    Returns
    -------
    FreeCAD.Vector
        Random perpendicular vector
    """

    if DraftVecUtils.isNull(fcv):
        logger.error('null vector')

    if fc_isonbase(fcv) == 1: # 2 of the bases are 0
         # just move them
        fcp = FreeCAD.Vector(fcv.z, fcv.x, fcv.y)
    elif fcv.x == 0:
        fcp = FreeCAD.Vector(0, fcv.z, -fcv.y)
    elif fcv.y == 0:
        fcp = FreeCAD.Vector(-fcv.z, 0, fcv.x)
    elif fcv.z == 0:
        fcp = FreeCAD.Vector(fcv.y, -fcv.x, 0)
    else: # none of them are zero (same as before)
        fcp = FreeCAD.Vector(fcv.y, -fcv.x, 0)

    return fcp


def get_tangent_circle_pt (ext_pt,
                           center_pt,
                           rad,
                           axis_n,
                           axis_side = None):
    """ Get the point of the tangent to the circle
    ::

            (difficult to draw in using ASCII text)

               external point
                :     tangent point 1
                *---  _
                \\  /  \\ 
                 \\(     ) circle
            tangent\\ _ /
             point 2
                
        The 3 points: center(C), ext_pt(E) and tangent_pt(T) form a
        rectangle triangle

                        axis_p
                           :    axis_side
                           :      /
                           : <90 /
                           T    /
                        .  *.  /
                   .      90 .  rad
               .               .
           . alpha         beta .
         *-----------------------*   ---- axis_c (axis going thru centers)
        E                  :      C
         :                 :     :
         :.................:     :
         :       +               :
         :   axis_c_ET_d         :
         :                       :
         :.......................:
                     +
              EC_d (hypotenuse)   

    Parameters
    ----------
    ext_pt : FreeCAD.Vector
        External point
    center_pt : FreeCAD.Vector
        Center of the circle
    rad : float
        Radius of the circle
    axis_n : FreeCAD.Vector
        Direction of the normal of the circle
    axis_side : FreeCAD.Vector
        Direction to the side of the tangent point, if not given, it will return both points
        The 2 tangent points will be at each side of axis_c. The smaller than 90 degree angle
        between axis_side and the 2 possible axis_p

    Returns
    -------
        If axis_side is not given:
          returns a list with the 2 points that each point forms a line tangent
          to the circle. The 2 lines are defined by one of each point and the 
          external point.
        If axis_side is given:
          Only returns a point (FreeCAD.Vector) with the tangent point defined
          by the direction of axis_side

        If there is an error it will return 0

    Notes
    -----
    **Interesting Parameters**  

    axis_p (FreeCAD.Vector)

        Vector of the circle plane, perpendicular to axis_d. It can have
        to possible directions. If parameter axis_side is defined, it will
        have the direction that has less than 90 degrees related to axis_side
    """
    # normalize axis_n vector (just in case)
    axis_n = DraftVecUtils.scaleTo(axis_n,1)

    E_pt = ext_pt
    C_pt = center_pt

    # vector from the external point to the center:
    EC = C_pt - E_pt
    # normalized vector:
    axis_c = DraftVecUtils.scaleTo(EC,1)

    if fc_isperp(axis_c, axis_n) == 0:
        logger.error('axis_n is not perpendicular to the line formed by the')
        logger.error('external point and the circle center')
        return 0

    #calculation of axis_p vector, and its negative
    axis_p = axis_n.cross(axis_c)
    axis_pn = axis_p.negative()
    if axis_side is not None:
        axis_side = DraftVecUtils.scaleTo(axis_side, 1)
        if axis_side.dot(axis_p) < 0 :
            # axis_p in the other direction
            axis_p = axis_pn
        axis_pn = Vectors.V0 # not using the negative direction, just one point


    # length (hypotenuse: distance from the circle center to the external point)
    EC_d = EC.Length
    if rad >= EC_d :
        logger.error('The external point has to be out of the circle')
        return 0

    # calculation of the length of the other cathetus (ET)
    ET_d = math.sqrt(EC_d*EC_d - rad*rad)
    # calculation of the sine and cosine of alpha angle
    cos_alpha = ET_d / EC_d
    sin_alpha = rad / EC_d
    # projection distance of the cathetus onto (axis_c: EC):
    axis_c_ET_d = ET_d * cos_alpha
    # projection vector
    axis_c_ET = DraftVecUtils.scale(axis_c, axis_c_ET_d)

    # projection distance of the cathetus onto (axis_p):
    axis_p_ET_d = ET_d * sin_alpha
    # projection vector along axis_p
    axis_p_ET  = DraftVecUtils.scale(axis_p , axis_p_ET_d)

    T_1 = E_pt + axis_c_ET + axis_p_ET
    if axis_pn == Vectors.V0:
        return T_1
    else:
        tg_list = []
        tg_list.append(T_1)
        # projection vector along axis_pn
        axis_pn_ET = DraftVecUtils.scale(axis_pn, axis_p_ET_d)
        T_2 = E_pt + axis_c_ET + axis_pn_ET
        tg_list.append(T_2)
        return tg_list


def get_tangent_2circles (center1_pt,
                          center2_pt,
                          rad1,
                          rad2,
                          axis_n,
                          axis_side = None):
    """ Returns a list of lists (matrix) with the 2 tangent points for each
    of the 2 tangent lines
    ::

        (difficult to draw in using ASCII text)


                        axis_p
                           :
                        T2 :         axis_side
                        .  * r1        /  ------------
                   .         .        /              :
              .         .     .      /               :
      T1  .        .           . r2-r1 (r_diff)      + r2*sin(beta)
         *     .                .                    :
       r1  . alpha          beta                     :
          *----------------------*   ---- axis_c (axis going thru centers)
        C1                 :      C2
         ::                :     :
         ::                :.....:
         ::                  +   :
         ::          r2*cos(beta):
         ::                      :
         ::......................:
         ::          +
         ::   C1_C2_d (hypotenuse)
         ::
         ::
         r1*cos(beta)

          alpha = atan(r_diff/C1_C2_d)
          beta = 90 - alpha

          tangent points along axis_c and axis_p

          T2_c = C2_c - r2 * cos(beta) 
          T2_p = C2_p - r2 * sin(beta) 

          T1_c = C1_c - r1 * cos(beta) 
          T1_p = C1_p - r1 * sin(beta) 

    Parameters
    ----------
    center1_pt : FreeCAD.Vector
        Center of the circle 1
    center2_pt : FreeCAD.Vector
        Center of the circle 2
    rad1 : float
        Radius of the circle 1
    rad2 : float
        Radius of the circle 2
    axis_n : FreeCAD.Vector
        Direction of the normal of the circle
    axis_side : FreeCAD.Vector
        Direction to the side of the tangent line, if not given,
        it will return the 2 points of both lines
        The 2 tangent lines will be at each side of axis_c. The smaller than
        90 degree angle between axis_side and the 2 possible axis_p
    
    Returns
    -------
        * If axis_side is given:  

            - Returns a list of lists (matrix)

                * Element [0][0] is the point tangent to circle 1 at side axis_side
                * Element [0][1] is the point tangent to circle 2 at side axis_side
                * Element [1][0] is the point tangent to circle 1 at opposite side of
                  direction of axis_side
                * Element [1][1] is the point tangent to circle 2 at opposite side of
                  direction of axis_side
        
        * If axis_side is not given, the order of the list of the lines is
          arbitrary
        * If there is an error it will return 0
    
    Notes
    -----
    **Interesting variables**

    axis_p (FreeCAD.Vecrtor)

        Vector of the circle plane, perpendicular to axis_d. It can have
        to possible directions. If parameter axis_side is defined, it will
        have the direction that has less than 90 degrees related to axis_side

    """
    # normalize axis_n vector (just in case)
    axis_n = DraftVecUtils.scaleTo(axis_n,1)

    # choosing r1 the smaller radius, and r2 the larger
    if rad1 < rad2:
        C1_pt = center1_pt
        C2_pt = center2_pt
        r1 = rad1
        r2 = rad2
    else: #changing circle names
        C1_pt = center2_pt
        C2_pt = center1_pt
        r1 = rad2
        r2 = rad1
    r_diff = r2 - r1

    # vector from center1 to center2:
    C1_C2 = C2_pt - C1_pt
    # normalized vector:
    axis_c = DraftVecUtils.scaleTo(C1_C2,1)

    if fc_isperp(axis_c, axis_n) == 0:
        logger.error('axis_n is not perpendicular to the line formed by the')
        logger.error('external point and the circle center')
        return 0

    #calculation of axis_p vector, and its negative
    axis_p = axis_n.cross(axis_c)
    axis_pn = axis_p.negative()
    if axis_side is not None:
        if axis_side.dot(axis_p) < 0 :
            # axis_p in the other direction
            axis_p = axis_pn
            axis_pn = axis_p.negative()
    # if axis_side is not defined, the order is random

    # length (hypotenuse: distance from the circle center to the external point)
    C1_C2_d = C1_C2.Length
    if r_diff >= C1_C2_d :
        logger.error('smaller circle is inside the larger')
        return 0

    # calculation of the length of the other cathetus (T1_T2)
    T1_T2_d = math.sqrt(C1_C2_d * C1_C2_d - r_diff * r_diff)
    # calculation of the sine and cosine of beta angle
    cos_beta =  r_diff / C1_C2_d
    sin_beta = T1_T2_d / C1_C2_d
    # projection distance of the radius onto axis_d
    axis_c_r1_d = r1 * cos_beta
    axis_c_r2_d = r2 * cos_beta
    # projection vector, negative, opposite direction to axis_c
    axis_c_r1 = DraftVecUtils.scale(axis_c, -axis_c_r1_d)
    axis_c_r2 = DraftVecUtils.scale(axis_c, -axis_c_r2_d)

    # projection distance of the radius onto axis_p
    axis_p_r1_d = r1 * sin_beta
    axis_p_r2_d = r2 * sin_beta
    # projection vector, negative, opposite direction to axis_c
    axis_p_r1 = DraftVecUtils.scale(axis_p, axis_p_r1_d)
    axis_p_r2 = DraftVecUtils.scale(axis_p, axis_p_r2_d)
    axis_pn_r1 = DraftVecUtils.scale(axis_pn, axis_p_r1_d)
    axis_pn_r2 = DraftVecUtils.scale(axis_pn, axis_p_r2_d)

    # tangent line on side axis_p
    L1_T1 = C1_pt + axis_c_r1 + axis_p_r1
    L1_T2 = C2_pt + axis_c_r2 + axis_p_r2
    L2_T1 = C1_pt + axis_c_r1 + axis_pn_r1
    L2_T2 = C2_pt + axis_c_r2 + axis_pn_r2
    if rad1 < rad2:
        L1 = [L1_T1, L1_T2]
        L2 = [L2_T1, L2_T2]
    else: # the order was changed
        L1 = [L1_T2, L1_T1]
        L2 = [L2_T2, L2_T1]

    L = [L1, L2]
    return L


def fuseshplist (shp_list):

    """  Since multifuse methods needs to be done by a shape and a list,
    and usually I have a list that I want to fuse, I make this function
    to save the inconvenience of doing every time what I will do here
    Fuse multiFuse
    """

    if len(shp_list) > 0:
        shp1 = shp_list.pop() #remove and get the first element
        if len(shp_list) > 0:
            shpfuse = shp1.multiFuse(shp_list)
        else: #only one element, no fuse:
            logger.debug('only one element to fuse')
            shpfuse = shp1
    else:
        logger.debug('empty list to fuse')
        return

    return shpfuse


def add_fcobj(shp, name:str, doc = None):
    """ Just creates a freeCAD object of the shape, just to save one line"""
    if doc is None:
        doc = FreeCAD.ActiveDocument
    fcobj = doc.addObject("Part::Feature", name)
    fcobj.Shape = shp
    return fcobj


# ------------------- def wire_beltclamp


def regpolygon_vecl (n_sides, radius, x_angle=0):

    """
    Calculates the vertices of a regular polygon. Returns a list of 
    FreeCAD vectors with the vertices. The first vertex will be repeated
    at the end, this is needed to close the wire to make the shape
    The polygon will be on axis XY (z=0). 

    Parameters
    ----------
    n_sides : int
        Number of sides of the polygon
    radius : float
        Circumradius of the polygon
    x_angle : float
        If zero, the first vertex will be on axis x (y=0)
        if x_angle != 0, it will rotated some angle

    Returns
    --------
    List
        List of FreeCAD.Vector of the vertices

    """

    v = FreeCAD.Vector(radius, 0, 0)
    if x_angle != 0:
        # rotate the polygon
        x_angle_rad = math.radians(x_angle)
        # uses radians, rotates around Z axis
        # It seems that the angle of the function is wrong, changing the sign
        v = DraftVecUtils.rotate2D(v,-x_angle_rad)
    vec_vertex_list = [v]
    # divide the 360 degrees by the number of sides
    polygon_angle = 2*math.pi / n_sides
    for i in xrange(n_sides):
        v = DraftVecUtils.rotate2D(v,polygon_angle)
        # the first vertex will be also the last one
        vec_vertex_list.append(v)
    return (vec_vertex_list)


def regpolygon_dir_vecl (n_sides, radius, fc_normal, fc_verx1, pos):

    """
    Similar to regpolygon_vecl but in any place and direction of the space
    calculates the vertices of a regular polygon. Returns a list of 
    FreeCAD vectors with the vertices. The first vertex will be repeated
    at the end, this is needed to close the wire to make the shape
    The polygon will have the center in pos. The normal on fc_normal
    The direction of the first vertex on fc_verx_1

    Parameters
    ----------
    n_sides : int
        Number of sides of the polygon
    radius : float
        Circumradius of the polygon
    fc_normal : FreeCAD.Vector
        Direction of the normal
    fc_verx1 : FreeCAD.Vector
        Direction of the first vertex
    pos : FreeCAD.Vector
        Position of the center

    Returns
    --------
    List
        List of FreeCAD.Vector of the vertices
    """

    # normalize the normal direction
    nnormal = DraftVecUtils.scaleTo(fc_normal,1)

    # check if the vectors are perpendicular
    if not fc_isperp(nnormal, fc_verx1):
        logger.error('Vectors are Not perpendicular')
    #direction of the first vertex scaled to the radius
    n1dir_rad = DraftVecUtils.scaleTo(fc_verx1,radius)

    vertex_list = []
    # divide the 360 degrees by the number of sides
    polygon_angle = 2*math.pi / n_sides
    for i in range(n_sides):
        rot_angle = i*polygon_angle
        # Rotate n1dir, and then add to pos
        vertex = pos + DraftVecUtils.rotate(n1dir_rad,rot_angle,nnormal)
        vertex_list.append(vertex)
    # the first vertex will be also the last one
    vertex_list.append(vertex_list[0])
        
    return (vertex_list)


class NutHole (object):
    """
    Adding a Nut hole (hexagonal) with a prism attached to introduce the nut.
    Tolerances are included
    ::
    
        0               1       
         /\              __
        |  |            |  |
        |  |            |  |
        |__|__ z = 0    |  | -- z = 0
                         \/

    Parameters
    ----------
    nut_r : float
        Circumradius of the hexagon
    nut_h : float
        Height of the nut, usually larger than the actual nut height, to be
        able to introduce it
    hole_h : float
        The hole height, from the center of the hexagon to the side it will
        see light
    name : str
        Name of the object (string)
    extra : int
        * 1 if you want 1 mm out of the hole, to cut

    nuthole_x : int 
        * 1 : if you want that the nut height to be along the X axis
          and the 2*apotheme on the Y axis
          ie. Nut hole facing X
        * 0 : if you want that the nut height to be along the Y axis
          ie. Nut hole facing Y

    cx : int
        * 1 : if you want the coordinates referenced to the x center of the piece
          it can be done because it is a new shape formed from the union

    cy : int
        * 1 : if you want the coordinates referenced to the y center of the piece

    holedown : int
        I THINK IS THE OTHER WAY; CHECK
            * 0: the z0 is the bottom of the square (hole)
            * 1: the z0 is the center of the hexagon (nut)
              it can be done because it is a new shape formed from the union
    
    Returns
    --------
    FreeCAD Object
        FreeCAD object of a nut hole
    """

    def __init__(self, nut_r, nut_h, hole_h, name,
                 extra = 1, nuthole_x = 1, cx=0, cy=0, holedown = 0):
        self.nut_r   = nut_r
        self.nut_h   = nut_h
        self.nut_2ap = 2 * nut_r * COS30    #Apotheme = R * cos (30)
        self.hole_h  = hole_h
        self.name    = name
        self.extra   = extra
        self.nuthole_x = nuthole_x
        self.cx      = cx
        self.cy      = cy
        self.holedown = holedown

        doc = FreeCAD.ActiveDocument
        self.doc     = doc

        # the nut
        nut = doc.addObject("Part::Prism", name + "_nut")
        nut.Polygon = 6
        nut.Circumradius = nut_r
        nut.Height = nut_h
        self.nutObj  = nut

        if nuthole_x == 1:
            x_hole = nut_h
            y_hole = self.nut_2ap
            nutrot = FreeCAD.Rotation(Vectors.VY,90)
            if cx == 1: #centered on X,
                xpos_nut = - nut_h / 2.0
            else:
                xpos_nut = 0
            if cy == 1: #centered on Y, already is
                ypos_nut = 0
            else:
              # already starting on y=0
              ypos_nut = self.nut_2ap/2.0
        else : # nut h is on Y
            x_hole = self.nut_2ap
            y_hole = nut_h
            # the rotation of the nut will be on X
            # this is a rotation of Yaw and Pitch, because we want to have the
            # vertex on top, not the face of the hexagonal prism
            nutrot = FreeCAD.Rotation(90,90,0)
            if cx == 1: #centered on X, already is
                xpos_nut = 0
            else:
                # move to the half of the apotheme
                xpos_nut = self.nut_2ap/2.0
            if cy == 1: #centered on Y, 
                ypos_nut = - nut_h / 2.0
            else:
                # already starting on y=0
                ypos_nut = 0

        hole = add_box (x_hole, y_hole, hole_h + extra, name + "_hole",
                     cx = cx, cy = cy)
        self.holeObj = hole

        if holedown== 1:
            # the nut will be top
            zpos_nut = hole_h
            if extra > 0: # then we will have to bring down the z of the hole
              hole.Placement.Base =   hole.Placement.Base \
                                    + FreeCAD.Vector(0,0,-extra)
        else:
            zpos_nut = 0

        nut.Placement.Base = FreeCAD.Vector (xpos_nut, ypos_nut, zpos_nut)
        nut.Placement.Rotation = nutrot

        nuthole =  doc.addObject("Part::Fuse", name)
        nuthole.Base = nut
        nuthole.Tool = hole
        self.fco = nuthole   # the FreeCad Object


#  ---------------- Fillet on edges of a certain length
#   box:   is the original shape we want to fillet
#   e_len: the length of the edges that we want to fillet
#   radius: the radius of the fillet
#   name: the name of the shape we want to create

def fillet_len (box, e_len, radius, name):
    """
    Make a new object with fillet 

    Parameters
    ----------
    box : TopoShape
        Original shape we want to fillet
    e_len : float
        Length of the edges that we want to fillet
    radius : float
        Radius of the fillet
    name : str
        Name of the shape we want to create

    Returns
    --------
    FreeCAD Object
        FreeCAD Object with fillet made
    """
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    fllts_v = []
    edge_ind = 1
    #logger.debug('fillet_len: box %s - %s' %
    #                     ( str(box), str(box.Shape)))
    for edge_i in box.Shape.Edges:
        #logging.debug('fillet_len: edge Length: %s' % str(edge_i.Length))
        if edge_i.Length == e_len: # same length
        # the index is appended (edge_ind),not the edge itself (edge_i)
        # radius is twice, because it can be variable
            #logging.debug('fillet_len: append edge. Length: %s ' ,
            #               str(edge_i.Length))
            fllts_v.append((edge_ind, radius, radius))
        edge_ind += 1
    box_fllt = doc.addObject ("Part::Fillet", name)
    box_fllt.Base = box
    box_fllt.Edges = fllts_v
    # to hide the objects in freecad gui
    if box.ViewObject != None:
      box.ViewObject.Visibility=False
    return box_fllt

# Calculate Bolt separation
# We want to know how much separation is needed for a bolt
# The bolt (din912) head diameter is usually smaller than the nut (din934)
# The nut max value is give by its 2*apotheme (S) (wrench size)
#     so its max diameter is 2A x cos(30)
#
#     din912  din938
#       D     S(max)   D(max)
# M3:  5.5      5.5     6,35
# M4:  7.0      7.0     8,08
# M5:  8.5      8.0     9,24
# M6: 10.0     10.0    11,55
#
# So it will the nut what gives the separation
#
#         _____    :    _______ 
#        |     |_  :  _|    
#        |       | : |    
#        |       | : |  
#        |      _| : |_ 
#        |_____|   :   |______
#        :     :   :        
#        :..,..:.,.:        
#        : sep  rad:
#        :         :
#        :....,....:
#          bolt_sep 
#
# Arguments:
# bolt_d: diameter of the bolt: 3, 4, ... for M3, M4,... 
# hasnut: 1: if there is a nut
#         0: if there is not a nut, so just the bolt head (smaller)
# sep: separation from the outside of the nut to the end, if empty,
#      default value 2mm

def get_bolt_end_sep (bolt_d, hasnut, sep=2.):
    """
    Calculate Bolt separation

    Calculates know how much separation is needed for a bolt
    The bolt (din912) head diameter is usually smaller than the nut (din934)
    The nut max value is given by its 2*apotheme (S) (wrench size)
    so its max diameter is 2A x cos(30)

    Example of nut and bolt head sizes:

    +--------+--------+--------+--------+
    |        | din912 | din938 |        |
    +========+========+========+========+
    |        |  D     | S(max) | D(max) |
    +--------+--------+--------+--------+
    | **M3** |   5.5  |   5.5  |   6,35 |
    +--------+--------+--------+--------+
    | **M4** |   7.0  |   7.0  |   8,08 |
    +--------+--------+--------+--------+
    | **M5** |   8.5  |   8.0  |   9,24 |
    +--------+--------+--------+--------+
    | **M6** |  10.0  |  10.0  |  11,55 |
    +--------+--------+--------+--------+

    Therefore, if there is a nut, the nut will be used to calculate the
    separation
    ::

          _____    :    _______ 
         |     |_  :  _|    
         |       | : |    
         |       | : |  
         |      _| : |_ 
         |_____|   :   |______
         :     :   :        
         :..,..:.,.:        
         : sep  rad:
         :         :
         :....,....:
           bolt_sep 
 
    Parameters
    ----------
    bolt_d : int
        Diameter of the bolt: 3, 4, ... for M3, M4,... 
    hasnut : int
        * 1: if there is a nut
        * 0: if there is not a nut, so just the bolt head (smaller)

    sep : float
        Separation from the outside of the nut to the end, if empty,
                default value 2mm

    Returns
    --------
    float
        Minimum separation between the center of the bolt and the end

    """

    if hasnut == 1:
        diam = NUT_D934_2A[bolt_d] / COS30
    else: # no nut, calculate with bolt head
        diam = D912_HEAD_D[bolt_d]

    rad  = diam/2.

    bolt_sep = rad + sep

    return bolt_sep

# ------------------- get_bolt_bearing_sep -------------------------
# same as get_bolt_end_sep, but when there is a bearing. 
# If there is a bearing, there will be more space because the nut is at
# the bottom or top, and the widest side is on the middle
#
#                            lbearing_r
#                    rad    ..+...
#                   ..+..  :      :
#         ______    :   :__:______:_
#        |      |_  :  _|      .* : 
#        |        | : |     .*    : this is the bearing section (circumference)
#        |        | : |    (      :
#        |       _| : |_   : *.   :
#        |______|   :   |__:____*_:
#                   :   :  :      :
#                   :   :.bsep    :
#                   :             :
#                   :.bolt_b_sep..:

#
# Arguments:
# bolt_d: diameter of the bolt: 3, 4, ... for M3, M4,... 
# hasnut: 1: if there is a nut
#         0: if there is not a nut, so just the bolt head (smaller)
# lbearing_r: radius of the linear bearing
# bsep: separation from the outside of the nut to the end of bearing
#       default value 0mm

def get_bolt_bearing_sep (bolt_d, hasnut, lbearing_r, bsep=0):
    """
    same as get_bolt_end_sep, but when there is a bearing. 
    If there is a bearing, there will be more space because the nut is at
    the bottom or top, and the widest side is on the middle
    ::

                           lbearing_r
                   rad    ..+...
                  ..+..  :      :
        ______    :   :__:______:_
       |      |_  :  _|      .* : 
       |        | : |     .*    : this is the bearing section (circumference)
       |        | : |    (      :
       |       _| : |_   : *.   :
       |______|   :   |__:____*_:
                  :   :  :      :
                  :   :.bsep    :
                  :             :
                  :.bolt_b_sep..:

    Parameters
    ----------
    bolt_d : int
        Diameter of the bolt: 3, 4, ... for M3, M4,... 
    hasnut : int
        * 1: if there is a nut
        * 0: if there is not a nut, so just the bolt head (smaller)

    lbearing_r : float
        Radius of the linear bearing
    bsep : float
        Separation from the outside of the nut to the end of bearing
        default value 0mm
    
    Returns
    --------
    float
        Minimum separation between the center of the bolt and the bearing
    """

    if hasnut == 1:
        diam = NUT_D934_2A[bolt_d] / COS30
    else: # no nut, calculate with bolt head
        diam = D912_HEAD_D[bolt_d]

    rad  = diam/2.

    bolt_b_sep = rad + bsep + lbearing_r

    return bolt_b_sep



#  ---------------- edgeonaxis
# It tells if an edge is on an axis
# Arguments:
# edge: an FreeCAD edge, with its vertices
# axis: a text, being 'x', '-x', 'y', '-y', 'z', '-z'

def edge_on_axis (edge, axis):
    """
    It tells if an edge is on an axis

    Parameters
    ----------
    edge : Edge
        A FreeCAD edge, with its vertices
    axis : str
        'x', '-x', 'y', '-y', 'z', '-z'
    
    Returns
    -------
    boolean
        True: edge on an axis
        False: edge not on an axis
    """

    vex0 = edge.Vertexes[0]
    vex1 = edge.Vertexes[1]

    if (equ(vex0.X, vex1.X) and 
        equ(vex0.Y, vex1.Y) and
        equ(vex0.Z, vex1.Z)):
        logger.debug('edgeonaxis:  error, same point')
        return False
    elif equ(vex0.X, vex1.X) and equ(vex0.Y, vex1.Y):
        if axis == 'z' or axis == '-z':
            return True
        else:
            return False
    elif equ(vex0.X, vex1.X) and equ(vex0.Z, vex1.Z):
        if axis == 'y' or axis == '-y':
            return True
        else:
            return False
    elif equ(vex0.Y, vex1.Y) and equ(vex0.Z, vex1.Z):
        if axis == 'x' or axis == '-x':
            return True
        else:
            return False
    else:
        return False


def shp_filletchamfer_dir (shp, fc_axis = Vectors.VZ,  fillet = 1, radius=1):
    """
    Fillet or chamfer edges on a certain axis
    
    Parameters
    ----------
    shp : Shape
        Original shape we want to fillet or chamfer
    fillet : int 
        * 1 if we are doing a fillet
        * 0 if it is a chamfer

    radius : float
        The radius of the fillet or chamfer
    fc_axis : FreeCAD.Vector
        Axis where the fillet will be

    Returns
    --------
    Shape
        FreeCAD Shape with fillet/chamfer made
    """

    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    doc.recompute()  # you may have problems if you don't do it
    edgelist = []
    # normalize the axis:
    nnorm = DraftVecUtils.scaleTo(fc_axis,1)
    # get the negative of the normalized vector
    nnorm_neg = nnorm.negative()
    for edge in shp.Edges:
        #logger.debug('filletchamfer: edge Length: %s', edge.Length)
        # get the FreeCAD.Vector with the point
        if len(edge.Vertexes) == 2:
            p0 = edge.Vertexes[0].Point
            p1 = edge.Vertexes[1].Point
            v_vertex = p1.sub(p0)  #subtraction
            # I could calculate the angle, but I think it will take more
            # time than normalizing and checking if they are the same
            v_vertex.normalize()
            # check if they are the same vector (they are parallel):
            if ( DraftVecUtils.equals(v_vertex, nnorm) or
                 DraftVecUtils.equals(v_vertex, nnorm_neg)):
                edgelist.append(edge)
                #logger.debug('append edge Length: %s', edge.Length)
                #logger.debug(str(p0) + ' - ' + str(p1))

    if len(edgelist) == 0:
        logger.debug('No edge to fillet or chamfer')
        return
    if fillet == 1:
        shp_fillcham = shp.makeFillet(radius, edgelist)
    else:
        shp_fillcham = shp.makeChamfer(radius, edgelist)
    doc.recompute()
    return shp_fillcham


def calc_rot (vec1, vec2):
    """
    Having an object with an orientation defined by 2 vectors
    the vectors a tuples, nor FreeCAD.Vectors
    use the wrapper fc_calc_rot to have FreeCAD.Vector arguments
    First vector original direction (x,y,z) is (1,0,0) 
    Second vector original direction (x,y,z) is (0,0,-1) 
    we want to rotate the object in an ortoghonal direction. The vectors
    will be in -90, 180, or 90 degrees.
    this function returns the Rotation given by yaw, pitch and roll
    In case vec1 is (0,0,0), means that it doesn't matter that vector.
    Yaw is the rotation of Z axis. Positive Yaw is like screwing up
    ::

       Y         Y                   Y
       |_X       :   yaw=0           :     yaw=60
       /         :                   :   /
      Z          :                   :  /
                 :                   : /
                 :________....  X    :/............ X
     
     
      Z  Y       Z                   Z
      |/_ X      :   pitch=0         :     pitch=-60
                 :                   :   /
                 :                   :  /
                 :                   : /
                 :________....  X    :/............ X
     
     
                 Z                   Z
       Z         :   roll=0          :     roll=-60
       |_Y       :                   :   /
      /          :                   :  /
     X           :                   : /
                 :________....  Y    :/............ Y
     
    Parameters
    ----------
    vec1 : tuples
        Direction
    vec2 : tuples
        Direction

    Returns
    --------
    FreeCAD.Rotation

    """
           
    # rotation calculation
    if vec1 == (1,0,0):
        yaw = 0
        pitch = 0
        if vec2 == (0,1,0):
            roll  = 90
        elif vec2 == (0,-1,0):
            roll  = -90
        elif vec2 == (0,0,1):
            roll  = 180
        elif vec2 == (0,0,-1):
            roll  = 0
        else:
            print("error 1 in yaw-pitch-roll")
    elif vec1 == (-1,0,0):
        yaw = 180
        pitch = 0
        if vec2 == (0,1,0):
            roll  = -90 #negative because of the yaw
        elif vec2 == (0,-1,0):
            roll  = 90 # positive because of the yaw = 180
        elif vec2 == (0,0,1):
            roll = 180
        elif vec2 == (0,0,-1):
            roll  = 0
        else:
            print("error 2 in yaw-pitch-roll")
    elif vec1 == (0,1,0):
        yaw = 90
        pitch = 0
        if vec2 == (1,0,0):
            roll  = -90
        elif vec2 == (-1,0,0):
            roll  = 90
        elif vec2 == (0,0,1):
            roll  = 180
        elif vec2 == (0,0,-1):
            roll  = 0
        else:
            print("error 3 in yaw-pitch-roll")
    elif vec1 == (0,-1,0):
        yaw = -90
        pitch = 0
        if vec2 == (1,0,0):
            roll  = 90 
        elif vec2 == (-1,0,0):
            roll  = -90 
        elif vec2 == (0,0,1):
            roll  = 180
        elif vec2 == (0,0,-1):
            roll  = 0
        else:
            print("error 4 in yaw-pitch-roll")
    elif vec1 == (0,0,1):
        pitch = -90
        yaw = 0
        if vec2 == (1,0,0):
            roll  = 0 
        elif vec2 == (-1,0,0):
            roll  = 180 
        elif vec2 == (0,1,0):
            roll  = 90
        elif vec2 == (0,-1,0):
            roll  = -90
        else:
            print("error 5 in yaw-pitch-roll")
    elif vec1 == (0,0,-1):
        pitch = 90
        yaw = 0
        if vec2 == (1,0,0):
            roll  = 180 
        elif vec2 == (-1,0,0):
            roll  = 0 
        elif vec2 == (0,1,0):
            roll  = 90
        elif vec2 == (0,-1,0):
            roll  = -90
        else:
            print("error 6 in yaw-pitch-roll")
    elif vec1 == (0,0,0): # it doesn't matter the direction of vec1
        yaw = 0
        if vec2 == (1,0,0):
            pitch = -90
            roll  = 0 
        elif vec2 == (-1,0,0):
            pitch = 90
            roll  = 0 
        elif vec2 == (0,1,0):
            pitch = 0
            roll  = 90
        elif vec2 == (0,-1,0):
            pitch = 0
            roll  = -90
        elif vec2 == (0,0,1):
            pitch = 0
            roll  = 180
        elif vec2 == (0,0,-1):
            pitch = 0
            roll  = 0 # the same position
        else:
            print("error 7 in yaw-pitch-roll")



    vrot = FreeCAD.Rotation(yaw,pitch,roll)
    return vrot


def get_fcvectup (tup):
    """
    Gets the FreeCAD.Vector of a tuple

    Parameters
    ----------
    tup : tuple
        Tuple of 3 elements

    Returns
    -------- 
    FreeCAD.Vector
        FreeCAD.Vector of a tuple
    """

    fcvec = FreeCAD.Vector(tup[0], tup[1], tup[2])
    return (fcvec)


#  ---------------- fc_calc_rot -----------------------------
# same as calc_rot but using FreeCAD.Vectors arguments

def fc_calc_rot (fc_vec1, fc_vec2):
    """
    Same as calc_rot but using FreeCAD.Vectors arguments
    """
    ##vec1 = (fc_vec1.X, fc_vec1.Y, fc_vec1.Z)
    ##vec2 = (fc_vec2.X, fc_vec2.Y, fc_vec2.Z)
    vrot = calc_rot(DraftVecUtils.tup(fc_vec1),DraftVecUtils.tup(fc_vec2))
    return vrot

def calc_rot_z (v_refz, v_refx):
    """
    Calculates de rotation like calc_rot. However uses a different
    origin axis. calc_rot uses:
    vec1 original direction (x,y,z) is (0,0,1) 
    vec2 original direction (x,y,z) is (1,0,0) 
    So it makes a change of axis before calling calc_rot

    Parameters
    ----------
    v_refz : tuple or FreeCAD.Vector
        Vector indicating the rotation from (0,0,1) to v_refz
    v_refx : tuple or FreeCAD.Vector
        Vector indicating the rotation from (1,0,0) to v_refx

    Returns
    --------
    FreeCAD.Rotation 

    """

    if type(v_refz) is tuple:
        v_refz = get_fcvectup(v_refz)
        v_refx = get_fcvectup(v_refx)

    # since arg2 of calc_rot is referenced to VNZ, v_refz is negated
    # so v_refnz becomes referenced to VZ
    v_refnz = DraftVecUtils.neg(v_refz)
    vrot = fc_calc_rot(v_refx, v_refnz)
    return vrot


#  ---------------- calc_desp_ncen ------------------------
#  similar to calc_rot, but calculates de displacement, when we don't want
#  to have all of the dimensions centered
#  First vector original direction (x,y,z) is (1,0,0)
#  Second vector original direction (x,y,z) is (0,0,-1)
#  The arguments vec1, vec2 are tuples (x,y,z) but they may be also
#   FreeCAD.Vectors
#  vec1, vec2 have to be on the axis: x, -x, y, -y, z, -z
#  vec1 can be (0,0,0): it means that it doesn't matter how it is rotated
#  Length: original dimension on X
#  Width:  original dimension on Y
#  Height: original dimension on Z
#
#  the picture is wrong, because originally it is centered, that's
#  why the position is moved only half of the dimension. But the concept
#  is valid
#
#      Z          . Y       length (x) = 1
#      :   _    .           width  (y) = 2
#      : /  /|              height (z) = 3
#      :/_ / |
#      |  |  |              vec1 original (before rotation) = VX
#      |  | /               vec2 original (before rotation) = -VZ
#      |__|/..............X
#
#
#    Example after rotation and change position
#
#      Z         . Y       length (x) = 3
#      :   ____.           width  (y) = 2
#      : /    /|           height (z) = 1
#      :/___ //                  vec1 = VZ
#      |____|/..............X    vec2 = VX
#
#    So we have to move X its original heith (3), otherwise it would
#       be on the negative side, like this
#
#           Z
#           :    . Y       length (x) = 3
#          _:__.           width  (y) = 2
#        /  : /|           height (z) = 1
#       /___://                  vec1 = VZ
#      |____|/..............X    vec2 = VX

def calc_desp_ncen (Length, Width, Height,
                     vec1, vec2, cx=False, cy=False, cz=False, H_extr = False):
    """
    Similar to calc_rot, but calculates de displacement, when we don't want
    to have all of the dimensions centered
    First vector original direction (x,y,z) is (1,0,0)
    Second vector original direction (x,y,z) is (0,0,-1)
    The arguments vec1, vec2 are tuples (x,y,z) but they may be also
    FreeCAD.Vectors
    ::

         Z          . Y       length (x) = 1
     :   _    .           width  (y) = 2
     : /  /|              height (z) = 3
     :/_ / |
     |  |  |              vec1 original (before rotation) = VX
     |  | /               vec2 original (before rotation) = -VZ
     |__|/..............X


     Example after rotation and change position

     Z         . Y       length (x) = 3
     :   ____.           width  (y) = 2
     : /    /|           height (z) = 1
     :/___ //                  vec1 = VZ
     |____|/..............X    vec2 = VX

     So we have to move X its original heith (3), otherwise it would
      be on the negative side, like this

          Z 
          :    . Y       length (x) = 3
         _:__.           width  (y) = 2
       /  : /|           height (z) = 1
      /___://                  vec1 = VZ
     |____|/..............X    vec2 = VX

     the picture is wrong, because originally it is centered, that's
     why the position is moved only half of the dimension. But the concept
     is valid 

    Parameters
    ----------
    vec1 : tuples
        Have to be on the axis: x, -x, y, -y, z, -z
        ::
        
         vec1 can be (0,0,0): it means that it doesn't matter how it is rotated

    vec2 : tuples
        Have to be on the axis: x, -x, y, -y, z, -z
    Length : float
        Original dimension on X
    Width : float
        Original dimension on Y
    Height : float
        Original dimension on Z
    cx : boolean
        Position centered or not
    cy : boolean
        Position centered or not
    cz : boolean
        Position centered or not

    Returns
    --------
    FreeCAD.Vector
        Vector of the displacement
    """
    # rotation calculation
    x = 0
    y = 0
    z = 0
    if abs(vec1[0]) == 1: # X axis: vec1 == (1,0,0) or vec1 == (-1,0,0):
        if abs(vec2[1]) == 1:   # Y
            if cx == False:
                x = Length / 2.0
            if cy == False:
                y = Height / 2.0
            if cz == False:
                z = Width / 2.0
        elif abs(vec2[2]) == 1:    # Z
            if cx == False:
                x = Length / 2.0
            if cy == False:
                y = Width / 2.0
            if cz == False:
                z = Height / 2.0
        else:
            print("error 1 in calc_desp_ncen")
    elif abs(vec1[1]) == 1: # Y axis
        if abs(vec2[0]) == 1:   # X
            if cx == False:
                x = Height / 2.0
            if cy == False:
                y = Length / 2.0
            if cz == False:
                z = Width / 2.0
        elif abs(vec2[2]) == 1:    # Z
            if cx == False:
                x = Width / 2.0
            if cy == False:
                y = Length / 2.0
            if cz == False:
                z = Height / 2.0
        else:
            print("error 2 in calc_desp_ncen")
    elif abs(vec1[2]) == 1: # Z axis
        if abs(vec2[0]) == 1:   # X
            if cx == False:
                x = Height / 2.0
            if cy == False:
                y = Width / 2.0
            if cz == False:
                z = Length / 2.0
        elif abs(vec2[1]) == 1:    # Y
            if cx == False:
                x = Width / 2.0
            if cy == False:
                y = Height / 2.0
            if cz == False:
                z = Length / 2.0
        else:
            print("error 3 in calc_desp_ncen")
    elif (vec1[0]==0 and vec1[1]==0 and vec1[2]==0): 
        #It doesn't matter vec1. Probably it is symmetrical on plane XY.
        # So Length and Width are the same
        if Width != Length:
            logger.error('Check rotation vec1=(0,0,0), and Length!=Width')
        if abs(vec2[0]) == 1:   # X. Pitch = -90. in calc_rot
            if cx == False:
                x = Height / 2.0
            if cy == False:
                y = Width / 2.0
            if cz == False:
                z = Length / 2.0
        elif abs(vec2[1]) == 1:   # Y. Roll = +-90. in calc_rot
            if cx == False:
                x = Length / 2.0
            if cy == False:
                y = Height / 2.0
            if cz == False:
                z = Width / 2.0
        elif abs(vec2[2]) == 1:    # Z. Nothing. Roll 0 or 180
            if cx == False:
                x = Width / 2.0
            if cy == False:
                y = Length / 2.0
            if cz == False:
                z = Height / 2.0
        else:
            print("error 4 in calc_desp_ncen")
    else:
        print("error 5 in calc_desp_ncen")


    vdesp = FreeCAD.Vector(x,y,z)
    return vdesp



#  ---------------- fc_calc_desp_ncen -----------------------------
# same as calc_desp_ncen but using FreeCAD.Vectors arguments

def fc_calc_desp_ncen (Length, Width, Height,
                       fc_vec1, fc_vec2,
                       cx=False, cy=False, cz=False, H_extr = False ):
    """
    Same as calc_desp_ncen but using FreeCAD.Vectors arguments
    """

    vec1 = DraftVecUtils.tup(fc_vec1)
    vec2 = DraftVecUtils.tup(fc_vec2)
    vdesp = calc_desp_ncen(Length, Width, Height,
                           vec1, vec2, cx, cy, cz, H_extr)
    return vdesp
