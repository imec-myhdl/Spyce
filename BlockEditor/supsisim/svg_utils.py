# -*- coding: utf-8 -*-
"""
scalable vector graphics utilities


createSvgIcon
    create a (new) icon file
    returns svgwriter object (file is already created)

createSvgMirrorTxt
    read an svg and reverse all text labels (flip horizontal)
    returns string
    
scrubSvgLabels
    read an remove all pin-labels from an svg file (in place)
    returns None
    
    
"""

import os, tempfile, subprocess
import svgwrite
from lxml import etree
from collections import OrderedDict

from libraries import libroot

from supsisim.const import icon_font_size, icon_pin_size, PW, icon_cache_dir, respath
#from supsisim.port import isInPort, isOutPort, isInoutPort
#from supsisim.block import calcBboxFromPins

def svg2png(svgfilename):
    svgfilename = os.path.abspath(svgfilename)
    if svgfilename.startswith(libroot):
        pngfilename = svgfilename[len(libroot)+1:]
    elif svgfilename.startswith(respath):
        pngfilename = svgfilename[len(respath)+1:]
    else:
        pngfilename = svgfilename
    pngfilename = os.path.join(icon_cache_dir, pngfilename.rstrip('.svg') + '.png')
    dirname, fname = os.path.split(pngfilename)
#    print ('    svg:',svgfilename)
#    print ('    png:',pngfilename)
    if not os.path.exists(svgfilename): # no svg
        return False
    pngmirrorfile = pngfilename.rstrip('.png') + 'flip.png'
    timestamp0 = os.stat(svgfilename).st_mtime
    
    if  os.path.isfile(pngfilename)  and os.stat(pngfilename).st_mtime > timestamp0:
        return pngfilename, pngmirrorfile
    
    # (re)create if svg newer than png
    # create pngfilename
    dirname, fname = os.path.split(pngfilename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname) # make directory path (if not alrady present)
    print('generating png image', pngfilename)
    subprocess.call('inkscape -z {} -e {}'.format(svgfilename, pngfilename).split())
    # also create mirror
    fo = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
    fo.write(createSvgMirrorTxt(svgfilename))
    svgmirrorfile = fo.name
    fo.close()
    print('generating png image', pngmirrorfile)
    subprocess.call('inkscape -z {} -e {}'.format(svgmirrorfile, pngmirrorfile).split())
    os.remove(svgmirrorfile)
    return pngfilename, pngmirrorfile

def createSvgMirrorTxt(svgfilename):
    '''generate an svg flie that has text-labels flipped'''
    dirpath, fname = os.path.split(svgfilename)
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svgfilename, parser)
    root = tree.getroot()
    svg_namespace = root.nsmap[None]
    svg_path = '{{{}}}'.format(svg_namespace)
