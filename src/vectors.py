from typing import List
from enum import Enum

import FreeCAD
import DraftVecUtils


class Vector(FreeCAD.Vector):
    def __init__(self, x, y, z, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name
        super().__init__(x, y, z)
    

    def isParallel(self, other:FreeCAD.Vector) -> bool:
        """ Check if two vectors are parallel
        
        Parameters
        ----------
        other : FreeCAD.Vector
            Vector to check if it is parallel
        
        Returns
        -------
        bool
            True if the vectors are parallel
        """
        return self.isParallel(other)


    def isPerpendicular(self, other:FreeCAD.Vector) -> bool:
        """ Check if two vectors are perpendicular
        
        Parameters
        ----------
        other : FreeCAD.Vector
            Vector to check if it is perpendicular
        
        Returns
        -------
        bool
            True if the vectors are perpendicular
        """
        return self.dot(other) == 0


    def isOnBase(self) -> bool:
        """ Check if the vector is a base vector
        
        Returns
        -------
        bool
            True if the vector is a base vector
        """
        return sum([x == 0 for x in [self.x, self.y, self.z]]) == 2


    def getName(self) -> str:
        """ Get the name of the vector """
        return self.name


    def getPositiveName(self) -> str:
        """ Get the positive name of the vector
        
        Returns
        -------
        str
            Positive vector name
        """
        return self.name.replace('-','')


    def getPerpendicular1(self) -> FreeCAD.Vector:
        """ Get the first perpendicular vector
        
        Returns
        -------
        FreeCAD.Vector
            Perpendicular vector
        """
        return getfcvecofname(get_vecname_perpend1(self.name))


    def getPerpendicular2(self) -> FreeCAD.Vector:
        """ Get the second perpendicular vector
        
        Returns
        -------
        FreeCAD.Vector
            Perpendicular vector
        """
        return getfcvecofname(get_vecname_perpend2(self.name))


    def getRotation(self, other:FreeCAD.Vector) -> FreeCAD.Rotation:
        """ Calculate the rotation to v2
        The difference with DraftVecUtils.getRotation is that getRotation doesn't
        work for vectors with 180 degrees.

        Parameters
        ----------
        other : FreeCAD.Vector
            Vector to calculate the rotation

        Returns
        --------
        FreeCAD.Rotation
            Tuple representing a quaternion rotation between v2 and v1
        """

        #normalize vectors
        nv1 = DraftVecUtils.scaleTo(self,1.)
        nv2 = DraftVecUtils.scaleTo(other,1.)

        if DraftVecUtils.equals(nv1,nv2.negative()):
            # we have to flip, but DraftVecUtils.getRotation doesn't get it done
            # for this case
            return FreeCAD.Rotation(Vectors.VX,180)
        else:
            return DraftVecUtils.getRotation(nv1,nv2)



class Vectors(Enum):
    """ vector constants """
    V0 = Vector(0,0,0,'0')
    VX = Vector(1,0,0,'x')
    VY = Vector(0,1,0,'y')
    VZ = Vector(0,0,1,'z')
    VXN = Vector(-1,0,0,'-x')
    VYN = Vector(0,-1,0,'-y')
    VZN = Vector(0,0,-1,'-z')
    # no rotation vector
    V0ROT = FreeCAD.Rotation(VZ,0)


def fc_isperp (fc1, fc2):
    """ Return 1 if fc1 and fc2 are perpendicular, 0 if they are not

    Parameters
    ----------
    fc1 : FreeCAD.Vector
        First vector
    fc2 : FreeCAD.Vector
        Second vector
    
    Returns
    -------
        * True if fc1 and fc2 are perpendicular
        * False if they are not 
    """

    if DraftVecUtils.isNull(fc1) or DraftVecUtils.isNull(fc2):
        # if any of them are null, they are not perpendicular
        return False
    nperp = fc1.dot(fc2)
    if round(nperp,DraftVecUtils.precision()) == 0:
        return True
    return False


def fc_isparal (fc1, fc2):
    """ Return 1 if fc1 and fc2 are parallel (colinear), 0 if they are not

    Parameters
    ----------
    fc1 : FreeCAD.Vector
        First vector
    fc2 : FreeCAD.Vector
        Second vector
    
    Returns
    -------
        * True if fc1 and fc2 are parallel
        * False if they are not 
    """
    return fc1.isParallel(fc2)


def fc_isonbase (fcv):
    """  Just tells if a vector has 2 of the coordinates zero
    so it is on just a base vector
    """

    return sum([x == 0 for x in [fcv.x, fcv.y, fcv.z]]) == 2


def get_positive_name (vecname:str) -> str:
    """
    It just get 'x' when vecname is 'x' or '-x', and the same
    for the others, because some functions receive only positive
    base vector
    
    Parameters
    ----------
    vecname : str
        'x', '-x', 'y', '-y', 'z', '-z'

    Returns
    -------
    str
        Vector name
    """
    vecname = vecname.lower().replace('-','')
    if vecname in ['x', 'y', 'z']:
        return vecname
    raise NameError('Not a valid base vector name')


def get_fclist_4perp2_fcvec(fcvec) -> List[FreeCAD.Vector]:
    """
    Gets a list of 4 FreCAD.Vector perpendicular to one base vector
    fcvec can only be:
    * (1,0,0)
    * (0,1,0)
    * (0,0,1)
    * (-1,0,0)
    * (0,-1,0)
    * (0,0,-1)

    For example:
        ::
        
                from (1,0,0) -> (0,1,0), (0,0,1), (0,-1,0), (0,0,-1)

    Parameters
    ----------
    fcvec : vector
        (1,0,0), (0,1,0), (0,0,1), (-1,0,0), (0,-1,0), (0,0,-1)

    Returns
    -------
    list
        List of FreeCAD.Vector 
    """
    return get_fclist_4perp2_vecname(get_nameofbasevec(fcvec))


def get_fclist_4perp2_vecname (vecname:str) -> List[FreeCAD.Vector]:
    """ 
    Gets a list of 4 FreCAD.Vector perpendicular to one vecname
    different from get_fclist_4perp_vecname
    For example:
    ::
        
        from 'x' -> (0,1,1), (0,-1,1), (0,-1,-1), (0,1,-1)

    Parameters
    ----------
    vecname : str
        'x', '-x', 'y', '-y', 'z', '-z'

    Returns
    -------
    list
        List of FreeCAD.Vector
    """

    fc_p1 = getfcvecofname(get_vecname_perpend1(vecname))
    fc_p1_neg = DraftVecUtils.neg(fc_p1)
    fc_p2 = getfcvecofname(get_vecname_perpend2(vecname))
    fc_p2_neg = DraftVecUtils.neg(fc_p2)
    fc_list = [(fc_p1     + fc_p2),
               (fc_p1     + fc_p2_neg),
               (fc_p1_neg + fc_p2_neg),
               (fc_p1_neg + fc_p2)]
    return fc_list


def getvecofname(axis:str) -> tuple:
    """
    Get axis name returns the vector
    """
    axis = axis.lower()
    negative = '-' in axis
    if 'x':
        vec = (1,0,0)
    elif axis == 'y':
        vec = (0,1,0)
    elif axis == 'z':
        vec = (0,0,1)

    return vec if not negative else tuple(-i for i in vec)


def getfcvecofname(axis):
    """
    Returns the FreeCAD.Vector of the vector name given
    """

    fc_vec = FreeCAD.Vector(getvecofname(axis))
    return fc_vec


def vecname_paral (vec1, vec2):
    """
    Given to vectors by name 'x', '-x', ... indicates if they are parallel
    or not

    """
    if vec1.replace('-','') == vec2.replace('-',''):
        return 1
    return 0


def get_vecname_perpend1(vecname):

    """ 
    Gets a perpendicular vecname

    Parameters
    ----------
    vec : str
        'x', '-x', 'y', '-y', 'z', '-z'

    Returns
    --------
    str
        Perpendicular vector name
    """

    if vecname == 'x':
        return 'y'
    elif vecname == 'y':
        return 'z'
    elif vecname == 'z':
        return 'x'
    elif vecname == '-x':
        return '-y'
    elif vecname == '-y':
        return '-z'
    elif vecname == '-z':
        return '-x'


def get_vecname_perpend2(vecname) -> str:

    """ 
    Gets the other perpendicular vecname (see get_vecname_perpend)

    Parameters
    ----------
    vec : str
        'x', '-x', 'y', '-y', 'z', '-z'

    Returns
    -------
    str
        Perpendicular vector name
    """

    if vecname == 'x':
        return 'z'
    elif vecname == 'y':
        return 'x'
    elif vecname == 'z':
        return 'y'
    elif vecname == '-x':
        return '-z'
    elif vecname == '-y':
        return '-x'
    elif vecname == '-z':
        return '-y'


def get_nameofbasevec (fcvec:FreeCAD.Vector) -> str:
    """ 
    From a base vector either:
    (1,0,0), (0,1,0), (0,0,1), (-1,0,0), (0,-1,0), (0,0,-1)
    Gets its name: 'x', 'y',....

    Returns
    -------
    str
        Vector name
    """
    names = {0:'x', 1:'y', 2:'z'}
    if sum(fcvec) != 1 and sum(fcvec) != -1:
        raise ValueError("Not a base vector")
    try:
        return names[[int(i) for i in fcvec].index(1)]
    except:
        return '-'+names[[int(i) for i in fcvec].index(-1)]


def get_fclist_4perp_vecname (vecname:str) -> List[FreeCAD.Vector]:

    """ 
    Gets a list of 4 FreCAD.Vector perpendicular to one vecname
    for example:
    ::
        
        from 'x' -> (0,1,0), (0,0,1), (0,-1,0), (0,0,-1)
    
    Parameters
    ----------
    vecname : str
        'x', '-x', 'y', '-y', 'z', '-z'

    Returns
    -------
    list
        List of FreeCAD.Vector 
    """

    fc_p1 = getfcvecofname(get_vecname_perpend1(vecname))
    fc_p2 = getfcvecofname(get_vecname_perpend2(vecname))
    fc_list = [fc_p1, fc_p2, DraftVecUtils.neg(fc_p1), DraftVecUtils.neg(fc_p2)]
    return fc_list


def get_fclist_4perp_fcvec (fcvec) -> List[FreeCAD.Vector]:
    """ 
    Gets a list of 4 FreeCAD.Vector perpendicular to one base vector
    fcvec can only be:
    * (1,0,0)
    * (0,1,0)
    * (0,0,1)
    * (-1,0,0)
    * (0,-1,0)
    * (0,0,-1)
        
    For example:
        ::
        
             from (1,0,0) -> (0,1,0), (0,0,1), (0,-1,0), (0,0,-1)

    Parameters
    ----------
    fcvec : vector
        (1,0,0), (0,1,0), (0,0,1), (-1,0,0), (0,-1,0), (0,0,-1)

    Returns
    -------
    list
        List of FreeCAD.Vector 
    """
    return get_fclist_4perp_vecname(get_nameofbasevec(fcvec))


def get_rot (v1, v2):
    """ 
    Calculate the rotation from v1 to v2
    the difference with previous versions, such fc_calc_rot, calc_rot, calc_rot
    is that it is for any vector direction.
    The difference with DraftVecUtils.getRotation is that getRotation doesn't
    work for vectors with 180 degrees.

    Notes
    -----
        MAYBE IT IS NOT NECESSARY, just use FreeCAD.Rotation
        rotation.Axis, math.degrees(rotation.Angle)

    Parameters
    ----------
    v1 : FreeCAD.Vector
        Vector to calculate the rotation
    v2 : FreeCAD.Vector
        Vector to calculate the rotation

    Returns
    --------
    FreeCAD.Rotation
        Tuple representing a quaternion rotation between v2 and v1
    """

    #normalize vectors
    nv1 = DraftVecUtils.scaleTo(v1,1.)
    nv2 = DraftVecUtils.scaleTo(v2,1.)

    if DraftVecUtils.equals(nv1,nv2.negative()):
        # we have to flip, but DraftVecUtils.getRotation doesn't get it done
        # for this case
        return FreeCAD.Rotation(Vectors.VX,180)
    else:
        return DraftVecUtils.getRotation(nv1,nv2)


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
