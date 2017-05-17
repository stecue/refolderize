#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 21:41:16 2017

@author: xing

Version: 0.1
"""

import sys,re,os

nameJS=sys.argv[1]
print("Unpacking file {0} ...".format(nameJS))

#fileJS=open(nameJS,'r')

fileRaw=open(nameJS,'r')
#use hybrid block and inline comments will cause bugs (becase we are comparing line by line)
#make block comments starts with a new line
fileJS=open('@'+nameJS,'w')
blockcomment=False
currLine=fileRaw.readline()
while currLine != "":
    if re.match(r'.*/\*',currLine) == None  and blockcomment == False:
        fileJS.write(currLine)
        currLine=fileRaw.readline()
        continue

    if blockcomment == True:
        if re.match(r'.*?\*/',currLine) == None:
            #we are safe
            fileJS.write(currLine)
            currLine=fileRaw.readline()
            continue
        elif re.match(r'.*?\*/\s*$',currLine) != None:
            #The end has reached
            blockcomment=False
            if re.match(r'\s*\*/',currLine) == None:
                # */ must be in a separate line
                fileJS.write(re.sub(r'(.*?)\*/.*\n',r'\1',currLine)+'\n')
                fileJS.write('*/\n')
            else:
                fileJS.write(currLine)
            currLine=fileRaw.readline()
            continue
        elif re.match(r'.*\*/',currLine) != None:
            #some contents after block comment
            blockcomment=False
            if re.match(r'\s*\*/',currLine) == None: #means there are leading non-space contents
                # */ must be in a separate line
                tmpStr=re.sub(r'(.*?)\s*\*/.*\n',r'\1',currLine)
                if len(tmpStr) > 0: #print only the non-space contents on a sperate line
                    fileJS.write(tmpStr+'\n')
                tmpStr=re.sub(r'(.*?)(\s*\*/)(.*)\n',r'\2',currLine)
                fileJS.write(tmpStr+'\n')
            else:
                fileJS.write(re.sub(r'(.*?\*/)(.*\n)',r'\1\n',currLine))
            currLine=re.sub(r'(.*?\*/)(.*$)',r'\2',currLine)
            continue
    else:
    # blockcomment == False and we do have a '/*' now
    # split into two
        strBefore=re.sub(r'(.*?)(\s*/\*)(.*)\n',r'\1',currLine)
        strToken=re.sub(r'(.*?)(\s*/\*)(.*)\n',r'\2',currLine)
        strAfter=re.sub(r'(.*?)(\s*/\*)(.*)\n',r'\3',currLine)
        if re.match(r'.*//',strBefore) != None:
        # /* will not be effective. We are safe.
            fileJS.write(currLine)
            currLine=fileRaw.readline()
            continue
        else:
            if len(strBefore) > 0:
                fileJS.write(strBefore+'\n')
            fileJS.write(strToken+'\n')
            if len(strAfter) > 0:
                currLine=strAfter+'\n'
            else:
                currLine=fileRaw.readline()
            blockcomment=True
            continue
    #The following line will not be reached.
    currLine=fileRaw.readline()

fileJS.close()
fileRaw.close()
fileJS=open('@'+nameJS,'r')

# js function name will not starte with @
namePreface='@preface.js'
filePreface=open(namePreface,'w')
nameMain='@main.js'
fileMain=open(nameMain,'w')
fileFuns=[fileMain]

"""
Define some REs first
Note that re.match will only match string from the beginning and
no ^ is needed.
"""

reComment=re.compile(r'\s*//')
reFuncStart=re.compile(r'[\s(]*function[^)(]*\(\s*[^)(]*\s*\).*')

#The _preface.js
currLine=fileJS.readline()
rawCurrLine=currLine
while currLine != "":
    if re.match(reComment,currLine) != None:        
        print(currLine,end="")
        filePreface.write(currLine)
        currLine=fileJS.readline()
        rawCurrLine=currLine
        continue
    elif re.match(reFuncStart,currLine) == None:
        print(currLine,end="")
        filePreface.write(currLine)
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
    # now // and */ or */ will not be in the same line.
    if blockcomment:
        fileFuns[-1].write(rawCurrLine)
        if re.match(r'.*?\*/',currLine):
            blockcomment=False
        currLine=fileJS.readline()
        rawCurrLine=currLine
        continue

    # check for whole line comment starting with //. Now // and */ or */ will not be in the same line.
    if re.match(reComment,currLine) != None: #It will always be a comment line becase no /* or */ will be present here.
        fileFuns[-1].write(rawCurrLine)
        currLine=fileJS.readline()
        rawCurrLine=currLine
        continue
    #Now strip all inline comments
    currLine=re.sub(r'(.*)//.*',r'\1',currLine)
    
    if blockcomment == False:
        if re.match(r'.*/\*',currLine): #look for the start of block comment
            fileFuns[-1].write(rawCurrLine)
            blockcomment=True
            currLine=fileJS.readline()
            rawCurrLine=currLine
            continue
    
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

fileJS.close()
os.remove(fileJS.name)
print('All done!')
