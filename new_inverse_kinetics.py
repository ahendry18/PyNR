def inverse_kinematics(x,y,**kwargs):
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

    parameters = {
        'sh-el': 170,  # shoulder to elbow length
        'el-gr': 170,  # elbow to gripper length
        'sh-cpr': 50500,  # shoulder counts per revolution
        'el-cpr': 25500,  # elbow counts per revolution
        'sh-zero': 16451,  # shoulder zero value (in counts)
        'el-zero': 10374,  # elbow zero value (in counts)
        'x-offset': 0.910, # x error
        'y-offset': -0.225, # y error
    }
    parameters.update(kwargs)

    x_corr = x - parameters['x-offset'] # correct x
    y_corr = y - parameters['y-offset'] # correct y
    import math

    gamma = math.pi - math.acos( # shoulder-elbow-gripper outside angle (elbow angle from straight out; radians; no sign)
        (
            x_corr ** 2 + y_corr ** 2 - parameters['sh-el'] ** 2 - parameters['el-gr'] ** 2
        ) / (
            -2 * parameters['sh-el'] * parameters['el-gr']
        )
    )

    print("outside elbow angle\t",math.degrees(gamma)) #from zero elbow angle, no sign.

    pseudoLine = math.sqrt(x_corr**2 + y_corr**2) #length of pseudoLine (hypotenuse)

    pseudoAngle = math.atan2(y_corr,x_corr)
    print("pseudoAngle\t\t\t",math.degrees(pseudoAngle))   #pseudoline angle

    L1insideAngle = math.acos( # shoulder-elbow-gripper angle
        (
            parameters['sh-el'] ** 2 + pseudoLine ** 2 - (parameters['el-gr'] ** 2)
        ) / (
            2 * parameters['sh-el'] * pseudoLine
        )
    )
    print("L1insideAngle\t\t",math.degrees(L1insideAngle))

    L1angle1 = pseudoAngle -math.pi/2 - L1insideAngle # CW angle
    L1angle2 = pseudoAngle -math.pi/2 + L1insideAngle # CCW angle
    print("L1angle1\t\t\t",math.degrees(L1angle1))
    print("L1angle2\t\t\t",math.degrees(L1angle2))

    L1angle1 /= 2*math.pi # convert angle from radians to a fraction of a circle (1 rotation = 1.0)
    L1angle2 /= 2*math.pi
    L1angle1 *= parameters['sh-cpr'] # convert fraction to counts
    L1angle2 *= parameters['sh-cpr']
    L1angle1 += parameters['sh-zero'] # adjust to zero
    L1angle2 += parameters['sh-zero']

    gamma /= 2*math.pi
    gamma *= parameters['el-cpr']

    intround = lambda i: int(round(i,0)) # returns the integer value of x rounded

    print(L1angle1,L1angle2)

    shright = {# shoulder right, elbow left
        2:intround(L1angle1),
        1:intround(parameters['el-zero'] - gamma)
    }
    shleft = {# shoulder left, elbow right
        2:intround(L1angle2),
        1:intround(parameters['el-zero'] + gamma)
    }

    return shright,shleft