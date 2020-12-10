#!/usr/bin/env python
import skfuzzy as fuz

from skfuzzy import control as ctrl
import numpy as np
import math
import random
  
def fuz_fun(dis_error,yaw_error):  
    d_e_range = np.arange(-2,2,0.1)
    th_e_range = np.arange(-1,1,0.1)
    v_range = np.arange(0.18,0.54,0.1)
    w_range = np.arange(-3.5,3.5,0.1)
    pi=np.pi
    
    d_e        = ctrl.Antecedent(d_e_range, 'd_e')
    th_e_scale = ctrl.Antecedent(th_e_range, 'th_e_scale')
    v          = ctrl.Consequent(v_range, 'v')
    w          = ctrl.Consequent(w_range, 'w')
    
    d_e['d_e_NH']= fuz.trapmf(d_e.universe,[-2,-2,-1.5,-0.5])
    d_e['d_e_NL']= fuz.trapmf(d_e.universe,[-0.6,-0.45,-0.3,0])
    d_e['d_e_AZ']= fuz.trimf(d_e.universe,[-0.15, 0 ,0.1])
    d_e['d_e_PL']= fuz.trapmf(d_e.universe,[0,0.3,0.5,0.6])
    d_e['d_e_PH']= fuz.trapmf(d_e.universe,[0.5,1.5,2,2])
    
    th_e_scale['th_e_NH'] = fuz.trapmf(th_e_scale.universe,[-pi,-pi,-pi/4,-pi/6])
    th_e_scale['th_e_NL'] = fuz.trapmf(th_e_scale.universe,[-pi/6,-pi/12,-pi/18,0])
    th_e_scale['th_e_AZ'] = fuz.trimf(th_e_scale.universe,[-pi/36,0,pi/36])
    th_e_scale['th_e_PL'] = fuz.trapmf(th_e_scale.universe,[0,pi/18,pi/12,pi/6])
    th_e_scale['th_e_PH'] = fuz.trapmf(th_e_scale.universe,[pi/6,pi/4,pi,pi])
    
    v['v_AZ']= fuz.trimf(v_range,[0.18,0.18,0.19])
    v['v_PL']= fuz.trapmf(v_range,[0.17,0.20,0.24,0.28])
    v['v_PM']= fuz.trapmf(v_range,[0.26,0.32,0.4,0.5])
    v['v_PH']= fuz.trapmf(v_range,[0.4,0.48,0.54,0.54])
    
    w['w_NH']= fuz.trapmf(w_range,[-pi,-pi,-pi/2,-pi/4])
    w['w_NM']= fuz.trapmf(w_range,[-pi/2,-pi/4,-pi/8,-pi/15])
    w['w_NL']= fuz.trapmf(w_range,[-pi/10,-pi/12,-pi/24,0])
    w['w_AZ']= fuz.trimf(w_range,[-pi/30,0,pi/30])
    w['w_PL']= fuz.trapmf(w_range,[0,pi/24,pi/12,pi/10])
    w['w_PM']= fuz.trapmf(w_range,[pi/15,pi/8,pi/4,pi/2])
    w['w_PH']= fuz.trapmf(w_range,[pi/4,pi/2,pi,pi])
    
    rule1 = ctrl.Rule(d_e['d_e_AZ'] & th_e_scale['th_e_AZ'], (v['v_AZ'] , w['w_AZ']) )
    rule2 = ctrl.Rule(d_e['d_e_AZ'] & th_e_scale['th_e_PL'], (v['v_AZ'] , w['w_PL']) )
    rule3 = ctrl.Rule(d_e['d_e_AZ'] & th_e_scale['th_e_PH'], (v['v_AZ'] , w['w_PL']) )
    rule4 = ctrl.Rule(d_e['d_e_AZ'] & th_e_scale['th_e_NH'], (v['v_AZ'] , w['w_NL']) )
    rule5 = ctrl.Rule(d_e['d_e_AZ'] & th_e_scale['th_e_NL'], (v['v_AZ'] , w['w_NL']) )
    
    rule6 = ctrl.Rule(d_e['d_e_PL'] & th_e_scale['th_e_AZ'], (v['v_PL'] , w['w_AZ']) )
    rule7 = ctrl.Rule(d_e['d_e_PL'] & th_e_scale['th_e_PL'], (v['v_PL'] , w['w_PL']) )
    rule8 = ctrl.Rule(d_e['d_e_PL'] & th_e_scale['th_e_PH'], (v['v_AZ'] , w['w_PM']) )
    rule9 = ctrl.Rule(d_e['d_e_PL'] & th_e_scale['th_e_NH'], (v['v_AZ'] , w['w_NM']) )
    rule10= ctrl.Rule(d_e['d_e_PL'] & th_e_scale['th_e_NL'], (v['v_PL'] , w['w_NL']) )
    
    rule11 = ctrl.Rule(d_e['d_e_PH'] & th_e_scale['th_e_AZ'], (v['v_PM'] , w['w_AZ']) )
    rule12 = ctrl.Rule(d_e['d_e_PH'] & th_e_scale['th_e_PL'], (v['v_AZ'] , w['w_PL']) )
    rule13 = ctrl.Rule(d_e['d_e_PH'] & th_e_scale['th_e_PH'], (v['v_AZ'] , w['w_PM']) )
    rule14 = ctrl.Rule(d_e['d_e_PH'] & th_e_scale['th_e_NH'], (v['v_AZ'] , w['w_NM']) )
    rule15 = ctrl.Rule(d_e['d_e_PH'] & th_e_scale['th_e_NL'], (v['v_AZ'] , w['w_NL']) )
    
    rule16= ctrl.Rule(d_e['d_e_NL'] & th_e_scale['th_e_AZ'], (v['v_AZ'] , w['w_AZ']) )
    rule17= ctrl.Rule(d_e['d_e_NL'] & th_e_scale['th_e_PL'], (v['v_AZ'] , w['w_AZ']) )
    rule18= ctrl.Rule(d_e['d_e_NL'] & th_e_scale['th_e_PH'], (v['v_AZ'] , w['w_AZ']) )
    rule19= ctrl.Rule(d_e['d_e_NL'] & th_e_scale['th_e_NH'], (v['v_AZ'] , w['w_AZ']) )
    rule20= ctrl.Rule(d_e['d_e_NL'] & th_e_scale['th_e_NL'], (v['v_AZ'] , w['w_AZ']) )
    
    rule21 = ctrl.Rule(d_e['d_e_NH'] & th_e_scale['th_e_AZ'], (v['v_AZ'] , w['w_AZ']) )
    rule22 = ctrl.Rule(d_e['d_e_NH'] & th_e_scale['th_e_PL'], (v['v_AZ'] , w['w_NL']) )
    rule23 = ctrl.Rule(d_e['d_e_NH'] & th_e_scale['th_e_PH'], (v['v_AZ'] , w['w_AZ']) )
    rule24 = ctrl.Rule(d_e['d_e_NH'] & th_e_scale['th_e_NH'], (v['v_AZ'] , w['w_AZ']) )
    rule25 = ctrl.Rule(d_e['d_e_NH'] & th_e_scale['th_e_NL'], (v['v_AZ'] , w['w_AZ']) )
    
    
    jetbot_ctrl = ctrl.ControlSystem([rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,
                                      rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25])
    
    velocity = ctrl.ControlSystemSimulation(jetbot_ctrl)
    
    
    velocity.input['d_e'] = dis_error 
    velocity.input['th_e_scale'] = yaw_error 
    velocity.compute()
    
    return ([velocity.output['v'],velocity.output['w']])

