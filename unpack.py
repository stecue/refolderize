#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 21:41:16 2017

@author: xing
"""

import sys,re,os

nameJS=sys.argv[1]
print("Unpacking file {0} ...".format(nameJS))

fileRaw=open(nameJS,'r')

#use hybrid block and inline comments will cause bugs (becase we are comparing line by line)
#make block comments starts with a new line
fileJS=open('@'+nameJS,'w')
currLine=fileRaw.readline()
while currLine != "":
    #delete the extra /*
    while len(re.findall(r'([^\\]//.*)/\*',currLine)) > 0:
        currLine=re.sub(r'([^\\]//.*)/\*',r'\1',currLine)
        print(currLine)
    while len(re.findall(r'([^\\]//.*)\*/',currLine)) > 0:
        currLine=re.sub(r'([^\\]//.*)\*/',r'\1',currLine)
        print(currLine)
    re.sub(r'/\*',r'\n/*\n',currLine)
    re.sub(r'\*/',r'\n*/\n',currLine)
    re.sub(r'\n+',r'\n',currLine)
    fileJS.write(currLine)
    currLine=fileRaw.readline()

fileJS.close()
fileRaw.close()
fileJS=open('@'+nameJS,'r')

# js function name will not starte with @
nameIntro='@intro.js'
fileIntro=open(nameIntro,'w')
nameMain='@main.js'
fileMain=open(nameMain,'w')
fileFuns=[fileMain]

"""
Define some REs first
Note that re.match will only match string from the beginning and
no ^ is needed.
"""

reComment=re.compile(r'\s*//')
reFuncStart=re.compile(r'[\s(]*function[^)(]*\([^)(]*\).*')

#The _intro.js
currLine=fileJS.readline()
rawCurrLine=currLine
while currLine != "":
    if re.match(reComment,currLine) != None:        
        print(currLine,end="")
        fileIntro.write(currLine)
        currLine=fileJS.readline()
        rawCurrLine=currLine
        continue
    elif re.match(reFuncStart,currLine) == None:
        print(currLine,end="")
        fileIntro.write(currLine)
        currLine=fileJS.readline()
        rawCurrLine=currLine
        continue
    else:
        print('Entering main function....{0:s}'.format(currLine),end="")
        fileFuns[-1].write(rawCurrLine)
        currLine=fileJS.readline()
        rawCurrLine=currLine
        break

#The _main.js
os.makedirs(r'@main', exist_ok=True)
#Keep track of current level
parentDir=r'@main/'
currDir=parentDir
parentFunc=['main']
#level 1 for main function. level 0 is the user js itself.
nlevel=len(parentFunc)
leftcb=1
rightcb=0
blockcomment=False
while currLine != "":
    # First test if full inline comment
    if re.match(reComment,currLine) != None:
        fileFuns[-1].write(rawCurrLine)
        currLine=fileJS.readline()
        rawCurrLine=currLine
        continue
    #Now strip all inline comments
    currLine=re.sub(r'(.*)//.*',r'\1',currLine)
    
    #Check if it is the inline block comment
    if blockcomment:
        if re.match(r'.*\*/',currLine):
            #strip and continue:
            currLine=re.sub(r'.*\*/(.*)',r'\1',currLine)
            blockcomment=False
            continue
        else:
            fileFuns[-1].write(rawCurrLine)
            currLine=fileJS.readline()
            rawCurrLine=currLine
            continue
    #Not that there is not "contniue" so that the "blockcomment" will be
    # applied to the next line.
    if blockcomment == False:
        if re.match(r'.*/\*',currLine):
            #strip the inline comment and set ifcomment to true;
            currLine=re.sub(r'(.*)/\*.*',r'\1',currLine)
            blockcomment=True
    
    #Testing comments done. 
    if re.match(reFuncStart,currLine) == None:
        #Copy the function first
        fileFuns[-1].write(rawCurrLine)
        leftcb=leftcb+len(re.findall('{',currLine))
        rightcb=rightcb+len(re.findall('}',currLine))
        print('leftcb: {0:3d}, rightcb: {1:3d}'.format(leftcb,rightcb))
        #leftcb-nlevel should be larger than rightcb by (at least) 1 before the pairing rightcb
        if (leftcb-nlevel+1) == rightcb:
            print(currLine,end="")
            print('Going to the upper level...')
            print('from '+parentDir+' ',end='')
            parentDir=re.sub(r'(.*)@'+parentFunc.pop()+r'/$',r'\1',parentDir)
            print('to '+parentDir)
            #decrease level number by one.
            nlevel=len(parentFunc)
            #close the function file, but not the @main.js
            if len(fileFuns) > 1:
                fileFuns.pop().close()
                #We also need to the add the ending line to the file for the parent function.
                #Note that for the "main" function, we should not add the exta line.
                fileFuns[-1].write(rawCurrLine)
        currLine=fileJS.readline()
        rawCurrLine=currLine
    else:
        print(currLine,end="")
        #increase level number by one.
        nlevel=nlevel+1 #should be the same as len(parentFunc) after push.
        leftcb=leftcb+len(re.findall('{',currLine))
        rightcb=rightcb+len(re.findall('}',currLine))
        nameFunc=re.sub(r'[\s(]*function\s*([^)(\s]*)\s*.*\n',r'\1',currLine)
        currDir=parentDir+r'@'+nameFunc+r'/'
        os.makedirs(currDir, exist_ok=True)
        #Note that we need to add the line to current level function as well.
        fileFuns[-1].write(rawCurrLine)
        fileFuns.append(open(parentDir+'@'+nameFunc+'.js','w'))
        fileFuns[-1].write(rawCurrLine)
        parentDir=currDir
        parentFunc.append(nameFunc)
        currLine=fileJS.readline()
        rawCurrLine=currLine

