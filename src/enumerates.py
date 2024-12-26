""" Constants for the whole project """
import FreeCAD

class Colors:
    """ color constants """
    WHITE  = (1.0, 1.0, 1.0)
    BLACK  = (0.0, 0.0, 0.0)

    RED    = (1.0, 0.0, 0.0)
    RED_05    = (1.0, 0.5, 0.5)
    RED_07    = (1.0, 0.7, 0.7)
    RED_D07    = (0.7, 0.0, 0.0)

    GREEN  = (0.0, 1.0, 0.0)
    GREEN_05  = (0.5, 1.0, 0.5)
    GREEN_07  = (0.7, 1.0, 0.7)
    GREEN_D07  = (0.0, 0.7, 0.0)

    BLUE   = (0.0, 0.0, 1.0)
    BLUE_05   = (0.5, 0.5, 1.0)
    BLUE_07   = (0.7, 0.7, 1.0)
    BLUE_D07   = (0.0, 0.0, 0.7)

    YELLOW = (1.0, 1.0, 0.0)
    YELLOW_05 = (1.0, 1.0, 0.5)
    YELLOW_08 = (1.0, 1.0, 0.8)
    YELLOW_095 = (1.0, 1.0, 0.95)

    MAGENT = (1.0, 0.0, 1.0)
    MAGENT_05 = (1.0, 0.5, 1.0)
    MAGENT_08 = (1.0, 0.8, 1.0)

    CIAN   = (0.0, 1.0, 1.0)
    CIAN_05   = (0.5, 1.0, 1.0)
    CIAN_08   = (0.8, 1.0, 1.0)

    ORANGE = (1.0, 0.5, 0.0)
    ORANGE_08 = (1.0, 0.8, 0.0)

    DSKYBLUE   = (0.0, 0.7, 1.0)
    LSKYBLUE   = (0.5, 0.7, 1.0)

    GRAY_08  = (0.8, 0.8, 0.8)
    GRAY_09  = (0.9, 0.9, 0.9)

    @staticmethod
    def custom_color(r,g,b):
        """ Create a custom color """
        return (r/255.0, g/255.0, b/255.0)

EQUAL_TOL = 0.001 # less than a micron is the same


COS30 = 0.86603
COS45 = 0.707
