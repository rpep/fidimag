import numpy as np

from micro import FDMesh
from micro import UniformExchange
from micro import Sim
from micro import Demag


from util.oommf import compute_demag_field
from util.oommf import compute_exch_field

import clib

def compare_fields(v1, v2):    
    
    v1.shape = (3,-1)
    v2.shape = (3,-1)
    
    f = (v1[0,:]**2+v1[1,:]**2+v1[2,:]**2)**0.5
    diff = abs(v1 - v2)
    
    print 'max error',np.max(diff), np.argmax(diff),len(v1)
    #print v1[0,:]-v2[0,:]
    
    #print v2[0,:]
    
    max0 = np.max(diff[0,:]/f)
    max1 = np.max(diff[1,:]/f)
    max2 = np.max(diff[2,:]/f)
    
    v1.shape = (-1,)
    v2.shape = (-1,)
    return max0, max1, max2


def test_oommf_coefficient():
    
    res =  clib.compute_Nxx(10,1,1,1,2,3)

    assert  abs(-0.000856757528962409449 - res) < 5e-15
    
    #print clib.compute_Nxx_asy(10,1,1,1,2,3)


def test_exch_field_oommf(A=1e-11, Ms=2.6e5):
    
    mesh = FDMesh(nx=10, ny=3, nz=2, dx=0.5, unit_length=1e-9)
    
    sim = Sim(mesh)
    sim.Ms = Ms
    
    exch = UniformExchange(A=A)
    sim.add(exch)
    
    def init_m(pos):
        
        x,y,z = pos
        
        return (np.sin(x)+y+2.3*z,np.cos(x)+y+1.3*z,0)
    
    sim.set_m(init_m)
    
    field = exch.compute_field()
    
    init_m0="""
    return [list [expr {sin($x*1e9)+$y*1e9+$z*2.3e9}] [expr {cos($x*1e9)+$y*1e9+$z*1.3e9}] 0]
    """
    field_oommf = compute_exch_field(mesh, Ms=Ms, init_m0=init_m0, A=A)
    
    mx0,mx1,mx2 = compare_fields(field_oommf, field)
    assert max([mx0,mx1,mx2])< 1e-12

def test_demag_field_oommf(Ms=6e5):
    mesh = FDMesh(nx=5,ny=2,nz=3, unit_length=1e-9)
    sim = Sim(mesh)
    
    sim.Ms = Ms
    
    demag = Demag()
    sim.add(demag)
    
    def init_m(pos):
        
        x = pos[0]
        
        if x<=2:
            return (1,0,0)
        elif x>=4:
            return (0,0,1)
        else:
            return (0,1,0)
    
    sim.set_m(init_m)
    field = demag.compute_field()
    exact=demag.compute_exact()
    
    init_m0="""
    
    if { $x <=2e-9 } {
        return "1 0 0"
    } elseif { $x >= 4e-9 } {
        return "0 0 1"
    } else {
        return "0 1 0"
    }
    """
    
    field_oommf = compute_demag_field(mesh, Ms=Ms, init_m0=init_m0)
    
    mx0,mx1,mx2 = compare_fields(field_oommf, exact)
    print mx0,mx1,mx2
    assert max([mx0,mx1,mx2])< 2e-14
    
    mx0,mx1,mx2 = compare_fields(field_oommf, field)
    print mx0,mx1,mx2
    
    assert np.max(abs(field - field_oommf)) < 2e-9


def test_demag_field_oommf_large(Ms=8e5, A=1.3e-11):
    mesh = FDMesh(nx=150, ny=50, nz=1, dx=2.5, dy=2.5, dz=3, unit_length=1e-9)
    sim = Sim(mesh)
    
    sim.Ms = Ms
    
    exch = UniformExchange(A=A)
    sim.add(exch)
    
    demag = Demag()
    sim.add(demag)
        
    def init_m(pos):
        
        x,y,z = pos
        
        return (np.sin(x)+y+2.3*z,np.cos(x)+y+1.3*z,0)
    
    sim.set_m(init_m)
    demag_field = demag.compute_field()
    exch_field = exch.compute_field()
    

    
    #exact = demag.compute_exact()
    
    init_m0="""
    return [list [expr {sin($x*1e9)+$y*1e9+$z*2.3e9}] [expr {cos($x*1e9)+$y*1e9+$z*1.3e9}] 0]
    """
    
    demag_oommf = compute_demag_field(mesh, Ms=Ms, init_m0=init_m0)
    exch_oommf = compute_exch_field(mesh, Ms=Ms, init_m0=init_m0, A=A)
    

    mx0,mx1,mx2 = compare_fields(demag_oommf, demag_field)
    print mx0,mx1,mx2
    #assert max([mx0,mx1,mx2])< 5e-10

    mx0,mx1,mx2 = compare_fields(exch_oommf, exch_field)
    print mx0,mx1,mx2
    assert max([mx0,mx1,mx2])< 1e-11
    
    #mx0,mx1,mx2 = compare_fields(demag_oommf, exact)
    #print mx0,mx1,mx2
    
    
def test_energy(Ms=8e5, A=1.3e-11):
    
    mesh = FDMesh(nx=40, ny=50, nz=1, dx=2.5, dy=2.5, dz=3, unit_length=1e-9)
    sim = Sim(mesh)
    
    sim.Ms = Ms
    
    exch = UniformExchange(A=A)
    sim.add(exch)
    
    demag = Demag()
    sim.add(demag)
        
    def init_m(pos):
        
        x,y,z = pos
        
        return (np.sin(x)+y+2.3*z,np.cos(x)+y+1.3*z,0)
    
    sim.set_m(init_m)
    demag_energy = demag.compute_energy()
    exch_energy = exch.compute_energy()
    
    
    #init_m0="""
    #return [list [expr {sin($x*1e9)+$y*1e9+$z*2.3e9}] [expr {cos($x*1e9)+$y*1e9+$z*1.3e9}] 0]
    #"""
    
    #field_oommf = compute_exch_field(mesh, Ms=Ms, init_m0=init_m0, A=A)
    
    exch_energy_oommf =  1.9885853028738599e-19
    demag_energy_oommf =  5.5389695779175673e-19
    
    print demag_energy, exch_energy
    
    assert abs(exch_energy - exch_energy_oommf)/exch_energy_oommf<1e-15
    assert abs(demag_energy - demag_energy_oommf)/demag_energy_oommf <1e-10
    
if __name__=='__main__':

    #test_demag_field_oommf()
    
    #test_exch_field_oommf()
    
    #test_demag_field_oommf_large()
    
    test_energy()
    
    