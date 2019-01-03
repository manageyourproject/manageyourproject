import os
import sys
import math
import click
import shutil
import datetime as dt

from myp import projObj
from myp import confObj
from myp.utilities import datIO

class Namespace: pass

this = sys.modules[__name__]
this.projValid = [\
        'Subprojects can\'t have children',
        'Can\'t have identically named project and subproject',
        'Project does not exist',
        'Project already exists',
        ]

this.taskValid = [\
        'Subtasks can\'t have children',
        'Can\'t have identically named task and subtask',
        'Task does not exist',
        'Task already exists',
        ]

def initWConf(cfg):
    conf = confObj.confObj(cfg)
    if not os.path.isfile(conf.cfgFile):
        return 'No Config file found.'
    else:
        conf.loadDat(datIO.yamlRead(conf.cfgFile))
        return conf

def makeConf(cfg, name, email):
    conf = confObj.confObj(cfg)
    conf.newConf(name, email)
    writeConf(conf)
    return conf

def makeActive(confObj, projname=None):                # mark a project as active
    if projname:
        check = projCheck(confObj, projname)
        if isinstance(check, str) and not check == this.projValid[3]:
            return check

    confObj.confDat['session']['active']=projname
    writeConf(confObj)

def getActive(confObj):                              # print the active project
    if confObj.confDat['session']['active']:
        return 'Current active project: ' + confObj.confDat['session']['active']
    else:
        return 'There are no currently active projects'

def writeConf(confObj):
    confDat, confLoc = confObj.dumpDat()
    datIO.yamlWrite(confDat, confLoc)

def makeProj(confObj, projName, storeType, storeLoc, overwrite):
    names=projName.split('.')
    check = projCheck(confObj, projName)
    if isinstance(check, str) and not check == this.projValid[2]:
        return check
    
    elif check == this.projValid[3]:
        if not overwrite and not click.confirm(\
                'Project already exists.\n'+\
                'Would you like to overwrite it?'):
            return check
        else:
            deleteProj(confObj, projName)

    check = projStoreCheck(confObj, projName)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]

    if len(names)>1:
        check = projCheck(confObj, names[0])
        if check == this.projValid[2] and click.confirm(\
                'Parent project doesn\'t exists.\n'+\
                'Would you like to create it?', abort=True):
            output = makeProj(confObj, names[0], storeType, storeLoc, overwrite)
            if isinstance(output, str):
                return output

        elif not check == this.projValid[3]:
            return check

    confObj.trackProj(projName, storeType, storeLoc)
    createdProj = projObj.projObj(projName, projFile)
    createdProj.newProj(confObj)
    
    if len(names)>1:
        createdProj.giveParent(names[0])
        parProj = loadProj(confObj, names[0])
        if isinstance(parProj, str):
            return parProj
        else:
            parProj.giveChild(names[-1])
            writeProj(parProj)

    writeProj(createdProj)
    writeConf(confObj)

def deleteProj(confObj, projName, storeType=None, storeLoc=None):
    names=projName.split('.')
    check = projCheck(confObj, projName)
    if isinstance(check, str) and not check == this.projValid[3]:
        return check

    check = projStoreCheck(confObj, projName, storeType, storeLoc)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]

    childList=[]
    parProj = loadProj(confObj, names[0])
    if isinstance(parProj, str):
        return parProj

    if len(names)>1:
        if click.confirm('Are you sure you want to'+\
                ' delete this subproject', abort=True):

            os.remove(projFile)
            parProj.projDat['children'].remove(names[-1])
            writeProj(parProj)

    elif click.confirm('Are you sure you want to'+\
            ' delete this project, its folder,'+\
            ' and contents?', abort=True):
        
        childList = parProj.projDat['children']
        shutil.rmtree(storeLoc)
        if childList:
            for i in childList:
                del confObj.confDat['session']['projs']['.'.join([projName,i])]

    del confObj.confDat['session']['projs'][projName]

    if confObj.confDat['session']['active']==projName:
        makeActive(confObj)

    writeConf(confObj)


def loadProj(confObj, projName, storeType=None, storeLoc=None):
    check = projCheck(confObj, projName)
    if isinstance(check, str) and not check == this.projValid[3]:
        return check

    check = projStoreCheck(confObj, projName, storeType, storeLoc)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]

    loadedProj = projObj.projObj(projName,projFile)
    loadedProj.loadProj(datIO.yamlRead(projFile))
    return loadedProj

def writeProj(projObj):
    projDat, projFile = projObj.dumpProj()
    datIO.yamlWrite(projDat, projFile)

def projStoreCheck(confObj, projName, storeType=None, storeLoc=None):
    names=projName.split('.')
    if not storeType:
        storeType = confObj.confDat['session']['defaultstoretype']

    if storeType == 'yaml':
        if not storeLoc:
            storeLoc = os.path.join(confObj.confDat['session']['defaultprojpath'], names[0])
        elif storeLoc:
            storeLoc = os.path.normpath(storeLoc)

        projFile = os.path.join(storeLoc, names[-1]+'.yaml')
        if not os.path.exists(storeLoc):
            os.makedirs(storeLoc)

        return [storeType, storeLoc, projFile]

    else:
        return 'Can\'t load that store type'

def projCheck(confObj, projName, storeType=None, storeLoc=None):
    names=projName.split('.')
    if len(names) > 1:
        if len(names) > 2:
            return this.projValid[0]
        elif names[0]==names[-1]:
            return this.projValid[1]
    elif not projName in confObj.confDat['session']['projs']:
        return this.projValid[2]
    else:
        return this.projValid[3]
