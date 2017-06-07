from scipy.optimize import leastsq
from scipy.signal import step2
import numpy as np
import scipy as sp
from matplotlib.pyplot import plot, show
from control import *
import control.matlab as mt
import supsictrl.ctrl_repl as rp
from supsictrl.ctrl_utils import *
from supsictrl.ctrl_repl import *

# Gears
Rm = 0.0273/2   # Gear on motor
Rw = 0.0753/2   # Gear on wheel
#Krapp = Rw/Rm
#Krapp = 333.599109/(2*np.pi*20)
Krapp = 48.0/18.0

#Motor
kt = 126e-3
Kt = kt*Krapp   # Torque constant on wheel

# Wheel
def residuals(p, y, t):  
    [k,alpha] = p
    g = tf(k,[1,alpha,0])
    Y,T = mt.step(g,t)
    err=y-Y
    return err

x = np.loadtxt('ID_23082016');
t = x[:,0] 
y = x[:,1]
y=y-y[0]
y = y/Krapp

U0=1000
p0=[1,1]

t = np.arange(0,6.01,0.01)
ydata = y/U0
plsq = leastsq(residuals, p0, args=(ydata, t))

K = plsq[0][0]
D = plsq[0][1]

g=tf([K],[1,D,0])  # Transfer function Torque on Wheel -> Wheel angle

Y,T = mt.step(g,t)
plot(T,Y)
plot(t,ydata)
show()

# Design Controller
a=[[0,1],[0,-D]]
b=[[0],[K]]
c=[[1,0]];
d=[0];

sysc=ss(a,b,c,d)                # Continous state space form

Ts=0.01                         # Sampling time
sys = c2d(sysc,Ts,'zoh')        # Get discrete state space form

# Control system design - Wheel position
# State feedback with integral part

wn = 5
xi=np.sqrt(2)/2

cl_p1=[1,2*xi*wn,wn**2]
cl_p2=[1,wn]
cl_poly=sp.polymul(cl_p1,cl_p2)
cl_poles=sp.roots(cl_poly);   # Desired continous poles
cl_polesd=sp.exp(cl_poles*Ts)  # Desired discrete poles

sz1=sp.shape(sys.A);
sz2=sp.shape(sys.B);

# Add discrete integrator for steady state zero error
Phi_f=np.vstack((sys.A,-sys.C*Ts))
Phi_f=np.hstack((Phi_f,[[0],[0],[1]]))
G_f=np.vstack((sys.B,np.zeros((1,1))))

k=rp.place(Phi_f,G_f,cl_polesd)

#Reduced order observer
p_oc=-10*max(abs(cl_poles))
p_od=sp.exp(p_oc*Ts);

T=[0,1]
r_obs=red_obs(sys,T,[p_od])

contr_I=comp_form_i(sys,r_obs,k)

# Anti windup
[gss_in,gss_out]=set_aw(contr_I,[0,0])

Sat = 3300

# Ball On Whell
# Constants
g = 9.81;

# Ball
M_b = 0.106712  # Palla blu
#M_b = 0.083      # Palla rossa
R_b = 0.105/2   # Palla blu
#R_b = 0.04      # Palla rossa
#R_b = 0.05165
J_b = 2.0/3*M_b*R_b**2
J_b = 2.3608e-04; # taratura palla blu
#J_b = 3.4147e-4   # Palla rossa


# Wheel
J_w = Kt/K
J_w = 58.4315
d_w = D*J_w
d_w = 5.078122003714248
R_w = 0.285

