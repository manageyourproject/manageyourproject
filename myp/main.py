import os
import sys
import math
import shutil
import datetime

from collections import OrderedDict

from myp import confObj
from myp import projObj
from myp import taskObj
from myp.scripts import cli
from myp.scripts import cliUtils
from myp.utilities import datIO

def initConf(cfg):
    cfgFile = os.path.join(cfg, 'config.yaml')           # default file location
    if not os.path.isfile(cfgFile):
        name, email = getUserInfo()
        conf = confObj.confObj(cfg=cfg, name=name, email=email)
        writeConf(conf)
    else:
        conf = confObj.confObj(cfg=cfg, dat=datIO.yamlRead(cfgFile))

    return conf

def getUserInfo():
    cliUtils.printToCli('No config file found.')
    cliUtils.getConfirmation('Would you like to create one?')
    name = cliUtils.getInput('Name:')
    email = cliUtils.getInput('Email:')
    return [name, email]

def writeConf(confObj):
    confDat, confLoc = confObj.dumpDat()
    datIO.yamlWrite(confDat, confLoc)

def makeActive(confObj, projname=None):                # mark a project as active
    if projname:
        check = confObj.projCheck(projname)
        if isinstance(check, str) and not check.endswith(confObj.projValid[3]):
            return check

    confObj.confDat['session']['active']=projname
    writeConf(confObj)

def getActive(confObj):                              # print the active project
    if confObj.confDat['session']['active']:
        return 'Current active project: ' + confObj.confDat['session']['active']
    else:
        return 'There are no currently active projects'

def makeProj(confObj, projName, storeType, storeLoc, force=False,\
             dat=None, *args, **kwargs):
    names=projName.split('.')
    check = confObj.projCheck(projName)
    if isinstance(check, str) and (check.endswith(confObj.projValid[0]) or\
                                   check.endswith(confObj.projValid[1])):
        return check
    
    elif check.endswith(confObj.projValid[3]):
        if not force and cliUtils.getConfirmation(check+\
                '\nWould you like to overwrite it?'):
            deleteProj(projName)
        elif force:
            deleteProj(projName)

    check = confObj.projStoreCheck(projName)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]
    else:
        return check

    createdProj = projObj.projObj(projName, projFile, confObj=confObj, dat=dat)
    if len(names)>1:
        check = confObj.projCheck(names[0])
        if check.endswith(confObj.projValid[2]):
            if not force:
                cliUtils.getConfirmation('Parent ' + check + '\nWould you like to create it?')

            createdProj.giveParent(names[0])
            parProj = confObj.addProj(names[0], storeType=StoreType,\
                                  storeLoc=storeLoc, force=force)
            if isinstance(parProj, str):
                return parProj

        elif check.endswith(confObj.projValid[3]):
            parProj = loadProj(confObj, names[0])

        else:
            return check

        parProj.giveChild(names[-1])
        writeProj(parProj)

    writeProj(createdProj)
    confObj.addProj(createdProj)
    writeConf(confObj)
    return createdProj

def writeProj(projObj):
    projDat, projFile = projObj.dumpDat()
    datIO.yamlWrite(projDat, projFile)

def loadProj(confObj, projName, storeType=None, storeLoc=None):
    names=projName.split('.')
    check = confObj.projCheck(projName)
    if isinstance(check, str) and (check.endswith(confObj.projValid[0]) or\
                                   check.endswith(confObj.projValid[1]) or \
                                   check.endswith(confObj.projValid[2])):
        return check
    
    check = confObj.projStoreCheck(projName)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]
    else:
        return check

    loadedProj = projObj.projObj(projName, projFile, dat=datIO.yamlRead(projFile))
    loadedProj.loadDat()
    return loadedProj

def copyProj(confObj, projName, newProjName, deleteold):
    proj = loadProj(confObj,projName)
    if isinstance(proj, str):
        return proj

    check = confObj.projStoreCheck(projName)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]
    else:
        return check

    if deleteold:
        output = deleteProj(confObj, projName)
        if isinstance(output, str):
            return output

    output = makeProj(confObj, newProjName, storeType, storeLoc, None, dat=proj.dumpDat()[0])
    if isinstance(output, str):
        return output

