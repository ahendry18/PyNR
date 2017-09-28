"""
A file for storing robot parameters necessary for operation
"""

params = {
    'sh_el': 170.,  # shoulder to elbow length
    'el_gr': 170.,  # elbow to gripper length
    'sh_cpr': 50500,  # shoulder counts per revolution
    'el_cpr': 25500,  # elbow counts per revolution
    'sh_zero': 16449,  # shoulder zero value (in counts)
    'el_zero': 10370,  # elbow zero value (in counts)
    # 'x_offset': 1.3545997795873177, # x error
    # 'y_offset': 0.11256347689902668, # y error
    'x_offset': 0.,  # x error
    'y_offset': 0.,  # y error
    'halfpoints': {  # half points
        1: 10378,  # elbow
        2: 16452,  # shoulder
        3: 6125,  # z
    },
    'ranges': {  # bounds for axis use (does not account for the negative y regions)
        1: [0, 21050],  # elbow
        2: [0, 33200],  # shoulder
        3: [0, 12250],  # z axis
    },
    'zcountspermm': 120,  # counts per mm for the z axis
    'zbedzero': 17953.6,  # the counts at which the gripper would touch the bed of the robot
}
outputs = {  # outputs
    1: None,
    2: None,
    3: 'gripper',
    4: None,
    5: 'vial_gripper',
    6: None,
    7: None,
}

components = {  # locations for components installed on the N9 bed
    'vial_gripper': {  # vial gripper for uncapping
        'x': -188.36,
        'y': 200.585,
    }
}


class Deck(object):
    def __init__(self, **kwargs):
        """Defines the positioning of screw holes on the deck of the N9 relative to the shoulder"""
        self.kw = {
            'spacing': 37.5,  # spacing in mm
            'array': [21, 17],  # hole array (across, down)
            'zero': [375.,219.],  # zero location (shoulder origin)
            # 'dimensions': [770., 638.],  # dimensions of the deck
            # 'shoulder': [385., 238.],  # location of the shoulder origin
        }
        self.kw.update(kwargs)

        from PyNR.dependencies.general import cellname_to_inds
        self.cti = cellname_to_inds
        self.array = self.generate_array()

    def __getitem__(self, item):
        if type(item) == str:
            x, y = self.cti(item)
            print(x,y)
            return self.array[y][x]
        elif type(item) == tuple:
            return self.array[item[0]][[item[1]]]

    def generate_array(self):
        """generates an appropriately spaced array"""
        # TODO figure out WTF is wrong with this array and why I can't get either the x values or y values to change
        pass
        """
        # x_span = [a*self.kw['spacing']-self.kw['zero'][0] for a in range(self.kw['array'][0])]
        # x_span.reverse()
        # y_span = [b*self.kw['spacing']-self.kw['zero'][1] for b in range(self.kw['array'][1])]
        # y_span.reverse()
        # # a = lambda z: [None for i in range(z)]
        # out = [[None]*self.kw['array'][0]]*self.kw['array'][1]
        # for row, val1 in enumerate(out):
        #     for col, val2 in enumerate(val1):
        #         out[row][col] = {
        #             'x': x_span[row],
        #             'y': y_span[row],
        #         }
        # return out
        
        x, y = self.kw['array']
        import numpy as np
        xlocs = np.linspace(0., (x - 1) * self.kw['spacing'], x)  # create spacing array
        xlocs -= self.kw['zero'][0]  # correct for center of plate
        # xlocs += self.kw['center'][0]  # align to position of plate
        ylocs = np.linspace(0., (y - 1) * self.kw['spacing'], y)
        ylocs -= self.kw['zero'][1]
        # ylocs += self.kw['center'][1]
        xlocs = np.flip(xlocs, 0)
        # ylocs = np.flip(ylocs, 0)
        # basearray = [[None]*self.kw['array'][0]]*self.kw['array'][1]
        a = lambda x: [None for i in range(x)]
        basearray = [a(self.kw['array'][0]) for i in range(self.kw['array'][1])]
        for row, val1 in enumerate(basearray):
            for col, val2 in enumerate(val1):
                basearray[row][col] = {  # define x,y,z location
                    'x': xlocs[col],
                    'y': ylocs[row],
                }
        return basearray
        """
