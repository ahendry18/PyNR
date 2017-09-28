"""
a series of functions which take simple commands and converts/sends them to the NR9

- wait for echo
- create custom exceptions (no response, failed execution, target outside of bed range)
- put communication messages in a dictionary
- build in a logger

Also include a set of basic movement/sequences to accomplish a given task (uncap, draw, fill, etc.) 


Look up buffer check
"""


class NoResponse(Exception):
    def __init__(self, command, v=False):
        """an exception for no response from the robot"""
        self.message = 'There was no response from the robot.'  # the error message

        self.command = command  # the command that resulted in the error
        out = self.message
        if v is True:  # if details are requested
            out += '\nIssued command: %s' % command
        super(NoResponse, self).__init__(out)


class FailedExecution(Exception):
    def __init__(self, command, error):
        """an exception to give detailed on a failed exection of a command"""
        self.command = command
        self.error = error
        super(FailedExecution, self).__init__(
            'The command %s failed to execute. \nError message: %s' % (self.command, self.error))


class InvalidCommand(Exception):
    def __init__(self, command):
        super(InvalidCommand, self).__init__("The specified command ('%s') is not recognized." % command)


class Communicator(object):
    def __init__(self, **kwargs):
        self.kw = {  # keyword arguments to adjust the behaviour of the communicator class instance
            'baudrate': 115200,  # used for serial communication
            'comport': 6,  # serial communication port
            'timeout': 1,  # used for serial communication
            'verbose': False,  # used to make the debug output really chatty
            'offline': False,  # bool for offline mode (will not activate any com ports)
            'stepcycle': False,  # whether step-cycle mode is enabled (this requires user input before execution is completed)
            'connectionattempts': 3,  # number of attempts to connect to the robot
            'homeinitialize': True,  # whether to home the robot upon initialization
            'velocity': 10000,  # velocity (counts/s)
            'acceleration': 75000,  # acceleration
            'safeheight': None,  # safe height for operations (height were object collisions will be avoided)
        }

        from PyNR.dependencies.robot_parameters import params, outputs, \
            components  # load robot parameters and update the keywords with them
        self.kw.update(params)

        self.ops = {}  # dictionary of outputs
        for key in outputs:  # map defined outputs to their key
            if outputs[key] is not None:
                self.ops[outputs[key]] = key

        self.comp_locs = components  # locations for installed components

        if set(kwargs.keys()) - set(self.kw.keys()):  # check for and build a list of invalid keyword arguments
            string = ''
            for i in set(kwargs.keys()) - set(self.kw.keys()):
                string += ' %s' % i
            raise KeyError('Unsupported keyword argument(s): %s' % string)
        self.kw.update(kwargs)  # update defaults with provided keyword arguments

        self.math = __import__('math')
        from PyNR.dependencies._commands import commands  # import commands dictionary from _commands.py
        self.commands = commands

        self.t = __import__('time')  # time function for wait commands
        self.va = {'v': self.kw['velocity'],
                   'a': self.kw['acceleration']}  # package the default velocity and acceleration

        self.loc = {}
        if self.kw['offline'] is True:
            print('OFFLINE MODE IS ACTIVE')
        else:
            self.sercon = self.connect(self.kw['connectionattempts'])  # connect to the robot
            if self.kw['homeinitialize'] is True:
                self.home()  # home the robot
        self.in_gripper = None,  # holder for object in the robot's gripper (default empty)
        # self.loc = { # location tracker for the robot
        #     0: 0, # gripper rotation
        #     1: 0, # elbow
        #     2: 0, # shoulder
        #     3: 0, # up/down
        #     # 4: 0, # unassigned
        #     # 5: 0, # unassigned
        #     # 6: 0, # unassigned
        #     }

    def calculate_offset(self, x, y):
        """calculates the offset of the current position from the provided x and y"""
        cur_pos = self.forward_kinematics(self.position())  # calculate current position by forward kinematics
        return {'x': x - cur_pos['x'], 'y': y - cur_pos['y']}

    def chooseangle(self, options):
        """chooses the closest shoulder angle to the current shoulder position"""
        shlist = []
        for dct in options:
            if dct[2] < 0:  # ignore if value less than 0
                continue
            shlist.append(dct[2])
        if len(shlist) == 0:
            raise ValueError('No solution for this point could be determined (both shoulder angles are negative).')
        difflist = [abs(i - self.loc[2]) for i in
                    shlist]  # determine the differences between the shoulder values and the current shoulder value
        ind = difflist.index(min(difflist))  # select the closest
        for dct in options:
            if dct[2] == shlist[ind]:  # if the shoulder value matches the closest one, return
                return dct

    def connect(self, attempts=3):
        """
        attempts to connect to the robot
        
        If you cannot connect to the robot, install the FTDI drivers from 
        http://www.ftdichip.com/Drivers/VCP.htm
        (the easiest way to do this is to use the executables)
        """
        from serial import Serial, SerialException  # import pyserial
        import time
        if self.kw['verbose']:
            print('Connecting to the robot on comport %d' % self.kw['comport'])
        attempt = 1
        while attempt < attempts:
            try:
                return Serial('COM' + str(self.kw['comport']),  # establish the serial connection
                              baudrate=self.kw['baudrate'],
                              timeout=self.kw['timeout'],
                              )
            except SerialException as e:
                attempt += 1
                time.sleep(1)
                if attempt == attempts:
                    print(
                        'A connection could not be established with the robot. Switching to offline mode. Communication error:\n%s' % e)
                    self.kw['offline'] = True

    def disconnect(self, roughhome=True):
        """disconnects from the robot"""
        if roughhome is True:  # roughly home the robot for faster initialization later
            self.roughhome()
        if self.kw['verbose']:
            print('Disconnecting')
        self.sercon.close()

    def execute(self, cmd, *args, validate=False, **kwargs):
        """
        Executes the specified command by communicating it to the robot
        
        Arguments are the sequential arguments to pass the function. 
        If an insufficient number of arguments are passed, an error will be raised. 
        
        Velocity and acceleration are specified upon initiation of the class, 
        but can be passed to this function as keyword arguments 'v' and 'a' respectively. 
        
        """

        # TODO update the errorcheck function to check for <executed_command>
        def errorcheck(written, read):
            """error checks the written string against the read string"""
            if not read.startswith('<') or not read.endswith('>'): # if the command is not packaged properly
                return False
            elif read[1:-1] != written: # if the packaged execution does not match what was written
                return False
            else:
                return True  # successful execution and return

        def pseudorobot(written):
            """pretends to be the robot in offline mode"""
            return written + '>'

        try:
            try:
                cmddct = self.commands[cmd]  # retrieve the command
            except KeyError:
                raise InvalidCommand(cmd)
            if len(args) != cmddct['nargs']:  # if an incorrect number of arguments were provided
                if len(args) >= cmddct['nargs'] - 2 and len(args) < cmddct['nargs'] and cmddct[
                        'va'] is True:  # if velocity and acceleration were skipped
                    args = list(args)
                    largs = len(args)  # check the number of arguments
                    va = dict(self.va) # retrieve instance velocity and acceration
                    va.update(**kwargs) # update the velocity and acceleration
                    # if largs != cmddct['nargs'] - 1:  # if acceleration was provided as an argument
                    args.append(va['a']) # append acceleration
                    args.append(va['v']) # append velocity

                else:
                    raise ValueError(
                        'An incorrect number of variable arguments were passed for the function %s\n'
                        '(expected: %d, passed: %d)'
                        % (cmd, cmddct['nargs'], len(args))
                    )
            strcmd = cmddct['CMD'] # get the four letter command key
            for i, v in enumerate(args):  # package variables
                strcmd += ' V' + str(i + 1) + '[' + str(round(v)) + ']'
            if self.kw['offline'] is True:  # if offline mode is enabled, don't actually execute anything
                if self.kw['verbose'] is True:
                    pseudorobot(strcmd)
                    # print('executing %s with package %s' %(cmd,pkg))
                return None

            if self.kw['verbose']:
                print("Executing command '%s'" % (strcmd))
            self.sercon.write(self.pkg(strcmd))  # execute the string

            output = self.read()  # retrieve the output and error check
            if validate is True: # if return validation is called for
                if errorcheck(strcmd, output) is False:
                    # TODO should the command resend?
                    raise FailedExecution(strcmd,'input does not match pingback: %s' %output)

            if self.kw['stepcycle'] is True:  # if step-cycle mode is enabled
                input('Command %s executed successfully, continue?' % cmd)

            return output

        except KeyboardInterrupt:  # CTRL+C will break out of any execute command
            print('User interrupted exection')
            self.home()  # send robot home
            raise KeyboardInterrupt

    def forward_kinematics(self, dct=None, offset=False, **kwargs):
        """converts a location dictionary to x,y,z coordinates"""
        if dct is None:  # if a location dictionary was provided
            dct = self.loc
        # TODO update this to accept keywords (for backcalculation of locations with different arm lengths)
        sh = (dct[2] - self.kw['sh_zero']) / self.kw['sh_cpr'] * 2 * self.math.pi  # calculate the shoulder angle
        el = (dct[1] - self.kw['el_zero']) / self.kw['el_cpr'] * 2 * self.math.pi * -1
        # print('Shoulder angle (degrees):\t', self.math.degrees(sh))
        # print('Elbow angle (degrees):\t', self.math.degrees(el))
        # TODO figure out why x and y are reversed
        x = self.kw['sh_el'] * self.math.cos(sh) + self.kw['el_gr'] * self.math.cos(sh + el)
        y = self.kw['sh_el'] * self.math.sin(sh) + self.kw['el_gr'] * self.math.sin(sh + el)

        if offset is False: # if uncorrected values are desired
            return {'x': -y, 'y': x}
        else:
            # TODO apply offset to values, (change offset kwarg to True when this is done)
            pass

    def goto(self, *args, **kwargs):
        """
        go to the provided position location

        By default, the execution will prioritize the up/down axis if moving up, and the shoulder/elbow if moving down.

        An order may be forced by providing the 'order' kwarg. Order keys are supplied by the one letter codes:
        'z' for z-axis, 'g' for gripper, 's' for shoulder, and 'e' for elbow.

        Movesync will be used by default, but can be disabled by using 'movesync'=False.
        """
        if len(args) == 1:  # only one argument has been handed
            if type(args[0]) != dict:
                raise ValueError('The goto function must be handed a dictionary.')
            posdct = args[0]
        elif len(args) == 2 and type(args[0]) == int and type(args[1]) == int:  # if handed an axis and a value
            posdct = {args[0]: args[1]}
        else:  # handles multiple dictionaries and will execute them in the sequence provided
            for i in args:
                if type(i) != dict:
                    raise ValueError('Goto arguments may be either a dictionary or a list of dictionaries.')
                self.goto(i)
            return None

        if 'x' in posdct:
            if 'y' not in posdct:
                raise ValueError('If x is provided, y must also be provided.')
            options = self.inverse_kinematics(posdct, **kwargs)  # determine the angle options from inverse kinematics
            posdct.update(self.chooseangle(options))  # choose the closest shoulder angle to current

            if 'z' in posdct:
                pass
                # TODO create a handler for z values (calibrate deck and offset according to x and y position)
                # TODO need to know the exact height of the gripper bottom relative to the deck
        # TODO create a handler for acceleration and velocity
        deltas = {}  # dictionary for determining what axes are changing
        for key in posdct:  # for each provided axis
            if type(key) == int:  # ignore letter axis values
                delta = self.loc[key] - posdct[
                    key]  # determine the difference between the specified count and the current count
                if delta != 0:  # if that is nonzero
                    deltas[key] = self.loc[key] - posdct[key]  # append to deltas dictionary

        # determine axis movement order
        order = []  # order list
        if 'order' in kwargs:  # if an order was specified in the kwargs
            orderdct = {  # letter keys for axes
                'g': 0,
                's': 1,
                'e': 2,
                'z': 3,
            }
            for i in kwargs['order']:  # append the axis indicies in the specified order
                order.append(orderdct[i])
        elif 0 in deltas:  # if a z movement is specified
            if deltas[0] < 0:  # if moving up
                for i in [0, 3, 1, 2]:
                    if i in deltas:
                        order.append(i)
            else:  # if moving down
                for i in [1, 2, 0, 3]:
                    if i in deltas:
                        order.append(i)
        else:  # if no z movement
            for i in [1, 2, 3]:
                if i in deltas:
                    order.append(i)
        # print('order:\t',order)
        # move the robot
        if 'sync' in kwargs and kwargs['sync'] is False:  # if movesync is force disabled
            for i in order:
                self.execute('move', i, posdct[i])  # move the axis to the specified location
        else:  # automatically apply movesync
            while len(order) != 0:
                if len(order) // 2:  # if there are at least two axes to move
                    self.execute('movesync', order[0], order[1], posdct[order[0]],
                                 posdct[order[1]])  # move the next two axes
                    order = order[2:]  # remove the executed axes
                else:  # if only one axis is left to move
                    self.execute('move', order[0], posdct[order[0]])  # move that axis
                    order = order[1:]
        self.loc.update(posdct)  # update the axes locations

    def home(self):
        """homes the robot"""
        if self.kw['verbose']:
            print('Homing the robot')
        self.sercon.write(self.pkg('HOME'))
        self.loc.update({0: 0, 1: 0, 2: 0, 3: 0, })
        return self.read(100)

    def inverse_kinematics(self, x, y=None, z=None, **kwargs):
        """
            converts the provided x y coordinates into joint angles

            The frame of reference for the coordinate system is from the perspective of the shoulder, looking out onto the bed.
            The y axis is towards the far edge of the bed (increasing towards the far edge of the bed from the shoulder),
            and the x axis is perpendicular to this.

            y axis
            ^
            |
            ----------------------------------------
            |                                       |
            |    -+         bed           ++        |
            |                                       |
            |                                       |
            |                                       |
            |             shoulder                  |
            |             ________                  |
            |            |   o    |                 | o: origin
            |    --      |        |       +-        |
            +----------------------------------------------> x-axis

            """
        # allow for modification of function behaviour if keywords were supplied
        if len(kwargs) > 0:  # if keyword arguments were supplied
            execdict = dict(self.kw)
            execdict.update(kwargs)
        else:
            execdict = self.kw
        if type(x) == dict:  # if provided with a position dictionary
            if 'x' not in x or 'y' not in x:
                raise ValueError('Both x and y values must be passed to the inverse kinematics function.')
            x_corr = x['x'] - execdict['x_offset']  # set and correct y
            y_corr = x['y'] - execdict['y_offset']
        else:
            x_corr = x - execdict['x_offset']  # correct x
            y_corr = y - execdict['y_offset']  # correct y

        gamma = self.math.pi - self.math.acos(
            # shoulder-elbow-gripper outside angle (elbow angle from straight out; radians; no sign)
            (
                x_corr ** 2 + y_corr ** 2 - execdict['sh_el'] ** 2 - execdict['el_gr'] ** 2
            ) / (
                -2 * execdict['sh_el'] * execdict['el_gr']
            )
        )

        # print("outside elbow angle\t",math.degrees(gamma)) #from zero elbow angle, no sign.

        pseudoline = self.math.sqrt(x_corr ** 2 + y_corr ** 2)  # length of pseudoline (hypotenuse)

        pseudoangle = self.math.atan2(y_corr, x_corr)
        # print("pseudoAngle\t\t\t",math.degrees(pseudoAngle))   #pseudoline angle

        L1insideAngle = self.math.acos(  # shoulder-elbow-gripper angle
            (
                execdict['sh_el'] ** 2 + pseudoline ** 2 - (execdict['el_gr'] ** 2)
            ) / (
                2 * execdict['sh_el'] * pseudoline
            )
        )
        # print("L1insideAngle\t\t",self.math.degrees(L1insideAngle))

        L1angle1 = pseudoangle - self.math.pi / 2 - L1insideAngle  # CW angle
        L1angle2 = pseudoangle - self.math.pi / 2 + L1insideAngle  # CCW angle
        # print("L1angle1\t\t\t",self.math.degrees(L1angle1))
        # print("L1angle2\t\t\t",self.math.degrees(L1angle2))

        L1angle1 /= 2 * self.math.pi  # convert angle from radians to a fraction of a circle (1 rotation = 1.0)
        L1angle2 /= 2 * self.math.pi
        L1angle1 *= execdict['sh_cpr']  # convert fraction to counts
        L1angle2 *= execdict['sh_cpr']
        L1angle1 += execdict['sh_zero']  # adjust to zero
        L1angle2 += execdict['sh_zero']

        gamma /= 2 * self.math.pi
        gamma *= execdict['el_cpr']

        def intround(i): return int(round(i, 0))  # returns the integer value of x rounded

        # print(L1angle1,L1angle2)

        shright = {  # shoulder right, elbow left
            2: intround(L1angle1),
            1: intround(execdict['el_zero'] - gamma)
        }
        shleft = {  # shoulder left, elbow right
            2: intround(L1angle2),
            1: intround(execdict['el_zero'] + gamma)
        }
        return shright, shleft

    def keyboard(self):
        """
        Keyboard driving mode
        
        Commands:
        i  gripper   CCW/+    (axis 0) 
        y  gripper   CW/-     (axis 0) 
        k  elbow     CW/+     (axis 1) 
        h  elbow     CCW/-    (axis 1) 
        ,  shoulder  CCW/+    (axis 2)
        n  shoulder  CW/-     (axis 2)
        u  robot     up       (axis 3)
        m  robot     down     (axis 3)
        /  exit driving mode
        
        Count jumps:
        q  big movements (1000 counts per command)
        a  medium (100)
        z  small (10)
        x  micro (2)
        """
        if self.kw['verbose']:
            print('Initializing keyboard driving mode, input "/" to exit this mode')
        valid = ['i', 'y', 'k', 'h', ',', 'n', 'u', 'm', '/', 'q', 'a', 'z', 'x', 'help']
        inp = ''
        self.sercon.write(self.pkg('KEYB'))
        while inp != '/':  # / is the exit command
            inp = ''
            while inp not in valid:  # wait for valid command
                inp = input('Input: ').lower()  # grab the input (convert to lower case to avoid case mismatches)
                if inp not in valid:  # if an invalid entry was provided
                    print("Invalid input, type 'help' for valid commands")
            if inp == 'help':  # if the user asks for help
                print(self.keyboard.__doc__)
            else:
                self.sercon.write(inp.encode('utf-8'))  # write the key
                if inp != '/':
                    self.parseloc(self.read(), True)  # read and parse the position output
                    # self.loc.update(self.position())

    def move_item(self, item, location):
        """moves the specified item from its current location to the specified location"""
        pass
        # TODO write a general pickup-place call sequence to make it a a single line

    def output(self, axis, value, sleep=0.2):
        """sets the output axis to the specified value"""
        if type(axis) == int:  # if an axis value was provided
            self.execute('output', axis, value)
        elif type(
                axis) == str:  # catches if a string axis was provided (mapped by robot_paramaters.py output dictionary)
            self.execute('output', self.ops[axis], value)
        self.t.sleep(sleep)  # sleep for 200 ms to allow the actuator to perform before moving

    def parseloc(self, string, printout=False):
        """parses the location output string of the robot"""
        splitstring = string.strip().split(',')[:-1]  # split it and remove /r values
        dct = {}  # dictionary of positions with integer keys and values
        for i in splitstring:  # go through list and add to dictionary
            x, y = i.split(':')
            y = int(y)
            dct[int(x[-1])] = y
        if printout:  # print if specified
            for i in sorted(dct):
                if dct[i] != 0:
                    print('Pos%d: %d' % (i, dct[i]))
        return dct

    def pkg(self, string):
        """packages the provided command and utf-8 encodes it"""
        string = '<' + string + '\r'
        return string.encode('utf-8')

    def pickup(self, item):
        """picks up the specified item

        A Vial instance may be provided.

        If an object is provided, it will be stored in the in_gripper property
        """
        # automatically take the top of the item and move down enough to grip the item
        if repr(item).startswith('Vial') is True:  # if handed a vial instance
            xy = {}
            xy['x'] = item.location['x']
            xy['y'] = item.location['y']
            z = {}
            z['z'] = item.location['z']
            z['z'] += item.p['height']  # offset by height
            z['z'] -= item.p['capheight']  # and cap height
            self.goto({xy})
            self.goto(z)
            self.output('gripper', 1)  # engage the gripper
            self.in_gripper = item  # put the item in the gripper variable
            self.goto({'z': self.kw['safeheight']})  # go to safe height
        else:
            # TODO code the pickup of a non-vial object
            raise ValueError("Pickups of non-vial objects haven't been coded yet")

    def place(self, position):
        """place the held item in the specified location"""
        if self.in_gripper is None:
            raise ValueError('This communicator instance is not aware of any item currently held in the gripper.')
        self.goto(position, order='sez')  # go to the position
        self.output('gripper', 0)  # release the item
        if repr(self.in_gripper).startswith('Vial'):  # if a Vial object
            out = self.in_gripper
            self.in_gripper = None
            out.location.update(position)  # update the vial's position
            return out  # return the vial object
        else:
            out = position
            self.in_gripper = None
            return out  # return the position

    def position(self):
        """get the position of of the robot
        This will be relative to the home position (or initial position if the robot was not homed)
        """
        self.loc = self.parseloc(self.execute('position'))
        return self.loc

    def read(self, attempts=500, sleeptime=0.01):
        """
        reads from the robot
        
        attempts: number of read attempts to make
        
        sleeptime: the time to wait between read attempts in seconds
        """
        # waiting = self.sercon.inWaiting() # check for waiting bytes
        # while waiting == 0: # if there are no bytes, wait
        #     self.t.sleep(sleeptime) # wait for a bit of time
        #     waiting = self.sercon.inWaiting() # check again
        # buffer = self.sercon.read(waiting).decode('ascii') # read from the buffer

        # TODO create an error checking function (entire command should be encapsulated in < >)
        buffer = ''
        while buffer.endswith('>\r') is False:  # check for the end character
            waiting = self.sercon.inWaiting()  # check for more bytes
            while waiting == 0:  # wait for more bytes
                self.t.sleep(sleeptime)
                waiting = self.sercon.inWaiting()
            buffer += self.sercon.read(waiting).decode('ascii')
        # print(buffer)
        return buffer

    def roughhome(self):
        """roughly homes the robot for faster initialization"""
        if self.kw['verbose']:
            print('Rough homing the robot')
        if self.kw['homeinitialize'] is True:
            acc = 150000
            vel = 10000
            self.execute('movesync', 0, 3,  # home gripper and z
                         0,
                         10,
                         acc, vel)
            self.loc.update({0: 0, 3: 10})
            self.execute('movesync', 1, 2,  # home shoulder and elbow
                         100,
                         100,
                         acc,
                         vel)
            self.loc.update({1: 100, 2: 100})

    def spin(self, time=60, v=25000):
        """spins the gripper for the specified amount of time

        a velocity of 2000 is 60 rpm
        25000 is 750 RPM
        """
        endcounts = self.loc[0] + int(time * v)
        self.execute('spin', 0, endcounts, a=50000, v=v)
        self.loc.update({0: endcounts})

    def test(self, repeats=1):
        """
        tests communication with the robot
        
        repeats: repeats the test executions this many times
        """
        if self.kw['verbose']:
            print('Executing test functions')
        for i in range(repeats):
            print(repr(self.execute('echo')))  # echos the robot
            print(repr(self.execute('random')))  # grabs a random number
            print(repr(self.execute('plustwo', i + 1)))  # returns the iteration plus 2

    def uncap(self, vial, tray):
        """
        uncaps the provided Vial object
        """
        if repr(vial).startswith('Vial') is False:
            raise ValueError('The communicator.uncap() function must be handed an instance of items.Vial')
        if vial.location is None:
            raise ValueError('The provided vial instance does not have a location associated with it.')

        if self.kw['verbose']:
            print("Executing uncap procedure on vial '%s'" % vial.name)
            # TODO make this a specific unscrew function
            # TODO when an uncap is performed, set the in_gripper to 'cap' (and unset in recap)


if __name__ == '__main__':
    from PyNR.dependencies._communicator import communicator

    n9 = communicator(
        # comport = 5, # Lars' laptop's port for the propeller board
        # homeinitialize = False,
        verbose=True,
        # acceleration = 25000,
        # velocity = 5000,
    )

    # from PyNR.dependencies.items import Vial
    # from PyNR.dependencies.vialprofiles import profiles
    # v1 = Vial('testvial',vialproperties=profiles['HPLC1mLpierce'])
