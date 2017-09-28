"""
The valid set of commands recognized by the North Robotics NR9 robot

New commands may be added to this file in dictionary format, 
with the appropriate command prefix being defined here. 

CMD: four letter command to send to the robot
nargs: number of arguments needed to execute the function
va: whether velocity and acceleration are expected 

Copy, paste, and edit the following to add new commands
'KEY':{
    'CMD':'CMND', 
    'nargs': ###, 
    'va': True/False, 
    },


"""

# perhaps convert everything to 'thing': ['command',#variables expected, errorcheck bool]
 # TODO have a check for nargs etc
commands = {
'echo':{ # echo the robot
    'CMD':'ECHO', 
    'nargs': 0, 
    'va': False, 
    },

'home':{ # home the robot
    'CMD':'HOME', 
    'nargs': 0, 
    'va': False, 
    },

'move':{ # move a single axis
    'CMD':'MOAX',
    'nargs': 4,
    'va': True,
    },

'movesync':{ # syncronous movement of 2 axes
    'CMD':'MOSY', 
    'nargs': 6, 
    'va': True, 
    },
    
'keyboard':{ # enable keyboard driving mode
    'CMD':'KEYB', 
    'nargs': 0, 
    'va': False, 
    },
    
'plustwo':{ # returns the value plus two
    'CMD':'AN02', 
    'nargs': 1, 
    'va': False, 
    },

'output':{ # set the specified output to 1 or 0
    'CMD':'OUTP',
    'nargs': 2,
    'va': False,
    },

'position':{ # returns the position of all axes
    'CMD':'POSR', 
    'nargs': 0, 
    'va': False, 
    },

'servo_on':{ # turns the servos on and sets values to zero (for troubleshooting)
    'CMD':'SEON',
    'nargs': 0,
    'va': False,
    },

'servo_off':{ # turns the servos off (for troubleshooting)
    'CMD':'SEOF',
    'nargs': 0,
    'va': False,
    },

'spin':{ # spins the gripper until toggled off
    'CMD':'MOID',
    'nargs': 4,
    'va': True,
    },

'random': {  # returns a random number
    'CMD': 'AN01',
    'nargs': 0,
    'va': False,
    },

'zero':{ # zeros axes to the current values
    'CMD':'ZERO',
    'nargs': 0,
    'va': False,
    },
}