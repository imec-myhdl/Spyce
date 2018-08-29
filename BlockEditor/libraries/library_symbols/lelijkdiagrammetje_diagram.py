blocks = [{'libname': u'testlib', 'name': u'module2', 'blockname': u'module', 'type': u'block', 'pos': {'y': 50.0, 'x': -340.0}, 'properties': {}},
          {'libname': u'symbols', 'name': u'module1', 'blockname': u'module', 'type': u'block', 'pos': {'y': -130.0, 'x': -530.0}, 'properties': {}},
          {'libname': 'nonlin', 'name': u'FMU', u'parameters': {'outp': 1, 'inp': 1}, 'blockname': 'FMU', 'type': u'block', 'pos': {'y': -290.0, 'x': -290.0}, 'properties': {'Major step': ' 0.01', 'Feedthrough': ' 0', 'OUT_REF': " ['y']", 'IN_REF': " ['u']", 'FMU_NAME': " ''", 'name': 'FmuBlk'}},
          {'libname': 'output', 'name': u'Plot', u'parameters': {'outp': 0, 'inp': 1}, 'blockname': 'Plot', 'type': u'block', 'pos': {'y': -290.0, 'x': -500.0}, 'properties': {'name': 'printBlk'}},
          {'libname': u'symbols', 'name': u'module', 'blockname': u'module', 'type': u'block', 'pos': {'y': -100.0, 'x': -250.0}, 'properties': {}}]

connections = []

nodes = []