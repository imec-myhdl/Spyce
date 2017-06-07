import numpy as np
import scipy.signal as sg
import scipy.interpolate as intp
import matplotlib.pyplot as plt
import cv2

def gen_gauss(N):
    sigma = float(N)/3
    x = np.arange(-N,N+1)
    y = 1/np.sqrt(2*np.pi*sigma**2)*np.exp(-x**2/(2*sigma**2));
    y = y/sum(y);
    return y

TimeFactor = 5
XSize = 0.3
YSize = 0.2

#fname = 'contour.png'
#fname = 'fiore.png'
fname = raw_input('Filename: ')

im = cv2.imread(fname)
plt.imshow(im);
plt.show()

Xpt = np.shape(im)[1]
Ypt = np.shape(im)[0]

imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(imgray,127,255,0)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

N=len(contours)
for n in np.arange(0,N):
    cnt = contours[n]
    print len(cnt)
    print np.shape(cnt)

cv2.drawContours(im,contours[1],-1,(0,255,0),3)

plt.imshow(im)
plt.show()

cnt = contours[1]
data = cnt[:][:,0]
x=data[:,0]
y=data[:,1]
#plt.plot(x,y)
#plt.show()

x = np.hstack((x,x[0]))
y = np.hstack((y,y[0]))

base = np.linspace(0,len(x),len(x))
basen = np.linspace(0,len(x),2000)

fx = intp.interp1d(base,x,kind='cubic')
fy = intp.interp1d(base,y,kind='cubic')
#fx = intp.interp1d(base,x)
#fy = intp.interp1d(base,y)

xn = fx(basen)
yn = fy(basen)
#xn = xn[0:-1]
#yn = yn[0:-1]

xn = XSize*xn/Xpt-XSize/2
yn = -1.0*(YSize*yn/Ypt-YSize/2)

plt.plot(xn,yn)
plt.axis([-0.15,0.15,-0.10,0.10])
plt.show()

np.savetxt('dataX.dat',xn)
np.savetxt('dataY.dat',yn)


