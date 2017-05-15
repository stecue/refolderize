#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 21:41:16 2017

@author: xing
"""

import sys,re

nameJS=sys.argv[1]
print("Unpacking file {0} ...".format(nameJS))

fileJS=open(nameJS,'r')

nameIntro='_intro.js'
fileIntro=open(nameIntro,'w')

"""
Define some REs first
Note that re.match will only match string from the beginning and
no ^ is needed.
"""

reComment=re.compile(r's*//')
reFuncStart=re.compile(r'.*function[^)(]*(\([^)(]*)\)')

#The main lo:q
currLine=fileJS.readline()
while currLine != "":
    if re.match(reFuncStart,currLine) == None:
        print(currLine,end="")
        fileIntro.write(currLine)
        currLine=fileJS.readline()
        continue
    elif re.match(reComment,currLine) != None:        
        print(currLine,end="")
        fileIntro.write(currLine)
        currLine=fileJS.readline()
        continue
    else:
        break
