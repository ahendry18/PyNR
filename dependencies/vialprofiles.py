"""
Store vial profiles here

The items in this dictionary may be handed to the Vial class as the vialproperties argument

New entrys may be added, provided that they have a unique name. 
All measurements should be in mm


capdiameter: the diameter of the cap (if this is the same as the vial diameter, this is not required)
crimp: whether it is a crimp cap (True or False)
diameter: the diameter of the vial
height: the total height from the base to the top of the vial (with cap tightened)
screw: whether it is a screw cap (True or False)
piercediameter: the diameter of the pieceable area of the cap (if there is no pieceable area, this is not required)
pitch: the pitch of the threads (tighen cap, measure vial height (H0), unscrew 360deg, measure again (H1); the pitch is H1-H0 in mm)
rotations: the number of rotations required to remove a screw cap (round up if partial)

Copy and paste the following to create a new entry:

'UNIQUEVIALNAME':{
    'capdiameter': None,
    'capheight': None,
    'crimp': True/False,
    'diameter': ###,
    'height': ###,
    'screw': True/False,
    'piercediameter': ###,
    'pitch': ###,
    }

"""

profiles = {
'HPLC1mLpierce':{
    'capdiameter': 11.51,
    'capheight': 5.82, #TODO measure cap height
    'crimp': False,
    'diameter': 11.62,
    'height': 33.41,
    'screw': True,
    'piercediameter': 5.97,
    'pitch': 1.07,
    'rotations': 2,
    }



}