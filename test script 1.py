# 25-45 psi

from PyNR.dependencies._communicator import communicator

n9 = communicator(
    comport = 6,
    homeinitialize = True,
    verbose = True,
    # stepcycle = True,
    # acceleration = 50000,
    # velocity = 5000,
    )

# elbow goes farther on move 2
acc = 150000
vel = 10000

"""
n9.execute('movesync',1,2,
        5000, #va move to
        8000, # vb move to
        acc, # acceleration (~150000)
        vel # velocity (5000-45000, go with 20000)
        )

n9.execute('movesync',1,2,
        16000, #va move to
        17000, # vb move to
        acc, # acceleration (~150000)
        vel # velocity (5000-45000, go with 20000)
        )

n9.execute('movesync',0,3,
        11000, #va move to
        5000, # vb move to
        acc, # acceleration (~150000)
        vel # velocity (5000-45000, go with 20000)
        )

n9.execute('movesync',0,2,
        3000, #va move to
        12000, # vb move to
        acc, # acceleration (~150000)
        vel # velocity (5000-45000, go with 20000)
        )
"""

# go to vial

n9.execute('movesync',1,2,2550,4350) # position shoulder and arm
n9.execute('movesync',0,3,100,12250) # position z and gripper

# gripper grip

pos = n9.position()

# curr0 = 100
# curr3 = 12200
rots = 2
pitch = 1.07

rotcounts = (pos[0] - rots*4000)
upcounts = (pos[3] - rots*pitch*120)
n9.execute('movesync',0,3,rotcounts,upcounts)
pos1 = n9.position() # position with cap removed

# position filler
n9.execute('movesync',1,2,1900,2200)
n9.execute('movesync',0,3,rotcounts,12250)

# fill

# move back
n9.execute('movesync',0,3,pos1[0],pos1[3])
n9.execute('movesync',1,2,pos1[1],pos1[2])

# recap
n9.execute('movesync',0,3,pos[0],pos[3])


n9.disconnect(True)