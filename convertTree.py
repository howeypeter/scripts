#!/usr/bin/env python

# Converts File Trees to normalized unix directories.

import sys
import codecs
import json

debug = False



def depthTree(linum):
    depth=0 # Find how many directories deep the line is
    ld = linum.split('--')[0]
    ld = ld.replace(u'\ufffd', '#')
    for i in range(0, len(ld)):
        depth=depth + 1
    depth = int(depth / 4)
    return depth

def create_directory(lines):
    maximumDepth=0
    for m in range(0, len(lines)):
          d = depthTree(lines[m])
          if d >= maximumDepth:
              maximumDepth=d
    # create a JSON skeleton
    data_set=[]
    for i in range(0,maximumDepth):
      data_set.append([])
    return data_set

def directoryMap(dirMap, lines):
    d=dirMap
    for m in range(0, len(lines)):
      if not isFile(lines, m): # if it's a directory
        depth=depthTree(lines[m])
        d[depth].append(m)
    return d


def isFile(lines, lineNo):
    # returns True if file, False if Dir
    try:
      currentLineDepth = depthTree(lines[lineNo])
      nl = lineNo + 1
      nextLineDepth = depthTree(lines[nl])
      if nextLineDepth <= currentLineDepth:
        return True
      else:
        return False
    except:
      return True

def findFirstDirOfDepth(lines, lineNo, depth):
  for e in reversed(range(0, lineNo)):
    dirtyName=lines[e]
    cleanName=dirtyName.split('-- ')[1]
    if not isFile(lines, e): # if it's a directory
     if depthTree(dirtyName) == depth:
         return str(cleanName)

def getFileFQDN(lines, dirMap, lineNo):
    # First goal here is to get a list of each dir which the file is under
    # Secondly, change that list to a concatenated FQDN
    FQDN=""
    dirDepthOfFile=depthTree(lines[lineNo])
    for i in range(0,dirDepthOfFile):
      p=0
      for d in range(0,len(dirMap[i])):
          if int(dirMap[i][d]) < int(lineNo):
              p=dirMap[i][d]
      FQDN=FQDN + lines[p].split('-- ')[1] + "\\"
    # Add the filename
    FQDN = FQDN + lines[lineNo].split('-- ')[1]

    return FQDN



def convertTree(filename):
  with codecs.open(filename, 'r',encoding='WINDOWS-1252', errors='replace') as f:
  #with codecs.open(filename, 'r',encoding='UTF-8', errors='replace') as f:
    lines = f.readlines()
    lines = [line.rstrip() for line in lines]

  # step 1 create a JSON skeleton for the directory maps
  d=create_directory(lines)

  # step 2 update JSON with info on each directory in the file
  dm=directoryMap(d, lines)
  # step 3 parse each file into a FQDN
  for q in range(0, len(lines)):
    if isFile(lines, q):
      result = getFileFQDN(lines, dm, q)
      print(result)
      #print("___")
  return 0

def main():
  print("Src File: " + sys.argv[1])
  convertTree(sys.argv[1])
main()
