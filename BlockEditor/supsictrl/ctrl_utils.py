"""
This is a procedural interface to the ctrl_utils library

roberto.bucher@supsi.ch

The following commands are provided:

Design and plot commands
  full_obs    - full order observer
  red_obs     - reduced order observer
  comp_form   - state feedback controller+observer in compact form
  comp_form_i - state feedback controller+observer+integ in compact form
  set_aw      - introduce anti-windup into controller
  grstep      - graphical step response
"""
from __future__ import print_function

from numpy import hstack, vstack, imag, zeros, eye, mat, shape
from scipy import poly 
from scipy.linalg import inv, eigvals
import matplotlib.pyplot as plt
from control import *
from supsictrl.ctrl_repl import place

def full_obs(sys,poles):
    """Full order observer of the system sys

    Call:
    obs=full_obs(sys,poles)

    Parameters
    ----------
    sys : System in State Space form
    poles: desired observer poles

    Returns
    -------
    obs: ss
    Observer

    """
    if isinstance(sys, TransferFunction):
        "System must be in state space form"
        return
    a=mat(sys.A)
    b=mat(sys.B)
    c=mat(sys.C)
    d=mat(sys.D)
    L=place(a.T,c.T,poles)
    L=mat(L).T
    Ao=a-L*c
    Bo=hstack((b-L*d,L))
    n=shape(Ao)
    m=shape(Bo)
    Co=eye(n[0],n[1])
    Do=zeros((n[0],m[1]))
    obs=StateSpace(Ao,Bo,Co,Do,sys.dt)
    return obs

def red_obs(sys,T,poles):
    """Reduced order observer of the system sys

    Call:
    obs=red_obs(sys,T,poles)

    Parameters
    ----------
    sys : System in State Space form
    T: Complement matrix
    poles: desired observer poles

    Returns
    -------
    obs: ss
    Reduced order Observer

    """
    if isinstance(sys, TransferFunction):
        "System must be in state space form"
        return
    a=mat(sys.A)
    b=mat(sys.B)
    c=mat(sys.C)
    d=mat(sys.D)
    T=mat(T)
    P=mat(vstack((c,T)))
    invP=inv(P)
    AA=P*a*invP
    ny=shape(c)[0]
    nx=shape(a)[0]
    nu=shape(b)[1]

    A11=AA[0:ny,0:ny]
    A12=AA[0:ny,ny:nx]
    A21=AA[ny:nx,0:ny]
    A22=AA[ny:nx,ny:nx]

    L1=place(A22.T,A12.T,poles)
    L1=mat(L1).T

    nn=nx-ny

    tmp1=mat(hstack((-L1,eye(nn,nn))))
    tmp2=mat(vstack((zeros((ny,nn)),eye(nn,nn))))
    Ar=tmp1*P*a*invP*tmp2
 
    tmp3=vstack((eye(ny,ny),L1))
    tmp3=mat(hstack((P*b,P*a*invP*tmp3)))
    tmp4=hstack((eye(nu,nu),zeros((nu,ny))))
    tmp5=hstack((-d,eye(ny,ny)))
    tmp4=mat(vstack((tmp4,tmp5)))

    Br=tmp1*tmp3*tmp4

    Cr=invP*tmp2

    tmp5=hstack((zeros((ny,nu)),eye(ny,ny)))
    tmp6=hstack((zeros((nn,nu)),L1))
    tmp5=mat(vstack((tmp5,tmp6)))
    Dr=invP*tmp5*tmp4
    
    obs=StateSpace(Ar,Br,Cr,Dr,sys.dt)
    return obs

def comp_form(sys,obs,K):
    """Compact form Conroller+Observer

    Call:
    contr=comp_form(sys,obs,K)

    Parameters
    ----------
    sys : System in State Space form
    obs : Observer in State Space form
    K: State feedback gains

    Returns
    -------
    contr: ss
    Controller

    """
    nx=shape(sys.A)[0]
    ny=shape(sys.C)[0]
    nu=shape(sys.B)[1]
    no=shape(obs.A)[0]

    Bu=mat(obs.B[:,0:nu])
    By=mat(obs.B[:,nu:])
    Du=mat(obs.D[:,0:nu])
    Dy=mat(obs.D[:,nu:])

    X=inv(eye(nu,nu)+K*Du)

    Ac = mat(obs.A)-Bu*X*K*mat(obs.C);
    Bc = hstack((Bu*X,By-Bu*X*K*Dy))
    Cc = -X*K*mat(obs.C);
    Dc = hstack((X,-X*K*Dy))
    contr = StateSpace(Ac,Bc,Cc,Dc,sys.dt)
    return contr

def comp_form_i(sys,obs,K,Cy=[[1]]):
    """Compact form Conroller+Observer+Integral part
    Only for discrete systems!!!

    Call:
    contr=comp_form_i(sys,obs,K [,Cy])

    Parameters
    ----------
    sys : System in State Space form
    obs : Observer in State Space form
    K: State feedback gains
    Cy: feedback matric to choose the output for integral part

    Returns
    -------
    contr: ss
    Controller

    """
    if sys.dt==None:
        print('contr_form_i works only with discrete systems!')
        return
    
    Ts = sys.dt
    ny=shape(sys.C)[0]
    nu=shape(sys.B)[1]
    nx=shape(sys.A)[0]
    no=shape(obs.A)[0]
    ni=shape(mat(Cy))[0]

    B_obsu = mat(obs.B[:,0:nu])
    B_obsy = mat(obs.B[:,nu:nu+ny])
    D_obsu = mat(obs.D[:,0:nu])
    D_obsy = mat(obs.D[:,nu:nu+ny])

    k=mat(K)
    nk=shape(k)[1]
    Ke=k[:,nk-ni:]
    K=k[:,0:nk-ni]
    X = inv(eye(nu,nu)+K*D_obsu);

    a=mat(obs.A)
    c=mat(obs.C)
    Cy=mat(Cy)

    tmp1=hstack((a-B_obsu*X*K*c,-B_obsu*X*Ke))

    tmp2=hstack((zeros((ni,no)),eye(ni,ni)))
    A_ctr=vstack((tmp1,tmp2))

    tmp1=hstack((zeros((no,ni)),-B_obsu*X*K*D_obsy+B_obsy))
    tmp2=hstack((eye(ni,ni)*Ts,-Cy*Ts))
    B_ctr=vstack((tmp1,tmp2))

    C_ctr=hstack((-X*K*c,-X*Ke))
    D_ctr=hstack((zeros((nu,ni)),-X*K*D_obsy))

    contr=StateSpace(A_ctr,B_ctr,C_ctr,D_ctr,sys.dt)
    return contr
    
def set_aw(sys,poles):
    """Divide in controller in input and feedback part
       for anti-windup

    Usage
    =====
    [sys_in,sys_fbk]=set_aw(sys,poles)

    Inputs
    ------

    sys: controller
    poles : poles for the anti-windup filter

    Outputs
    -------
    sys_in, sys_fbk: controller in input and feedback part
    """
    sys = ss(sys)
    Ts = sys.dt
    den_old=poly(eigvals(sys.A))
    sys=tf(sys)
    den = poly(poles)
    tmp= tf(den_old,den,sys.dt)
    sys_in=tmp*sys
    sys_in = sys_in.minreal()
    sys_in = ss(sys_in)
    sys_fbk=1-tmp
    sys_fbk = sys_fbk.minreal()
    sys_fbk = ss(sys_fbk)
    return sys_in, sys_fbk

def grstep(sys):
    t, y = step_response(sys)
    plt.plot(t,y),plt.grid()

    