#    texts = [dom2dict(el) for el in doc.getElementsByTagName('text')]
    texts = root.findall(svg_path+'text')
    for e in texts:
        ff = 'x y style transform'.split()
        rr = []
        for k in ff:
            try:
                v = e.attrib[k]
            except KeyError:
                v = '0'
            rr.append(v)
        x, y, style, transform = rr
        x = float(x)
        if int(x) == x:
            x = int(x)
        y = float(y)
        if int(y) == y:
            y = int(y)

        if style != '0':
            st = OrderedDict()
            for elmt in style.split(';'):
                key,_,val = elmt.partition(':')
                st[key]=val
            if 'text-anchor' in st:
                if st['text-anchor'] == 'end':
                    st['text-anchor'] == 'start'
                elif st['text-anchor'] == 'start':
                    st['text-anchor'] == 'end'
                #else middle -> unchanged (dont know what to do with inherit)
            else:
                st['text-anchor'] = 'end'
            style = [k+':'+vv for k,vv in st.items()]
            e.attrib['style'] = ';'.join(style)
        else:
            e.attrib['style'] = 'text-anchor:end'
            
        
        if transform != '0':
            m = [-1,0,0,1,0,0] # a,b,c,d,e,f newx = ax +cy + e, newy = bx + dy + f
            for tf in transform.split():
                tp,_,rest = tf.rstrip(')').partition('(')
                ops = [float(elmt) for elmt in rest.split(',')]
                if tp.lower() == 'matrix':
                    m = ops
                else:
                    if tp.lower() == 'scale':
                        if len(ops) == 1:
                            sx = -ops[0]
                            sy = ops[0]
                        else:
                            sx, sy = ops[0], ops[1]
                        m[0] *= sx # mirror
                        m[3] *= sy
                    elif tp.lower() == 'translate':
                        if len(ops) == 1:
                            dx = ops[0] # flip X not needed
                            dy = ops[0]
                        else:
                            dx, dy = ops[0], ops[1] # flip X not needed
                        m[4] += dx # flip side
                        m[5] += dy
                        
                    else: # unsupported skewX, skewY, rotate 
                    # see https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform
                        m = [-1,0,0,1,0,0]
                    break
            e.attrib['transform'] = 'matrix({},{},{},{},{},{})'.format(*m)
        else:
            e.attrib['transform'] = 'scale(-1,1)'
        
                    
        e.attrib['x'] = str(-x)
 
    svgflipped = etree.tostring(root, pretty_print=True)
    return svgflipped


def updateSvg(block, svgfilename, makeports=True):
    '''update the bbox (and pins + labels when makeports=True) '''
    checkAndCreateSvgIcon(block, svgfilename)
        
    parser = etree.XMLParser(remove_blank_text=True)
    tree =  etree.parse(svgfilename, parser)
    root = tree.getroot()

    left, top, w, h = block.bbox if block.bbox else block.calcBboxFromPins()
    right, bottom = left + w, top + h
    midx, midy = (left + right)/2, (top+bottom)/2
    
    # check if grid is present, and if not: insert
    namedview = root.find('{*}namedview')
    nv = etree.Element('{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview')
    nv.set('gridtolerance', '10000')
    nv.set('guidetolerance', '10')
    nv.set('{http://www.inkscape.org/namespaces/inkscape}current-layer', "svg2")
    nv.set('{http://www.inkscape.org/namespaces/inkscape}snap-grids', "true")
    nv.set('{http://www.inkscape.org/namespaces/inkscape}window-height', str(h + 2*icon_pin_size))
    nv.set('{http://www.inkscape.org/namespaces/inkscape}window-width', str(w + 2*icon_pin_size))
    nv.set('objecttolerance', '10')
    nv.set('showgrid', "true")
    
    grid = etree.Element('{http://www.inkscape.org/namespaces/inkscape}grid')
    grid.set('spacingx',"10")
    grid.set('spacingy',"10")
    grid.set('type', "xygrid")
    grid.set('units', "px")
    nv.append(grid)
    if namedview is not None:
        root.replace(namedview, nv)
    else:
        root.insert(0, nv)

    # remove old bbox (if present)

    g =  etree.Element('g')
    g.set('id', 'tmp_bbox')



    if makeports: # 
        # create bbox
        r = etree.Element('rect')    
        r.set('id', 'bbox')
        r.set('fill', 'none')
        r.set('stroke-width', '1')
        r.set('stroke', 'darkGreen')
        r.set('height', '{:.1f}'.format(h))
        r.set('width', '{:.1f}'.format(w-PW))
        r.set('x', '{:.1f}'.format(icon_pin_size+PW/2))
        r.set('y', '{:.1f}'.format(icon_pin_size))
        g.append(r)
        ports = block.ports()
        for p_ix, p in enumerate(ports):
            tp = p.porttype
            x, y = p.pos().x(), p.pos().y()
            x += icon_pin_size - left + midx
            y += icon_pin_size - top  + midy
    
            if p.label: # pin with label
                name = p.label.text()
                dd = OrderedDict(id='{}-port_{}'.format(tp, name))
                dd['font-size'] = '{}px'.format(icon_font_size)
      
                if p.label_side == 'left':
                    dd['text-anchor']='end'
                    tx, ty = x - icon_font_size*0.35 - PW/2 , y + icon_font_size*0.35
                elif p.label_side == 'right':
                    tx, ty = x + icon_font_size*0.35 + PW/2, y + icon_font_size*0.35
                else: # TODO: add top/bottom
                    raise Exception('not yet implemented' + p.label_side)
    
                dd['x'] = '{:.2f}'.format(tx)
                dd['y'] = '{:.2f}'.format(ty)
                   
                elmt = etree.Element("text", **dd)
                elmt.text = name
                g.append(elmt)
            
            # create pin-stroke       
            pin = etree.Element("rect")
            pin.set('id', '{}-port_{}'.format(tp, p_ix))
            pin.set('fill', 'none')
            pin.set('stroke-width', '1')
            pin.set('stroke', 'black')
            pin.set('fill',  'black')
            pin.set('height', '{:.1f}'.format(PW))
            pin.set('width', '{:.1f}'.format(PW))
            pin.set('x', '{:.1f}'.format(x-PW/2))
            pin.set('y', '{:.1f}'.format(y-PW/2))

            g.append(pin)


    grp = root.find('{*}g')
    if grp is not None and grp.attrib['id'] == 'tmp_bbox':
        root.replace(grp, g)
    else:
        root.append(g)
            
