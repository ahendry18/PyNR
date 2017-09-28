"""
The series of head modules that may be installed on the end of the NR9's arm

pipette thingy, gripper, dispenser
"""

class Head(object):
    def __init__(self, comms, **kwargs):
        """
        Defines the head of the robot and the components attached to it
        
        **Parameters**
        
        comms: *communicator instance*
            An instance of the communicator class (this communicates with the robot)
        
        
        **\*\*kwargs**
        
        rotary: False
            Whether the head of the robot has rotation enabled
        
        ncounts: 50000
            If rotary is True, how many counts for a full rotation. Options: integer. 
        """
        
        self.kw = {
            'rotary': False, # whether the robot head rotates
            'ncounts': 50000, # how many counts for a full rotation
            }
        
        if set(kwargs.keys()) - set(self.kw.keys()): # check for invalid keyword arguments
            string = ''
            for i in set(kwargs.keys()) - set(self.kw.keys()):
                string += ' %s' %i
            raise KeyError('Unsupported keyword argument(s): %s' %string)
        self.kw.update(kwargs) # update defaults with provided keyword arguments
    
    # ask Allan whether to do R,theta or cartesian for mapping the head attachments

class Gripper(object):
    def __init__(self,**kwargs):
        """
        A gripper atachment 
        
        need to know how big the cap is (diameter, height, altitude)
        also need to know exactly where the cap is relative to the gripper
        The closing value will be given by the triangle between the center of the vial, 
        the edge of the cap, and the height of the gripper origin above the vial cap
        """
        self.kw = {
            'ncounts': 50000, # how many counts for opening and closing
            }
        
        if set(kwargs.keys()) - set(self.kw.keys()): # check for invalid keyword arguments
            string = ''
            for i in set(kwargs.keys()) - set(self.kw.keys()):
                string += ' %s' %i
            raise KeyError('Unsupported keyword argument(s): %s' %string)
        self.kw.update(kwargs) # update defaults with provided keyword arguments
    
    def setgripper(self,value):
        pass
