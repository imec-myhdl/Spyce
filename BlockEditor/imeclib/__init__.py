# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 11:11:15 2017

@author: paul
"""

from supsisim.block import Block


libs = dict()
libs['can'] = [ \
    Block(name='Baumer_enc', outp=1, icon='ENC', params='baumer_EncBlk|Device ID: 0x01|Resolution: 500'),
    Block(name='Epos_AD', outp=1, icon='AD', params='epos_areadBlk|Device ID: 0x01|Channel [0/1]: 0'),
    Block(name='Epos_enc', outp=1, icon='ENC', params='epos_EncBlk|Device ID: 0x01|Resolution: 1000'),
    Block(name='Epos_mot_I', inp=1, icon='MOT_I', params='epos_MotIBlk|Device ID: 0x01|Prop. gain: 2200|Integ. gain: 500'),
    Block(name='Epos_mot_X', inp=1, icon='MOT_X', params='epos_MotXBlk|Device ID: 0x01|Prop. gain: 126|Integ. gain: 325|Deriv. gain: 238|Vel. FeedForw: 0|Acc. Feed Forw.:1'),
    Block(name='Maxon_enc', outp=1, icon='ENC', params='maxon_EncBlk|Device ID: 0x01|Resolution: 1000'),
    Block(name='Maxon_mot_I', inp=1, icon='MOT_I', params='maxon_MotBlk|Device ID: 0x01|Prop. gain: 2200|Integ. gain: 500'),
    Block(name='Mclm_AD', outp=1, icon='AD', params='MCLM_ADBlk|Device ID: 0x01'),
    Block(name='Mclm_enc', outp=1, icon='ENC', params='MCLM_EncBlk|Device ID: 0x01|Resolution: 125000'),
    Block(name='Mclm_mot_X', inp=1, icon='MOT_X', params='MCLM_MotXBlk|Device ID: 0x01|Resolution: 125000'),
    Block(name='Mclm_CO_enc', outp=1, icon='ENC', params='MCLM_CO_EncBlk|Device ID: 0x01|Resolution: 125000'),
    Block(name='Mclm_CO_mot_X', inp=1, icon='MOT_X', params='MCLM_CO_MotXBlk|Device ID: 0x01|Resolution: 125000') ]

libs['comedi'] = [ \
    Block(name='AD', outp=1, icon='AD', params="comediADBlk|Device: '/dev/comedi0'|Channel: 0|Range: 0"),
    Block(name='DA', inp=1, icon='DA', params="comediDABlk|Device: '/dev/comedi0'|Channel: 0|Range: 0"),
    Block(name='DI', outp=1, icon='DI', params="comediDIBlk|Device: '/dev/comedi0'|Channel: 0"),
    Block(name='DO', inp=1, icon='DO', params="comediDOBlk|Device: '/dev/comedi0'|Channel: 0|Threshold: 1.0") ]

libs['common'] = [ \
    Block(name='Const', outp=1, icon='CONST', params='constBlk|Value: 0'),
    Block(name='PulseGenerator', outp=1, icon='SQUARE', params='squareBlk|Amplitude: 1|Period: 4|Width: 2|Bias: 0|Delay: 0'),
    Block(name='Step', outp=1, icon='STEP', params='stepBlk|Step Time: 1|Step Value: 1'),
    Block(name='LTI_continous', inp=1, outp=1, iosetble=True, icon='CSS', params='cssBlk|System: sys|Initial conditions: 0'),
    Block(name='LTI_discrete', inp=1, outp=1, iosetble=True, icon='DSS', params='dssBlk|System: sys|Initial conditions: 0'),
    Block(name='Gain', inp=1, outp=1, iosetble=True, icon='MULT', params='matmultBlk|Gains: 1'),
    Block(name='Sub', inp=2, outp=1, icon='PM', params='sumBlk|Gains: [1,-1]'),
    Block(name='Sum', inp=2, outp=1, iosetble=True, icon='SUM', params='sumBlk|Gains: [1,-1]'),
    Block(name='Print', inp=1, iosetble=True, icon='PRINT', params='printBlk'),
    Block(name='Saturation', inp=1, outp=1, icon='SATUR', params='saturBlk|Upper saturation:10|Lower saturation: -10') ]

libs['linear'] = [ \
    Block(name='LTI_continous', inp=1, outp=1, iosetble=True, icon='CSS', params='cssBlk|System: sys|Initial conditions: 0'),
    Block(name='LTI_discrete', inp=1, outp=1, iosetble=True, icon='DSS', params='dssBlk|System: sys|Initial conditions: 0'),
    Block(name='Init_enc', inp=1, outp=1, icon='INIT', params='init_encBlk|Trigger Time: 1|Default Output: 0|Offset: 0'),
    Block(name='Integral', inp=1, outp=1, icon='INTG', params='intgBlk|Initial conditions: 0'),
    Block(name='Gain', inp=1, outp=1, iosetble=True, icon='MULT', params='matmultBlk|Gains: 1'),
    Block(name='Delay', inp=1, outp=1, icon='DELAY', params='zdelayBlk|Initial conditions: 0')]

libs['math'] = [ \
    Block(name='Sub', inp=2, outp=1, icon='PM', params='sumBlk|Gains: [1,-1]'),
    Block(name='Sum', inp=2, outp=1, iosetble=True, icon='SUM', params='sumBlk|Gains: [1,-1]'),
    Block(name='Prod', inp=2, outp=1, iosetble=True, icon='PROD', params='prodBlk') ]

libs['nonlin'] = [ \
    Block(name='Abs', inp=1, outp=1, icon='ABS', params='absBlk'),
    Block(name='FMU', inp=1, outp=1, iosetble=True, icon='FMU', params="FmuBlk|IN_REF: ['u']|OUT_REF: ['y']|FMU_NAME: ''|Major step: 0.01|Feedthrough: 0"),
    Block(name='Lookup', inp=1, outp=1, icon='LOOKUP', params='lutBlk|Coeff : [1,0]'),
    Block(name='Saturation', inp=1, outp=1, icon='SATUR', params='saturBlk|Upper saturation:10|Lower saturation: -10'),
    Block(name='Switch', inp=9, outp=1, icon='SWITCH', params='switchBlk|Condition [0 < or 1 >] : 0|Compare Value: 0.5|Persistence [0 no or 1 yes]: 0'),
    Block(name='Trig', inp=1, outp=1, icon='TRIG', params='trigBlk|sin->1 cos->2 tan->3: 1'),
    Block(name='Generic_C_Block', inp=1, outp=1, iosetble=True, icon='CBLOCK', params="genericBlk|States: [0,0]|FeedForw: 0|Real pars: []| Int pars:[]|String: ''| Function name: 'test'") ]

libs['output'] = [ \
     Block(name='Plot', inp=1, iosetble=True, icon='PRINT', params='printBlk') ]

libs['Socket'] = [ \
    Block(name='socket', inp=1, iosetble=True, icon='SOCK', params="unixsocketCBlk|Socket: 'bsock'"),
    Block(name='Socket', outp=1, iosetble=True, icon='SOCK', params="unixsocketSBlk|Socket: 'ssock'|Default outputs:[0.]") ]
        
libs['testlib'] = [ \
    Block(name='test1', inp=[(-40, -20, 'a'), (-40, 20, 'b')], outp=[(40, 0, 'z')], iosetble=True, icon='test1', params='sumBlk|Gains: [1,-1]')]