# State matrices (from Maxima Lagrange Model)
# Model
# Input Imot
# States: phi_w, phi, w_w, w
A = [[0,0,1,0],[0,0,0,1],[0,((J_b*M_b*R_w**3+J_b*M_b*R_b*R_w**2)*g)/(J_b*M_b*R_w**4+2*J_b*M_b*R_b*R_w**3+((J_w+J_b)*M_b*R_b**2+J_b*J_w)*R_w**2+2*J_w*M_b*R_b**3*R_w+J_w*M_b*R_b**4),-(((M_b*R_b**2+J_b)*R_w**2+2*M_b*R_b**3*R_w+M_b*R_b**4)*d_w)/(J_b*M_b*R_w**4+2*J_b*M_b*R_b*R_w**3+((J_w+J_b)*M_b*R_b**2+J_b*J_w)*R_w**2+2*J_w*M_b*R_b**3*R_w+J_w*M_b*R_b**4),0],[0,((J_b*M_b*R_w**3+J_b*M_b*R_b*R_w**2+J_w*M_b*R_b**2*R_w+J_w*M_b*R_b**3)*g)/(J_b*M_b*R_w**4+2*J_b*M_b*R_b*R_w**3+((J_w+J_b)*M_b*R_b**2+J_b*J_w)*R_w**2+2*J_w*M_b*R_b**3*R_w+J_w*M_b*R_b**4),-(J_b*R_w**2*d_w)/(J_b*M_b*R_w**4+2*J_b*M_b*R_b*R_w**3+((J_w+J_b)*M_b*R_b**2+J_b*J_w)*R_w**2+2*J_w*M_b*R_b**3*R_w+J_w*M_b*R_b**4),0]]

B = [[0],[0],[((M_b*R_b**2+J_b)*R_w**2+2*M_b*R_b**3*R_w+M_b*R_b**4)/(J_b*M_b*R_w**4+2*J_b*M_b*R_b*R_w**3+((J_w+J_b)*M_b*R_b**2+J_b*J_w)*R_w**2+2*J_w*M_b*R_b**3*R_w+J_w*M_b*R_b**4)],[(J_b*R_w**2)/(J_b*M_b*R_w**4+2*J_b*M_b*R_b*R_w**3+((J_w+J_b)*M_b*R_b**2+J_b*J_w)*R_w**2+2*J_w*M_b*R_b**3*R_w+J_w*M_b*R_b**4)]]

B= Kt*mat(B)

C = [[1, 0, 0, 0], [0, 1, 0, 0]]
C2 = mat([[0, 1, 0, 0]])
D = [[0],[0]] 

# Plant continous and discrete
# input Motor current
# output Wheel angle and Angle between Wheel CM and Ball CM

bow = ss(A,B,C,D)

Ts=0.01                         # Sampling time
bowD = c2d(bow,Ts,'zoh')        # Get discrete state space form
# Control system design
# State feedback with integral part
wn = 2
xi1 = np.sqrt(2)/2
xi2 = np.sqrt(3)/2
cl_p1 = [1,2*xi1*wn,wn**2]
cl_p2 = [1,2*xi2*wn,wn**2]
cl_p3 = [1, wn]

cl_poly = sp.polymul(cl_p1, cl_p2)
cl_polyf = sp.polymul(cl_poly, cl_p3)

cl_poles = sp.roots(cl_poly);    # Desired continous poles
cl_polesf = sp.roots(cl_polyf);    # Desired continous poles

cl_polesd = sp.exp(cl_poles*Ts)  # Desired discrete poles
cl_polesfd = sp.exp(cl_polesf*Ts)  # Desired discrete poles

# Choose Controller
#
# 1 - State feedback
# 2 - LQR controller

Controller = 2
Phi = bowD.A
G   = bowD.B

obs_poles = sp.roots(cl_p1)
p_od = sp.exp(obs_poles*Ts);

if Controller == 1:
    # Controller without integral part
    k = place(Phi,G,cl_polesd)

elif Controller == 2:
    # LQR Controller
    Q = np.diag([30,30,1,1]);
    R = [1];                    
    k, S, E = dlqr(Phi,G,Q,R)
    
# Observer design parameters
##############################################################################
# Control design - Reduced order observer
(preg,pvect) = sp.linalg.eig(A-B*k)
rho=max(abs(preg));       # process spectral radius
rhoamp=10;                # amplification of observer poles

angle1 = 15*1j*np.pi/16
poles_c = rhoamp*rho*sp.exp([angle1, -angle1])
obs_poles = sp.exp(poles_c*Ts)

T=[[0,0,1,0],[0,0,0,1]]
obs=red_obs(bowD,T,[obs_poles])

# Put Observer and controller together (compact form)
ctr = comp_form(bowD,obs,k)
    
# A/D filtering
wnf = 5
g = tf(wnf,[1,wnf])
gz = c2d(g,Ts)

# Real Plant constants
Sat = 3300
D0 = 2.5967

Kd = 0.35/10
D2PHI = Kd/(R_b+R_w)
KPHIW = 1/Krapp



