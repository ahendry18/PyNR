def inverse_kinematics(x, y, **kwargs):
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
        'sh-el': 170, # shoulder to elbow length
        'el-gr': 170, # elbow to gripper length
        'sh-cpr': 50000, # shoulder counts per revolution
        'el-cpr': 25000, # elbow counts per revolution
        'sh-zero': 16465, # shoulder zero value (in counts)
        'el-zero': 10497, # elbow zero value (in counts)
    }
    parameters.update(kwargs)
    import math


    beta = math.acos( # shoulder elbow gripper angle
        (
            parameters['sh-el']**2 + parameters['el-gr']**2 - x**2 - y**2
         ) / (
            2 * parameters['sh-el'] * parameters['el-gr']
        )
    )

    alpha = math.acos( # elbow shoulder gripper angle
        (
            x**2 + y**2 + parameters['sh-el']**2 - parameters['el-gr']**2
        ) / (
            2 * parameters['sh-el'] * math.sqrt(x**2 + y**2)
        )
    )

    gamma = math.atan2(y,x)

    righty = [
        parameters['el-zero'] + ((math.pi - beta) * parameters['el-cpr']), #/ (2 * math.pi)),  # elbow
        parameters['sh-zero'] - ((gamma - alpha)*parameters['sh-cpr'])#/(2*math.pi)), # shoulder
    ]
    lefty = [
        parameters['el-zero'] + ((beta - math.pi) * parameters['el-cpr']), #/ (2 * math.pi)),# elbow
        parameters['sh-zero'] - ((gamma + alpha)*parameters['sh-cpr'])#/(2*math.pi)) # shoulder
    ]

    print('righty:',righty)
    print('lefty:',lefty)

    return righty,lefty


"""
    # original method, ignore
    c = math.sqrt(x**2+y**2) # hypotenuse
    gamma = math.pi - math.acos( # elbow angle
        (
            parameters['sh-el']**2 + parameters['el-gr']**2 - c)/(2*parameters['sh-el']*parameters['el-gr']
        )
    )
    alpha = math.acos(  # elbow-gripper-shoulder angle
        (
            parameters['el-gr']**2 + c**2 - parameters['sh-el']**2
        ) / (
            2 * parameters['el-gr'] * c
        )
    )
    beta = math.pi/2-alpha-gamma # elbow-shoulder-gripper angle
    epsilon = math.sin(y/c) # x-axis-shoulder-gripper angle
    delta = math.pi-beta-epsilon # y-axis-shoulder-elbow angle

    print('degrees delta: ',math.degrees(delta),'gamma: ',math.degrees(gamma))
    print('rad delta: ',delta,'gamma: ',gamma)
    delta *= parameters['sh-cpr']/(2*math.pi) # convert shoulder angle to counts
    gamma *= parameters['el-cpr']/(2*math.pi) # conver elbow angle to counts

    delta = parameters['sh-zero'] - delta # offset by the shoulder zero (increases CCW)
    gamma = parameters['el-zero'] + gamma # offset by the elbow zero (incrases CW)

    return delta,gamma # return the shoulder and elbow angles
    """
