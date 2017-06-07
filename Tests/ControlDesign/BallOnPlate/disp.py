import numpy as np
import matplotlib.pyplot as plt
from os import system

xx=np.loadtxt('x.x')
t=xx[:,0]
xref=xx[:,1]
x=xx[:,2]
yref=xx[:,3]
y=xx[:,4]
plt.plot(xref,yref,x,y)
plt.show()
system('rm x.x')


