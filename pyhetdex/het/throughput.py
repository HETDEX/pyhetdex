"""

This server returns the illumination & throughput in the focal plane
of HE for a focal plane position and a shot object
containing important information about the telescope
configuration

@author dfarrow

"""
from __future__ import absolute_import, print_function
import numpy

class throughputServer(object):
    gconfig = None # global configuration container
    name = "Throughput server, returns a dummy model for throughput"
    
    def __init__(self, gconfig, shot):
        self.shot = shot
        self.gconfig = gconfig
        
        #Read in throughput file
        self.throughput_file = self.gconfig.get("throughputServer", "ThroughputTemplate")
        self.lambdas, self.throughputs = self.loadThroughputTemplate(self.throughput_file)
        
        #Specify throughput model
        self.illumination_model = self.gconfig.get("throughputServer", "IlluminationModel")

    def loadThroughputTemplate(self, throughputFile):
        
        lambdas = []
        throughputs = []
        
        try:
            f = open(throughputFile)
            for l in f:
                if l.startswith("#"): 
                    continue
                lambdas.append(float(l.split()[0]))
                throughputs.append(float(l.split()[1]))
            f.close()
            
            norm = max(throughputs)
            throughputs = numpy.array(throughputs) / norm
        except IOError:
            print("[throughputServer] ERROR: Could not open ", throughputFile)
            raise
        except:
            raise
            
            
        return lambdas, throughputs
        
    #Output thoughput file, and return f_illum
    def outputThroughputFile(self, ID, x, y):
        # x, y are the focal plane position of the IFU in arcseconds
        # multiplies a template throughput files with a focal-plane
        # position dependent illumination correction
        outfile = "throughput%04d.dat"%ID
        f_illum = self.fplaneToThroughput(x, y)

        with open(outfile, 'w') as f:
            s = "# L throughput"
            f.write(s + "\n")
            for l, t in zip(self.lambdas, self.throughputs):
                f.write( "%5.2f %5.4f \n"%(l,t*f_illum))
            f.close()
            
        return f_illum
        
    def fplaneToThroughput(self, x, y):
        # x, y are the focal plane position of the IFU in arcseconds
        # This is also a dummy, should contain some clever model to give throughput based on focal 
        # plane position, at the moment just falls off like a power law
        
        if "SimplePowerLaw" in self.illumination_model:
            s_sq = (x*x + y*y)/(435600.0)
            r = 1.0 / (1.0 + s_sq) 
        else:
            print("[throughputServer] Error: Unrecognised IlluminationModel choice ", self.throughput_model)
            raise

        return r
    