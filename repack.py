#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 21:41:16 2017

@author: xing
"""

import sys,re,os

def insertText(FileGuest, FileHost):
#FileGuest and FileHost are two FILE objects.
    currLine=FileGuest.readline()
    while currLine != "":
        FileHost.write(currLine)
        currLine=FileGuest.readline()

def expandFunc(currLine,parentFuncPath):
#Some debug info
#extract the name of the function:
    nameFunc=re.sub(r'[\s(]*function\s*([^)(\s]*)\s*.*\n',r'\1',currLine)
#I still need to strip the comments here:
    blockcomment=False
    fileFunc=open(parentFuncPath+r'@'+nameFunc+'.js','r')
#The first line (func name) should go directly to "toReturn"
    toReturn=fileFunc.readline()
#Start analyze the rest of the file:
    currLine=fileFunc.readline()
    rawCurrLine=currLine
    while currLine != '':
    #First deal with comments
    #if block comments:
        if re.match(r'.*\*/',currLine) == None  and blockcomment == True:
            toReturn=toReturn+currLine
            currLine=fileFunc.readline()
            rawCurrLine=currLine
            continue
    #whole inline comments:
        elif re.match(r'\s*//',currLine) != None:
            toReturn=toReturn+currLine
            currLine=fileFunc.readline()
            rawCurrLine=currLine
            continue
    #The last line of block comments:
        elif re.match(r'.*\*/',currLine) != None  and blockcomment == True:
            toReturn=toReturn+currLine
            currLine=fileFunc.readline()
            rawCurrLine=currLine
            blockcomment=False
            continue
    #The first line of block comments:
        elif re.match(r'.*/\*',currLine) != None and blockcomment == False:
            toReturn=toReturn+currLine
            currLine=fileFunc.readline()
            rawCurrLine=currLine
            blockcomment=True
            continue

    #whole line comments are processed, strip comments for further processing
        currLine=re.sub(r'(.*)//.*',r'\1',currLine)
        if re.match(reFuncStart,currLine):
            toReturn=toReturn+expandFunc(currLine,parentFuncPath+r'@'+nameFunc+r'/')
            #skip the ending "}"
            currLine=fileFunc.readline()
            currLine=fileFunc.readline()
            rawCurrLine=currLine
            continue
        else:
            #Simply return the current line
            toReturn=toReturn+rawCurrLine
            currLine=fileFunc.readline()
            rawCurrLine=currLine
            continue
    #The last line of the while block. It should not be reached under normal circumstances.
        print("Something wrong,-->{0:s}".format(fileFunc.readline()))

    fileFunc.close()
    return toReturn


nameJS=sys.argv[1]
print("Packing functions into {0} ...".format(nameJS))


fileJS=open(nameJS,'w')
#Append fileIntro first.
fileIntro=open(r'@intro.js','r')
insertText(fileIntro,fileJS)
fileIntro.close()
#Now let's deal with the main function file:

"""
Define some REs first
Note that re.match will only match string from the beginning and
no ^ is needed.
"""
reComment=re.compile(r'\s*//')
reFuncStart=re.compile(r'[\s(]*function[^)(]*\(\s*[^)(]*\s*\).*')

fileMain=open(r'@main.js','r')
#Skip the first line because it is often an anonymous function
fileJS.write(fileMain.readline())
currLine=fileMain.readline()
rawCurrLine=currLine
blockcomment=False

while currLine != "":
#First deal with comments
#if block comments:
    if re.match(r'.*\*/',currLine) == None  and blockcomment == True:
        fileJS.write(currLine)
        currLine=fileMain.readline()
        rawCurrLine=currLine
        continue
#whole inline comments:
    elif re.match(r'\s*//',currLine) != None:
        fileJS.write(currLine)
        currLine=fileMain.readline()
        rawCurrLine=currLine
        continue
#The last line of block comments:
    elif re.match(r'.*\*/',currLine) != None  and blockcomment == True:
        fileJS.write(currLine)
        currLine=fileMain.readline()
        rawCurrLine=currLine
        blockcomment=False
        continue
#The first line of block comments:
    elif re.match(r'.*/\*',currLine) != None and blockcomment == False:
        fileJS.write(currLine)
        currLine=fileMain.readline()
        rawCurrLine=currLine
        blockcomment=True
        continue
#whole line comments are processed, strip comments for further processing
    currLine=re.sub(r'(.*)//.*',r'\1',currLine)
    if re.match(reFuncStart,currLine):
#It seems that we need to define a recursive function...
        fileJS.write(expandFunc(currLine,r'@main/'))
        #Skip the ending "}"
        currLine=fileMain.readline()
        #The real "next" line
        currLine=fileMain.readline()
        rawCurrLine=currLine
        continue
    else:
        fileJS.write(rawCurrLine)
        currLine=fileMain.readline()
        rawCurrLine=currLine
        continue

#The last line of the while block. It should not be reached under normal circumstances.
    currLine=fileMain.readline()
#close the fileMain and exit
fileMain.close()
fileJS.close()
print('All Done!')
