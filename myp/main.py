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

    if not storeType:
        storeType = confObj.confDat['session']['defaultstoretype']

    if not storeLoc:
        storeLoc = confObj.confDat['session']['defaultstoretype']
    elif storeType == 'yaml' and storeLoc:
        storeLoc = os.path.normpath(storeLoc)

    names = projName.split('.')
    if names>1:
        check = projCheck(confObj, names[0])
        if check == this.projValid[2] and click.confirm(\
                'Parent project doesn\'t exists.\n'+\
                'Would you like to create it?', abort=True):
            parProj = makeProj(confObj, names[0], storeType, storeLoc)
            writeProj(parProj)
            confObj.trackProj(projName, storeType, storeLoc)
            writeConf(conf)
        else:
            return check

    if storeType == 'yaml':
        storeLoc = os.path.join(storeLoc, names[0])
        projFile = os.path.join(storeLoc, names[-1]+'.yaml')
        if not os.path.exists(storeLoc):
            os.makedirs(storeLoc)
    else:
        return 'Can\'t load that store type'

    confObj.trackProj(projName, storeType, storeLoc)
    createdProj = projObj.projObj(projFile, projName)
    createdProj.newProj(confObj, names[0], storeType, storeLoc)
    
    if names>1:
        createdProj.giveParent(names[0])
        parProj = loadProj(confObj, names[0])
        if isinstance(parProj, str):
            return parProj
        else:
            parProj.giveChild(names[-1])
            writeProj(parProj)

    writeProj(createdProj)
    writeConf(conf)

def deleteProj(confObj, projName):
    check = projCheck(confObj, projName)
    if isinstance(check, str) and not check == this.projValid[3]:
        return check

    storeType = confObj.confDat['session']['projs'][projName]['storeType']
    storeLoc = confObj.confDat['session']['projs'][projName]['storeLoc']
    names = projName.split('.')
    if storeType == 'yaml':
        storeLoc = os.path.join(storeLoc, names[0])
        projFile = os.path.join(storeLoc, names[-1]+'.yaml')
    else:
        return 'Can\'t load that store type'

    childList=[]
    if len(projname)>1:
        if click.confirm('Are you sure you want to'+\
                ' delete this subproject', abort=True):

            os.remove(projFile)
            parProj = projObj.projObj(confObj, names[0])
            parProj = loadProj(confObj, names[0])
            if isinstance(parProj, str):
                return parProj
            else:
                parProj.projDat['children'].remove(projname[-1])
                writeProj(parProj)

    elif click.confirm('Are you sure you want to'+\
            ' delete this project, its folder,'+\
            ' and contents?', abort=True):
        
        parProj = projObj.projObj(confObj, names[0])
        parProj = loadProj(confObj, names[0])
        if isinstance(parProj, str):
            return parProj
        else:
            childList = parProj.projDat['children']
            shutil.rmtree(storeLoc)

        if childList:
            for i in childList:
                del confObj.confDat['session']['projs']['.'.join([projName,i])]

    del confObj.confDat['session']['projs'][projName]

    if confObj.confDat['session']['active']==projName:
        makeActive(confObj)

    writeConf(confObj)


def loadProjDat(confObj, projName):
    check = projCheck(confObj, projName)
    if isinstance(check, str) and not check == this.projValid[3]:
        return check

    storeType = confObj.confDat['session']['projs'][projName]['storeType']
    storeLoc = confObj.confDat['session']['projs'][projName]['storeLoc']
    names = projName.split('.')
    if storeType == 'yaml':
        storeLoc = os.path.join(storeLoc, names[0])
        projFile = os.path.join(storeLoc, names[-1]+'.yaml')
    else:
        return 'Can\'t load that store type'

    loadedProj = projObj.projObj(projName,projFile)
    loadedProj.loadDat(datIO.yamlRead(projFile))
    
    return loadedProj

def writeProj(projObj):
    projDat, projFile = projObj.dumpDat()
    datIO.yamlWrite(projDat, projFile)

def projCheck(confObj, projName):
    names = projName.split('.')
    if len(names) > 1:
        if len(names) > 2:
            return this.projValid[0]
        elif names[0]==names[-1]:
            return this.projValid[1]
    elif not projName in confObj.confDat['session']['projs']:
        return this.projValid[2]
    else:
        return this.projValid[3]