def deleteProj(confObj, projName, storeType=None, storeLoc=None):
    names=projName.split('.')
    check = confObj.projCheck(projName)
    if isinstance(check, str) and (check.endswith(confObj.projValid[0]) or\
                                   check.endswith(confObj.projValid[1]) or \
                                   check.endswith(confObj.projValid[2])):
        return check

    check = confObj.projStoreCheck(projName)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]
    else:
        return check

    childList=[]
    parProj = loadProj(confObj, names[0])
    if isinstance(parProj, str):
        return parProj

    if len(names)>1:
        if cliUtils.getConfirmation('Are you sure you want to'+\
                ' delete this subproject'):

            os.remove(projFile)
            parProj.projDat['children'].remove(names[-1])
            writeProj(parProj)

    elif cliUtils.getConfirmation('Are you sure you want to'+\
            ' delete this project, its folder,'+\
            ' and contents?'):
        
        childList = parProj.projDat['children']
        shutil.rmtree(storeLoc)
        if childList:
            for i in childList:
                del confObj.confDat['session']['projs']['.'.join([projName,i])]

    del confObj.confDat['session']['projs'][projName]

    if confObj.confDat['session']['active']==projName:
        makeActive(confObj)

    writeConf(confObj)

def copyTask(confObj, projObj, taskName, newProjObj=None, newTaskName=None, *args, **kwargs):
    if not newtaskname:
        newtaskname = taskname

    if newtaskproj:
        newproj = loadProj(ctxObjs['confObj'],newtaskproj)
        if isinstance(newproj, str):
            return proj

        output = makeTask(newproj, newtaskname, None, task)
        if isinstance(output, str):
            return output
    else:
        output = makeTask(proj, newtaskname, None, task)
        if isinstance(output, str):
            return output

    if deleteold:
        output = deleteTask(proj, taskname)
        if isinstance(output, str):
            return output

def updateFiles(confObj, projName=None, *args, **kwargs):
    if not projName:
        for key, value in confObj.confDat['session']['projs'].items():
            proj = loadProj(confObj,key)
            if isinstance(proj, str):
                return proj

            cliUtils.printToCli('Updating project: ' + key)
            for key, value in proj.projDat['tasks'].items():
                if 'children' in value.taskDat and not value.taskDat['children']:
                    del value.taskDat['children']

                if 'parent' in value.taskDat and not value.taskDat['parent']:
                    del value.taskDat['parent']

            writeProj(proj)

    else:
        proj = loadProj(confObj,projName)
        writeProj(proj)

def makeMilestone(projName):
    pass

def promote(confObj, newProjName, parProj, taskObj):
    check = confObj.projCheck(newProjName)
    if isinstance(check, str) and not check == confObj.projValid[3]:
        return check

    check = confObj.projStoreCheck(parProj)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]
    else:
        return check
    
    newProj = makeProj(confObj, projName, storeType, storeLoc, None, None)
    if isinstance(newProj, str):
        return newProj

    taskDat = taskObj.dumpDat()
    for key, value in taskDat.items():
        if (key in newProj.projDat\
                and not key == 'parent'\
                and not key == 'children'\
                and not key == 'assignee'\
                and not key == 'name'):
            newProj.projDat[key]=value
        if key == 'assignee':
            for i, j in taskDat['assignee'].items():
                newProj.projDat['team'][i]=j

    writeProj(newProj)

def demote(confObj, proj, parentproj, taskname):
    output = parentproj.makeTask(taskname)
    if isinstance(output, str):
        return output

    for key, value in proj.projDat.items():
        if (key in parentproj.projDat\
                and not key == 'parent'\
                and not key == 'children'\
                and not key == 'assignee'\
                and not key == 'name'):
            output.taskDat[key]=value

    writeProj(parentProj)
