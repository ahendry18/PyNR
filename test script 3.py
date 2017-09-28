from time import time
t0 = time()
from PyNR.dependencies.components import VialTray

vialpop = {
    'A1':{},
    'A2':{},
    'A3':{},
    'A4':{},
    'A5':{},
}
from PyNR.dependencies.vialprofiles import  profiles

VT = VialTray(population=vialpop,vialproperties=profiles['HPLC1mLpierce'])
# locarray = VT.locationarray()

from PyNR.dependencies._communicator import communicator

n9 = communicator(
    verbose=True,
    homeinitialize=True,
    # stepcycle=True,
    acceleration=75000,
    velocity=20000,
    comport=5,
)

disploc = None
ucloc = {'x':-188.36,'y':200.585}

n9.goto(3,9000)
for ind,vial in enumerate(VT):
    print(vial)
    n9.goto(vial.location, {3: 10900})
    n9.output(3,1)
    n9.goto(3,7000)

    n9.goto(ucloc,{3:8700})
    n9.output(5,1)

    gr = n9.loc[0]
    z = n9.loc[3]
    rotcounts = (gr - 2 * 4000)
    upcounts = (z - 2 * vial.p['pitch'] * n9.kw['zcountspermm'])
    n9.goto({3:upcounts,0:rotcounts})

    # n9.output(3,0) # uncomment when uncap has happened
    if disploc is None:
        disploc = n9.chooseangle(n9.inverse_kinematics(-188.36,200.585,el_gr=210.879))
    n9.goto({3:7000},disploc,{3:8700})
    n9.goto({3:7000},ucloc,{3:upcounts})
    n9.goto({0:gr,3:z})
    n9.output(5,0)
    n9.goto({3:7000})
    n9.goto(VT.locarray[1][ind],{3:10900})
    n9.output(3,0)
    n9.goto(3,7000)

n9.roughhome()

print('total time (min)',(time()-t0)/60)