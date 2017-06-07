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

# Constants
gp = 9.81;

# Ball
Mb = 0.106712
Rb = 0.105/2
Jb = 2.0/3*Mb*Rb**2

# Gears
Rm = 0.0273/2   # On motor
Rw = 0.0753/2   # On wheel
Krapp = 333.599109/(2*np.pi*20)

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
#show()

# Design Controller
a=[[0,1],[0,-D]]
b=[[0],[K]]
c=[[1,0]];
d=[0];

sysc=ss(a,b,c,d)                # Continous state space form

Ts=0.01                         # Sampling time
sys = c2d(sysc,Ts,'zoh')        # Get discrete state space form

# Control system design
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
# Wheel
Jw = Kt/K
Dw = D*Jw
Rw = 0.285

from sympy import symbols, Matrix, pi
from sympy.physics.mechanics import *
import numpy as np

ph0, ph1, ph2 = dynamicsymbols('ph0 ph1 ph2')
w0, w1, w2 = dynamicsymbols('w0 w1 w2')

T = dynamicsymbols('T')

J1, J2 = symbols('J1 J2')
M1, M2 = symbols('M1 M2')
R1, R2 = symbols('R1 R2')
d1     = symbols('d1')
g      = symbols('g')
t      = symbols('t')

N = ReferenceFrame('N')

O = Point('O')
O.set_vel(N,0)

ph2 = ((R1+R2)*ph0-R1*ph1)/R2

N0 = N.orientnew('N0','Axis',[ph0,N.z])
N1 = N.orientnew('N1','Axis',[ph1,N.z])
N2 = N.orientnew('N2','Axis',[ph2,N.z])
N1.set_ang_vel(N,w1*N.z)
N2.set_ang_vel(N,w2*N.z)

CM2 = O.locatenew('CM2',(R1+R2)*N0.y)
CM2.v2pt_theory(O,N,N0)

Iz = outer(N.z,N.z)
In1T = (J1*Iz, O)
In2T = (J2*Iz, CM2)

B1 = RigidBody('B1', O, N1, M1, In1T)
B2 = RigidBody('B2', CM2, N2, M2, In2T)

forces = [(N1, (T-d1*w1)*N.z), (CM2,-M2*g*N.y)]
#forces = [(N1, T*N.z), (CM2,-M2*g*N.y)]

kindiffs = [ph1.diff(t)-w1,ph0.diff(t)-w0]

KM = KanesMethod(N,q_ind=[ph1, ph0],u_ind=[w1, w0],kd_eqs=kindiffs)
fr, frstar = KM.kanes_equations(forces,[B1, B2])

# Equilibrium point
eq_pt = [0, 0, 0, 0, 0]
eq_dict = dict(zip([ph1,ph0,w1,w0, T], eq_pt))

R1p = Rw
R2p = Rb
M2p = Mb
J1p = Jw
J2p = Jb
d1p = Dw

pars = [R1, R2, M2, J1, J2, d1, g]
par_vals =  [R1p, R2p, M2p, J1p, J2p, d1p, gp]
par_dict = dict(zip(pars, par_vals))

dynamic = [ph1, ph2, w1, w2, T]
kindiff_dict = KM.kindiffdict()

M = KM.mass_matrix_full
F = KM.forcing_full

# Linearize the system for control design

# symbolically linearize about arbitrary equilibrium
M, linear_state_matrix, linear_input_matrix, inputs = KM.linearize(new_method=True)

# sub in the equilibrium point and the parameters
f_A_lin = linear_state_matrix.subs(eq_dict)
f_B_lin = linear_input_matrix.subs(eq_dict)

# compute A and B
Atmp = M.inv() * f_A_lin
Btmp = M.inv() * f_B_lin

Atmp = Atmp.subs(par_dict)
Btmp = Btmp.subs(par_dict)

A = np.matrix(Atmp)
B = np.matrix(Btmp)

A = A.astype('float64')
B = Kt*B.astype('float64')
C = [[1, 0, 0, 0], [0, 1, 0, 0]]
D = [[0],[0]] 

