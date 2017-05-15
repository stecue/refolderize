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

# js function name will not starte with @
nameIntro='@intro.js'
fileIntro=open(nameIntro,'w')
nameMain='@main.js'
fileMain=open(nameMain,'w')

"""
Define some REs first
Note that re.match will only match string from the beginning and
no ^ is needed.
"""

reComment=re.compile(r'\s*//')
reFuncStart=re.compile(r'.*function[^)(]*\([^)(]*\).*')

#The _intro.js
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

#The _main.js
nameFunc1=re.sub(r'.*function[^)(]*\(([^)(]*)\).*\n',r'\1',currLine)
print(nameFunc1)
print(currLine,end='')
