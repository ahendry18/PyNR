class piercearray(object):
    def __init__(self,**kwargs):
        """
        creates an array of piece locations for a septum
        based on the gauge of the needle and the minimum spacing provided
        """
        self.kw = {
            'gauge':24, # the gauge of the needle
            'minspacing':1.5, # the minimum spacing for the holes (in units of needle diameters)
            'piercediameter':5.97, # the diameter of the piercable area
            'alloweduses': 1, # the number of times the holes may be used
            'diam': None, # diameter (can be specified instead of gauge)
            }
        self.kw.update(kwargs)
        
        def pol2cart(rho, phi):
            """converts spherical polar coordinates into cartesian coordinates"""
            x = rho * np.cos(phi)
            y = rho * np.sin(phi)
            return(x, y)
        
        gauges = { # outer diameter of needle gauges in mm
            7:  4.572,
            8:  4.191,
            9:  3.759,
            10: 3.404,
            11: 3.048,
            12: 2.769,
            13: 2.413,
            14: 2.108,
            15: 1.829,
            16: 1.651,
            17: 1.473,
            18: 1.270,
            19: 1.067,
            20: 0.9081,
            21: 0.8192,
            22: 0.7176,
            23: 0.6414,
            24: 0.5652,
            25: 0.5144,
            26: 0.4636,
            27: 0.4128,
            28: 0.3620,
            29: 0.3366,
            30: 0.3112,
            31: 0.2604,
            32: 0.2350,
            33: 0.2096,
            34: 0.1842,
            }
        if self.kw['diam'] is not None:
            self.diam  = self.kw['diam']
        else:
            self.diam = gauges[self.kw['gauge']]
        
        import numpy as np
        rlist = np.arange(0.,(self.kw['piercediameter']/2-self.diam/2),self.diam*self.kw['minspacing']) # list of radii
        self.locs = [[0.,0.]] # array of locs
        for r in rlist:
            circum = 2*np.pi*r # circumference at radius  
            numpierce = circum/self.diam # number of possible piercings in that radius
            # if numpierce %2 != 0: # ensure the number of holes is even
            #     numpierce -=1
            numpierce = int(numpierce/self.kw['minspacing']) # space holes out to minimum spacing
            thetas = [(2*np.pi)/numpierce*i for i in range(numpierce)] # angles of those piercings
            for theta in thetas:
                self.locs.append(pol2cart(r,theta)) # convert to x,y and append to locs list
        self.generatorarray = self.yieldloc() # creates a generator
        self.ntimesused = 0 # number of times the set of holes has been used
        self.i = 0
        # for ind,val in enumerate(self.locs):
        #     self.locs[ind] = pol2cart(*val)
    
    def __repr__(self):
        return "%s(%d guage)" %(self.__class__.__name__,self.kw['gauge'])
    def __str__(self):
        return "Needle pierce array: %d gauge" %self.kw['gauge']
    
    def yieldloc(self):
        """grabs the next location"""
        for ind,loc in enumerate(self.locs):
            self.i = ind
            yield loc
    
    def getloc(self):
        """retrieves the next location from the generator"""
        try:
            return next(self.generatorarray) # try to return the next pipette tip
        except StopIteration:
            self.ntimesused += 1 # increase the count of the number of times the array has been used
            if self.ntimesused == self.kw['alloweduses']: # if the allowable number of uses has been reached
                raise self.MaxPierces
            self.generatorarray = self.yieldloc() # otherwise, reset the array
            return next(self.generatorarray)
            
    class MaxPierces(Exception):
        def __init__(self):
            """custom exception to indicate that this tray is empty"""
            super(piercearray.MaxPierces, self).__init__("The maximum number of pierces for this septum has been reached")
    
    def plot(self):
        """plots a representation of the planned pierce array"""
        import pylab as pl
        pl.clf()
        pl.close()
        fig,ax = pl.subplots(figsize=(15,15))
        
        circles = [pl.Circle((0.,0.),self.kw['piercediameter']/2.,color='g',fill=False,clip_on=False,linewidth=2)]
        
        for ind,val in enumerate(self.locs):
            if ind < self.i: # if hole has been used
                c = {'color':'r'}
            elif ind == self.i: # current hole
                c = {'color':'y'}
            else: # unused
                c = {'color':'g'}
            ax.text(*val,ind+1,color='w',verticalalignment='center',horizontalalignment='center',size=20)
            circles.append(pl.Circle(val,self.diam/2.,clip_on=False,fill=True,**c))
        for circle in circles:
            ax.add_artist(circle)
        bounds = [-self.kw['piercediameter']/2,self.kw['piercediameter']/2]
        ax.set_xlim(*bounds)
        ax.set_ylim(*bounds)
        pl.show()
        


# diam = 0.5652 # arbitrarily chosen 24 gauge needle diameter
# 
# minspacing = 1.5 # number of times the width of the needle
# 
# piercediameter = 5.97 # pierce diameter of a 1 mL HPLC vial


import numpy as np

# numcircles = int((piercediameter-diam/2)/diam/2)
# rlist = np.linspace(0.,(piercediameter/2-diam/2),numcircles)


pa = piercearray(
    minspacing = 1.5, # the minimum spacing for the holes (in units of needle diameters)
    piercediameter = 5.97, # the diameter of the piercable area
    )

    
