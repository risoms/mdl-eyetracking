# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 15:55:48 2019

@author: mdl-admin
"""
from random import shuffle

#coordinates
_coordinates = dict(top = (960,0), middle = (960,540), bottom = (960,1080))
#locations
_all_locations = ['top','top','top','top','top','middle','middle','middle','middle','middle','bottom','bottom','bottom','bottom','bottom']
#blocks
_all_block = [0,1,2]
#trial
_all_trial = [0,1,2,3,4]

_double_check = []
top = []
bottom = []
middle = []

#block
for block in _all_block:
    #copy list
    _all_locations_block = _all_locations.copy()
    shuffle(_all_locations_block)
    for trial in _all_trial: 
        #picking first location in list  
        location = _all_locations_block[trial] 
        print('blockNum: %d'%(block))
        print('trialNum: %d'%(trial))
        print('location: %s'%(location))
        print('location: %s %s'%(_coordinates[location][0],_coordinates[location][1]))
        pos = _coordinates[location]
        #the list deletes the first item
        _all_locations_block.pop(0) 
        if location=="top":
            top.append(location)
        if location=="bottom":
            bottom.append(bottom)
        if location=="middle":
            middle.append(middle)