#    root.append(g)
    with open(svgfilename, 'wb') as f:
        f.write(etree.tostring(root, pretty_print=True))
            
    

        
    


def checkAndCreateSvgIcon(block, svgfilename):
    '''generate svg file (if not yet existing)'''
    # find bounding box
    if os.path.exists(svgfilename):
        with open(svgfilename, 'rb') as f:
            if '<svg' in f.read():
                return
    # create empty svg frame
    left, top, w, h = block.bbox if block.bbox else block.calcBboxFromPins()
    right, bottom = left + w, top + h
    dh2 = (h - (bottom - top))/2
    top = top - dh2
    bottom = bottom + dh2
        
            
    dwg = svgwrite.Drawing(filename=svgfilename, size=(right-left+2*icon_pin_size,bottom-top+2*icon_pin_size), profile='tiny', debug=False)
    dwg.attribs['xmlns:sodipodi'] = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"  
    dwg.attribs['xmlns:inkscape'] = "http://www.inkscape.org/namespaces/inkscape"
    dwg.attribs['id'] = "svg2"
    dwg.attribs['inkscape:version'] = "0.91 r13725"
    dwg.attribs['sodipodi:docname'] = block.blockname
    
    sodipodi = svgwrite.base.BaseElement(debug=False)
    sodipodi.elementname = 'sodipodi:namedview'
    t = '''objecttolerance="10"
           gridtolerance="10000"
           guidetolerance="10"
           showgrid="true"
           inkscape:snap-grids="true"
           inkscape:current-layer="svg2"
           inkscape:window-width="{w}"
           inkscape:window-height="{h}"'''.format(w=w, h=h)
    grid =  svgwrite.base.BaseElement(type="xygrid", units="px", spacingx="10", spacingy="10", debug=False)
    grid.elementname = 'inkscape:grid'
    sodipodi.elements.append(grid)
    
    
    for line in t.splitlines():
        k, v = line.split('=')
        sodipodi.attribs[k.strip()] = v.strip().strip('"')
    dwg.elements.append(sodipodi)
    
    group = svgwrite.container.Group(id='tmp_bbox')
    # create bbox
    group.add(dwg.rect(insert=(icon_pin_size, icon_pin_size), 
                                   size=(right-left, bottom-top),
                                   fill='none', stroke='darkGreen', stroke_width=1))
    dwg.add(group)
    dwg.save(pretty=True)
    print(dwg.elements)
    

