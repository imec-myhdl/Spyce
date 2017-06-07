from scipy.optimize import leastsq
from scipy.signal import step2
import numpy as np
import scipy as sp
from control import *
from control.matlab import *
from scipy.optimize import leastsq
from supsictrl.ctrl_repl import *
from supsictrl.ctrl_utils import *

g = 9.81;
K = 5.0/7*g

Ts=10e-3;

A = [[0,1],[0,0]]
B = [[0],[K]]
C = [1,0]
D = [0] 

# Plant continous and discrete
sysc = ss(A,B,C,D)
sysd = c2d(sysc, Ts, 'zoh')

wn = 6
xi1 = np.sqrt(2)/2;

cl_p1 = [1,2*xi1*wn,wn**2]
cl_p2=[1,wn]
cl_poly=sp.polymul(cl_p1,cl_p2)

cl_poles = sp.roots(cl_poly)   # Desired continous poles
cl_polesd = sp.exp(cl_poles*Ts)  # Desired discrete poles

z1=sp.shape(sysd.A);
sz2=sp.shape(sysd.B);

# Add discrete integrator for steady state zero error
Phi_f=np.vstack((sysd.A,-sysd.C*Ts))
Phi_f=np.hstack((Phi_f,[[0],[0],[1]]))
G_f=np.vstack((sysd.B,zeros((1,1))))

k=place(Phi_f,G_f,cl_polesd)

# Full order observer
p_oc=10*(cl_poles[1:3])
p_od=sp.exp(p_oc*Ts);

f_obs=full_obs(sysd,p_od)

#Reduced order observer
p_oc=-10*max(abs(cl_poles))
p_od=sp.exp(p_oc*Ts);

T=[0,1]
r_obs=red_obs(sysd,T,[p_od])

contr_I=comp_form_i(sysd,f_obs,k)

# Anti windup
[gss_in,gss_out]=set_aw(contr_I,[0,0,0])

Sat = np.pi/4


