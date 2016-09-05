#!/usr/bin/env python

import subprocess
import sys
import traceback

leftDict = {}
rightDict = {}


def execute_cmd(cmd):
    cmdStr =cmd
    #print("cmdStr: %r") %cmdStr
    try:
        x = subprocess.Popen(cmdStr,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        oc=x.communicate()
        x.wait()
        return oc[0]
    except:
        traceback.print_exc()
        return ""


def checkMD5Folder(username,hostname,directory,dict):
    cmdStr = "ssh "+username+"@"+hostname + " \'md5sum " +directory +"/*" + "\'"
    result = execute_cmd(cmdStr)
    resultList = result.split('\n')
    folderList = set()

    for tag in resultList:
        if (""==tag.strip()):
            continue
        tagList = tag.strip().split(" ",1)
        if tag.startswith("md5sum"):
            print("it must by impossible here ......")
            folderList.add(tagList[1].strip())
            continue
        else:
            dict[tagList[1]] = tagList[0].strip()
    #prepare to handle all the forder in the current directory:
    cmdForderStr = "ssh "+username+"@"+hostname + " \'ls -l " + directory  +  "  |grep \"^d\" \' "
    #print "cmdForderStr: %s" %cmdForderStr
    resultForder =  execute_cmd(cmdForderStr)
    if (""==resultForder.strip()):
        return
    resultForderList = resultForder.strip().split("\n")
    for folder in resultForderList:
        folderList = folder.strip().split(" ",-1)
        n = len(folderList)
        checkMD5Folder(username,hostname,directory+"/"+folderList[n-1],dict)



def campareDict(dict1, dict2):
    diffs = set ()
    keys = set(dict1.keys() + dict2.keys())
    for key in keys:
        if dict1.has_key(key) and dict2.has_key(key):
            if dict1.get(key) == dict2.get(key):
                print "********** file(%s) MD5 is same" %(key)
                continue
            else:
                print '\033[1;31;40m'
                print "**error** file(%s) MD5 not same, left MD5 is %r, right MD5 is %r. MD5 check failed !!!" %(key,dict1.get(key), dict2.get(key))
                print '\033[0m'
        elif dict1.has_key(key) == False:
            print '\033[1;31;40m'
            print "***error** file(%s) only exist in right folder, MD5 check failed !!!" % key
            print '\033[0m'
        elif dict2.has_key(key) == False:
            print '\033[1;31;40m'
            print "***error** file %s only exist in left folder, MD5 check failed !!!" % key
            print '\033[0m'
        else:
            print "it is impossible here ..."


if __name__ == "__main__":

    if (len(sys.argv) != 6):
        print "parameters not enough current: %d" %len(sys.argv)
        print '''
            usage: ./remoteMD5Check.py [username hostname1 hostname2 folder1 folder2]

        '''
        exit(1)

    username = sys.argv[1]
    hostname1 = sys.argv[2]
    folder1 = sys.argv[3]
    hostname2 = sys.argv[4]
    folder2 = sys.argv[5]

    print "username: %r,hostname1:%r,hostname2:%r,folder1:%r,folder2:%r" %(username,hostname1,hostname2,folder1,folder2)
    print '\n'
    #record md5code for remote host1
    checkMD5Folder(username,hostname1,folder1,leftDict)
    #checkMD5Folder("donghao.zdh","10.101.110.46","/home/donghao.zdh/conf_bak",leftDict)
    # for key,value in leftDict.items():
    #     print "key=%s, value=%s" %(key,value)

    #record md5code for remote host2
    #checkMD5Folder("donghao.zdh","10.189.231.62","/home/donghao.zdh/conf_bak",rightDict)
    checkMD5Folder(username,hostname2,folder2,rightDict)
    #campare two folder by MD5
    campareDict(leftDict,rightDict)
