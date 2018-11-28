# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 13:25:13 2018

@author: paul
"""
import sys, os

from supsisim.const import templates, PD, viewTypes
import libraries

def get_defs(filename):
    defs = []
    with open(filename, 'rb') as f:
        tt = f.readlines()
    ix = 0
    while ix < len(tt):
        line = tt[ix]
        ix += 1
        if line.startswith('def '):
            n = 0
            rr = []
            while True:
                rr.append(line.strip())
                n += line.count('(') - line.count(')')
                if n == 0:
                    break
                else:
                    line = tt[ix]
                    ix += 1
                    
            # find body text
            body = []
            while ix < len(tt):
                line = tt[ix]
                ix += 1
#                print ('debug, scanning:', line)
                if line.strip() == '': #empty
                    body.append(line)
#                    print ('debug, empty:', line)
                elif line.strip()[0] in "#'": # comment
                    body.append(line)
#                    print ('debug, empty:', line)
                elif line[0] in " \t": # indented
                    body.append(line)
#                    print ('debug, adding:', line)
                else:
#                    print ('debug, breaking:', line)
                    break                    
            defs.append((' '.join(rr), ''.join(body)))

    res = []
    for m, body in defs:
        d, _, rest = m.partition('(')
        name = d.split()[1]

        rest, _, _ = rest.rpartition(')')
        args = [a.strip() for a in rest.split(',')]
        kwargs = dict()
        while '=' in args[-1]:
            a, b = args.pop().split('=')
            b = b.strip()
            bi = None
            bf = None
            try:
                bi = int(b)
                bf = float(b)
            except ValueError:
                pass
            if not bi is None:
                b = bi
            elif not bf is None:
                b = bf
            elif b.startswith('"'):
                b = b.strip('"')
            elif b.startswith("'"):
                b = b.strip("'")
            kwargs[a.strip()] = b

        inp = []
        outp= []        
        for p in args:
            t = p+'.next'
            if t in body:
                outp.append(p)
            else:
                inp.append(p)
                
                
        tt = body.strip()
        if tt.startswith('"""'):
            doc = body.split('"""')[1]
        elif tt.startswith("'''"):
            doc = body.split('"""')[1]
        else:
            doc = ''
        doc = doc.splitlines()
        for ix, line in enumerate(doc):
            if line.startswith('    '):
                doc[ix] = line[4:]
        doc = '\n'.join(doc)
        res.append((name, inp, outp, kwargs, doc))
    return res


def toBlk(filename, libname):
    res = []
    for name, inp, outp, properties, doc in get_defs(filename):
        if doc.strip():
            fmt = templates['block'].splitlines()
            fmt.insert(3, 'tooltip = """{tooltip}"""\n')
            fmt = '\n'.join(fmt)
        else:
            fmt = templates['block']
        wi = max([len(i) for i in inp])
        wo = max([len(o) for o in outp])
        w2 = (wi + wo + 1)//2 * 10
        inputs, outputs = [], []
        
        for ix, i in enumerate(inp):
            inputs.append((i, -w2, ix*PD))
        for ix, o in enumerate(outp):
            outputs.append((o, w2, ix*PD))
        
        p = libraries.libpath(libname)
        
        # copy diagram        
        ed, ext = viewTypes['myhdl']
        fndgm = os.path.join(p, name + ext)       
        views = dict(myhdl=name + ext)        
        with open(filename) as f:
            t = f.read()
        with open(fndgm, 'wb') as f:
            f.write(t)

            
        fnblk = os.path.join(p, name + '.py')
        # write block
        with open(fnblk, 'wb') as f:
            f.write(fmt.format(name=name, libname=libname, 
                        inp=inputs, outp=outputs, io=[], 
                        bbox=None, tooltip=doc,
                        parameters={}, 
                        properties=properties,
                        views=views))
        res.append((libname, name))
    return res # return list of imported blocks
        
    

if __name__ == '__main__':
    # Usage:
    #     python myhdl_to_blk.py libname, myhdlfilename
    # libname is without prefix
    libname = sys.argv[1]
    p = libraries.libpath(libname)
    if not os.path.isdir(p):
        os.mkdir(p)
    for filename in sys.argv[2:]:
        toBlk(filename, libname)