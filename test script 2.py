from PyNR.dependencies._communicator import communicator

n9 = communicator(
    verbose=True,
    homeinitialize=True,
    # stepcycle=True
)

n9.goto({1:18176,2:19395},{3:10900})
n9.output(3,1)
n9.goto({3:5000},{1:1000,2:5000},{1:10374,2:16451})
n9.goto({1:18176,2:19395},{3:10900})
n9.output(3,0)
n9.roughhome()