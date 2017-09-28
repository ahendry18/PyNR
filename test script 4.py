import time
t0 = time.time()
from PyNR.dependencies.components import VialTray

vialpop = {
    # 'H8':{},
    'H9':{},
    'H10':{},
    'H11':{},
    'H12':{},
}
from PyNR.dependencies.vialprofiles import  profiles

VT = VialTray(population=vialpop,vialproperties=profiles['HPLC1mLpierce'])
# locarray = VT.locationarray()

from PyNR.dependencies._communicator import Communicator

n9 = Communicator(
    verbose=True,
    # stepcycle=True,
    acceleration=35000,
    velocity=15000,
    # comport=5,
)

disploc = None
ucloc = {'x':-188.36,'y':200.585}

newplaces = ['G8','G9','G10','G11','G12']

n9.goto(3,9000)
for ind,vial in enumerate(VT):
    n9.goto(vial.location, {3: 10900}) # go to vial
    n9.output('gripper',1) # grip
    n9.goto(3,7000) # move up

    n9.goto(ucloc,{3:8700}) # move to vial gripper
    n9.output('vial_gripper',1)

    gr = n9.loc[0]
    z = n9.loc[3]
    rotcounts = (gr - 2 * 4000)
    upcounts = (z - 2 * vial.p['pitch'] * n9.kw['zcountspermm'])
    n9.goto({3:upcounts,0:rotcounts})

    # n9.output(3,0) # uncomment when uncap has happened
    if disploc is None:
        disploc = n9.chooseangle(n9.inverse_kinematics(-188.36,200.585,el_gr=210.879))
    n9.goto({3:7000},disploc,{3:8700})
    time.sleep(0.5) # wait for "fill"
    n9.goto({3:7000},ucloc,{3:upcounts})
    n9.goto({0:gr,3:z})
    n9.output('vial_gripper',0)
    n9.goto({3:7000})
    n9.goto(VT[newplaces[ind]],{3:10900})
    n9.output(3,0)
    n9.goto(3,7000)

n9.roughhome()

print('total time (min)',(time.time()-t0)/60)