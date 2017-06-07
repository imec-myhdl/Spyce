import numpy as np

A=1
t = np.linspace(0,2*np.pi,1000,endpoint=False)
x = A*np.sin(t)
y = A*np.cos(t)
np.savetxt('cerchioX.dat',x)
np.savetxt('cerchioY.dat',y)
