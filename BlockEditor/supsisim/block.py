import sys, os, ast
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

#import sip

from pyqt45  import QGraphicsPathItem, QGraphicsTextItem, QPainterPath, \
                    QPen, QImage, QtCore, QTransform, QApplication


from supsisim.port import Port, InPort, OutPort
from supsisim.const import GRID, PW, LW, BWmin, BHmin, PD, respath

from lxml import etree
import tempfile


    

class Block(QGraphicsPathItem):
    """A block holds ports that can be connected to."""
    def __init__(self, *args, **kwargs):
        if len(args) >= 2:
            parent, self.scene = args[0], args[1]
        elif len(args) == 1:
            parent, self.scene = None, args[0]
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
            self.inp    = ast.literal_eval(ln[1]) # ast.literal_eval is a lot safer than 'eval'
            self.outp   = ast.literal_eval(ln[2])
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
            
    def from_txt(s):
        '''convert text to int or list'''
        
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
        return self.toPython()
        
    def toPython(self, lib=False):
        fmt = 'Block({kwargs})'
        fields = 'name inp outp iosetble icon params'.split()
        kwargs = []
        x, y, flip = int(self.x()), int(self.y()), self.flip
        if not lib: # add x, y, flip for schematic(diagrams)
            if x:
                fields.append('x')
            if y:
                fields.append('y')
            if flip:
                fields.append('flip')
        for k in fields:
            v = self.__dict__[k]
            if v:
                kwargs.append('{}={}'.format(k, repr(v)))

        return fmt.format(kwargs=', '.join(kwargs))
        
    def setup(self):
        self.ports_in = []
        self.name = self.scene.setUniqueName(self)
        Ni = self.inp if isinstance(self.inp, int) else len(self.inp)
        No = self.outp if isinstance(self.outp, int) else len(self.outp)
        Nports = max(Ni, No)
        self.w = BWmin
        self.h = BHmin+PD*(max(Nports-1,0))

        p = QPainterPath()
        
        p.addRect(-self.w/2, -self.h/2, self.w, self.h)

        self.setPath(p)

        if isinstance(self.inp, int):
            for n in range(0,self.inp): # legacy: self.inp is integer number
                self.add_inPort(n)
        else:
            for n in self.inp: # new: self.inp is list of tuples (x,y)
                self.add_inPort(n)

        if isinstance(self.outp, int):
            for n in range(0,self.outp):# legacy: self.out = integer number
                self.add_outPort(n)
        else:
            for n in self.outp: # new: self.outp is list of tuples (x,y)
                self.add_outPort(n)

        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(self.name)
        w = self.label.boundingRect().width()
        if self.flip:
            self.setTransform(QTransform.fromScale(-1,1))
            self.label.setTransform(QTransform.fromScale(-1,1))
            self.label.setPos(w/2, self.h/2+5)
        else:
            self.label.setPos(-w/2, self.h/2+5)

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        
        svgfilename = os.path.join(respath, 'blocks' , self.icon + '.svg')
        self.img = QImage(svgfilename)
        f = self.create_svg_mirror_txt(svgfilename)
        self.img_flippedtext = QImage(f)

        
    def add_inPort(self, n):
        if isinstance(n, int):
            ypos = -PD*(self.inp-1)/2 + n*PD
            xpos = -(self.w+PW)/2
            name = 'i_pin{}'.format(n)
        else: # tuple (x, y)
            xpos, ypos, name = n
        port = InPort(self, self.scene, name=name)
        port.block = self
        port.setPos(xpos, ypos)
        return port

    def add_outPort(self, n):
        if isinstance(n, int):
            xpos = (self.w+PW)/2
            ypos = -PD*(self.outp-1)/2 + n*PD
            name = 'o_pin{}'.format(n)
        else: # tuple (x, y)
            xpos, ypos, name = n
        port = OutPort(self, self.scene, name=name)
        port.block = self
        port.setPos(xpos, ypos)
        return port

    def ports(self):
        ports = []
        for thing in self.childItems():
            if isinstance(thing, Port):
                ports.append(thing)
        return ports
        
    def pins(self):
        '''return (inputs, outputs, inouts) that lists of tuples (io, x, y, name)'''
        inputs, outputs, inouts  = [], [], []
        ports = self.ports()
        for p in ports:
            x, y = p.x(), p.y()
            name = p.name
            if isinstance(p, InPort):
                 inputs.append(('i', x, y, name))
            elif isinstance(p, OutPort):
                outputs.append(('o', x, y, name))
            else:
                inouts.append(('io', x, y, name))
        return inputs, outputs, inouts


    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setBrush(self.line_color)
        pen.setWidth = LW
        if self.isSelected():
            pen.setStyle(QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawPath(self.path())
        if self.flip:
            img = self.img_flippedtext
#            img = img.mirrored(True, False)
        else:
            img = self.img
        rect = img.rect()
        painter.drawImage(-rect.width()/2,-rect.height()/2, img)

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

    def create_svg_mirror_txt(self, svgfilename):
        #generate an svg flie that has text-labels flipped
        dirpath, fname = os.path.split(svgfilename)
        svgflipped = os.path.join(dirpath, 'flipped', fname)
#        if os.path.exists(svgflipped):
#            return svgflipped
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(svgfilename, parser)
        root = tree.getroot()
        svg_namespace = root.nsmap[None]
        svg_path = '{{{}}}'.format(svg_namespace)
    #    texts = [dom2dict(el) for el in doc.getElementsByTagName('text')]
        texts = root.findall(svg_path+'text')
        for e in texts:
            ff = 'x y text-anchor style'.split()
            rr = []
            for k in ff:
                try:
                    v = e.attrib[k]
                    del e.attrib[k]
                except KeyError:
                    v = '0'
                rr.append(v)
            x, y, anchor, style = rr
            
            

            if style != '0':
                ix = -1
                styleelmnts = style.split(';')
                if 'text-anchor' in style:
                     for ix, se in enumerate(styleelmnts):
                        k, summy, v = se.partition(':')
                        if k == 'text-anchor':
                            anchor = v
                            styleelmnts.pop(ix)
                            break

            if anchor in ['0', 'start'] :
                anchor = 'end'
            elif anchor == 'end':
                anchor = ''

            if anchor:
                if style != '0':
                    styleelmnts.append('text-anchor:'+anchor)
                    e.attrib['style'] = ';'.join(styleelmnts)
                else:
                    e.attrib['text-anchor'] = anchor

            e.attrib['transform'] = 'translate({},{})scale(-1,1)'.format(x, y)

        tree.write(svgflipped, pretty_print=True)
        return svgflipped



