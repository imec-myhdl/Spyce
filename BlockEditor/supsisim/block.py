import sys, os
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

from pyqt45  import QGraphicsPathItem, QGraphicsTextItem, QPainterPath, \
                    QPen, QImage, QtCore, QTransform, set_orient


from supsisim.port import Port, InPort, OutPort
from supsisim.const import GRID, PW, LW, BWmin, BHmin, PD, respath

from lxml import etree

class Block(QGraphicsPathItem):
    """A block holds ports that can be connected to."""
    def __init__(self, *args, **kwargs):
        if len(args) >= 2:
            parent, self.scene = args[0], args[1]
        elif len(args) == 1:
            parent, self.scene = args[0], None
        else:
            parent, self.scene = None, None
        if QtCore.qVersion().startswith('5'):
            super(Block, self).__init__(parent)
            if self.scene:
                self.scene.addItem(self)
        else:
            super(Block, self).__init__(parent, self.scene)
        if len(args) == 9:
            parent, self.scene, self.name, self.inp, self.outp, self.iosetble, self.icon, self.params, self.flip = args
        elif len(args) == 3:
            parent, self.scene, strBlk = args
            ln = strBlk.split('@')
            self.name   = str(ln[0])
            self.inp    = int(ln[1])
            self.outp   = int(ln[2])
            self.icon   = str(ln[4])
            self.params = str(ln[5])
            self.flip   = False
            io          = int(ln[3])
            iosetble = (io==1)
            self.iosetble = iosetble
        elif len(args) <= 2:
            self.name     = kwargs.pop('name')     if 'name' in kwargs else ''
            self.inp      = kwargs.pop('inp')      if 'inp' in kwargs else 0
            self.outp     = kwargs.pop('outp')     if 'outp' in kwargs else 0
            self.icon     = kwargs.pop('icon')     if 'icon' in kwargs else ''
            self.params   = kwargs.pop('params')   if 'params' in kwargs else ''
            self.flip     = kwargs.pop('flip')     if 'flip' in kwargs else False
            self.iosetble = kwargs.pop('iosetble') if 'iosetble' in kwargs else False
            x             = float(kwargs.pop('x')) if 'x' in kwargs else 0.0
            y             = float(kwargs.pop('y')) if 'y' in kwargs else 0.0
            self.setPos(x, y)
            self.flip     = kwargs.pop('flip')     if 'flip' in kwargs else False
#            self.__dict__.update(kwargs) # update the block attributes, maybe a bit dangerous
        else:
            raise ValueError('Needs 9 or 3 arguments; received %i.' % len(args))
        
        self.line_color = QtCore.Qt.black
        self.fill_color = QtCore.Qt.black
        if self.scene:
            self.setup()
        
    def __str__(self):
        txt  = 'Name         :' + self.name.__str__() +'\n'
        txt += 'Input ports  :' + self.inp.__str__() + '\n'
        txt += 'Output ports :' + self.outp.__str__() + '\n'
        txt += 'Icon         :' + self.icon.__str__() + '\n'
        txt += 'Params       :' + self.params.__str__() + '\n'
        for thing in self.childItems():
            print(thing)
        return txt
        
    def __repr__(self):
        fmt = 'Block(None, scene, {kwargs})'
        kwargs = []
        x, y, flip = int(self.x()), int(self.y()), self.flip        
        if x:
            kwargs.append('x={}'.format(x))
        if y:
            kwargs.append('y={}'.format(y))
        if flip:
            kwargs.append('flip=True')
        for k in 'name inp outp iosetble icon params'.split():
            v = self.__dict__[k]
            if v:
                kwargs.append('{}={}'.format(k, repr(v)))

        return fmt.format(kwargs=', '.join(kwargs))
        
    def setup(self):
        self.ports_in = []
        self.name = self.scene.setUniqueName(self)
        Nports = max(self.inp, self.outp)
        self.w = BWmin
        self.h = BHmin+PD*(max(Nports-1,0))

        p = QPainterPath()
        
        p.addRect(-self.w/2, -self.h/2, self.w, self.h)

        self.setPath(p)

        self.port_in = []
        for n in range(0,self.inp):
            self.add_inPort(n)
        for n in range(0,self.outp):
            self.add_outPort(n)

#        set_orient(self, flip=True)
#        self.setTransform(QTransform.fromScale((1-2*self.flip),1))
#            set_orient(self.label, flip=True)
#            w = self.label.boundingRect().width()
#            self.label.setTransform(QTransform.fromTranslate(-w,0))        

        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(self.name)
        w = self.label.boundingRect().width()
        self.label.setPos(-w/2, self.h/2+5)
        if self.flip:
            self.setTransform(QTransform.fromScale(-1,1))
#            self.label.setTransform(QTransform.fromScale(1,1), False)
        self.setTransform(QTransform.fromTranslate(0,0))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        
    def add_inPort(self, n):
        pos = -PD*(self.inp-1)/2
        port = InPort(self, self.scene)
        port.block = self
        xpos = -(self.w+PW)/2
        port.setPos(xpos, pos+n*PD)
        return port

    def add_outPort(self, n):
        pos = -PD*(self.outp-1)/2
        port = OutPort(self, self.scene)
        port.block = self
        xpos = (self.w+PW)/2
        port.setPos(xpos, pos+n*PD)
        return port

    def ports(self):
        ports = []
        for thing in self.childItems():
            if isinstance(thing, Port):
                ports.append(thing)
        return ports

    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setBrush(self.line_color)
        pen.setWidth = LW
        if self.isSelected():
            pen.setStyle(QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawPath(self.path())
        img = QImage(os.path.join(respath, 'blocks' , self.icon + '.svg'))
        if self.flip:
            img = img.mirrored(True, False)
        rect = img.rect()
        painter.drawImage(-rect.width()/2,-rect.height()/2,img)

    def itemChange(self, change, value):
        return value

    def remove(self):
        self.scene.nameList.remove(self.name)
        for thing in self.childItems():
            try:
                thing.remove()
            except:
                pass
        self.scene.removeItem(self)

    def setPos(self, *args):
        if len(args) == 1:
            pt = self.gridPos(args[0])
            super(Block, self).setPos(pt)
        else:
            pt = QtCore.QPointF(args[0],args[1])
            pt = self.gridPos(pt)
            super(Block, self).setPos(pt)
        
    def gridPos(self, pt):
         gr = GRID
         x = gr * ((pt.x() + gr /2) // gr)
         y = gr * ((pt.y() + gr /2) // gr)
         return QtCore.QPointF(x,y)

    def clone(self, pt):
        b = Block(None, self.scene, self.name, self.inp, self.outp,
                      self.iosetble, self.icon, self.params,  self.flip)
        b.setPos(self.scenePos().__add__(pt))
       
    def save(self, root):
        blk = etree.SubElement(root,'block')
        etree.SubElement(blk,'name').text = self.name
        etree.SubElement(blk,'inp').text = self.inp.__str__()
        etree.SubElement(blk,'outp').text = self.outp.__str__()
        if self.iosetble:
            etree.SubElement(blk,'ioset').text = '1'
        else:
            etree.SubElement(blk,'ioset').text = '0'
        etree.SubElement(blk,'icon').text = self.icon
        etree.SubElement(blk,'params').text = self.params
        if self.flip:
            etree.SubElement(blk,'flip').text = '1'
        else:
            etree.SubElement(blk,'flip').text = '0'
        etree.SubElement(blk,'posX').text = self.pos().x().__str__()
        etree.SubElement(blk,'posY').text = self.pos().y().__str__()

