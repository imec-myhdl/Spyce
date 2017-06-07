from scipy.optimize import leastsq
from scipy.signal import step2
import numpy as np
import scipy as sp
from control import *
import control.matlab as mt
from supsictrl.ctrl_repl import *
from supsictrl.ctrl_utils import *
from matplotlib.pyplot import plot, show

# Motor response for least square identification
def residuals(p, y, t):
    [k,alpha] = p
    print(k, type(k))
    alpha = p[1]
    print(alpha, type(alpha))
    g = tf(k,[1,alpha,0])
    Y,T = mt.step(g,t)
    err=y-Y
    return err

# Identify motor 1

x = np.loadtxt('MOT');
t = x[:,0] 
y = x[:,2] 

t=t[100:250] 
t=t-t[0] 
y=y[100:250] 
y=y-y[0]


U0=500  
p0=[1.0,4.0]

ydata = y/U0
tt = np.linspace(t[0],t[-1],len(t))

plsq = leastsq(residuals, p0, args=(ydata, tt))

K = plsq[0][0]
d = plsq[0][1]

g=mt.tf([K],[1,d,0])  # Transfer function

Y,T = mt.step(g,tt)
plot(T,Y)
plot(t,ydata)
show()

# Design Controller Motor 1
a=[[0,1],[0,-d]]
b=[[0],[K]]
c=[[1,0]];
d=[0];

sysc=ss(a,b,c,d)                # Continous state space form

Ts=0.01                         # Sampling time
sys = c2d(sysc,Ts,'zoh')       # Get discrete state space form

# Control system design
# State feedback with integral part

wn = 30
xi=np.sqrt(2)/2

cl_p1=[1,2*xi*wn,wn**2]
cl_p2=[1,wn]
cl_poly=sp.polymul(cl_p1,cl_p2)
cl_poles=sp.roots(cl_poly);  # Desired continous poles
cl_polesd=sp.exp(cl_poles*Ts)  # Desired discrete poles

sz1=sp.shape(sys.A);
sz2=sp.shape(sys.B);

# Add discrete integrator for steady state zero error
Phi_f=np.vstack((sys.A,-sys.C*Ts))
Phi_f=np.hstack((Phi_f,[[0],[0],[1]]))
G_f=np.vstack((sys.B,zeros((1,1))))

k=place(Phi_f,G_f,cl_polesd)

#Reduced order observer
p_oc=-10*max(abs(cl_poles))
p_od=sp.exp(p_oc*Ts);

T=[0,1]
r_obs=red_obs(sys,T,[p_od])

contr_I=comp_form_i(sys,r_obs,k)

# Anti windup
[gss_in,gss_out]=set_aw(contr_I,[0,0])

Ref = 15
Res = 1024
Kp = 400
Ki = 216
Sat = 2000



