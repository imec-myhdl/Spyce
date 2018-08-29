blocks = [{'libname': 'nonlin', 'name': u'FMU', u'parameters': {'outp': 1, 'inp': 1}, 'blockname': 'FMU', 'type': u'block', 'pos': {'y': 50.0, 'x': -60.0}, 'properties': {'Major step': ' 0.01', 'Feedthrough': ' 0', 'OUT_REF': " ['y']", 'IN_REF': " ['u']", 'FMU_NAME': " ''", 'name': 'FmuBlk'}},
          {'libname': 'common', 'name': u'LTI_discrete', u'parameters': {'outp': 1, 'inp': 1}, 'blockname': 'LTI_discrete', 'type': u'block', 'pos': {'y': -110.0, 'x': -410.0}, 'properties': {'Initial conditions': ' 0', 'name': 'dssBlk', 'System': ' sys'}}]

connections = [{'pos2': {'y': -10.0, 'x': -170.0}, 'type': u'connection', 'pos1': {'y': -110.0, 'x': -366.0}}]

nodes = [{'type': u'node', 'pos': {'y': -10.0, 'x': -170.0}}]