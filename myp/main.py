import os
import sys
import math
import click
import shutil
import datetime

from collections import OrderedDict

from myp import confObj
from myp import projObj
from myp import taskObj
from myp.scripts import cli
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
    cli.printToCli('No config file found.')
    cli.getConfirmation('Would you like to create one?')
    name = cli.getInput('Name:')
    email = cli.getInput('Email:')
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
        if not force and cli.getConfirmation(check+\
                '\nWould you like to overwrite it?'):
            confObj.deleteProj(projName)
        elif force:
            confObj.deleteProj(projName)

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
                cli.getConfirmation('Parent ' + check + '\nWould you like to create it?')

            createdProj.giveParent(names[0])
            parProj = confObj.addProj(names[0], storeType=StoreType,\
                                  storeLoc=storeLoc, force=force)
            if isinstance(parProj, str):
                return parProj

        elif check.endswith(confObj.projValid[3]):
            parProj = confObj.loadProj(names[0])

        else:
            return check

        parProj.giveChild(names[-1])
        writeProj(parProj)

    writeProj(createdProj)
    confObj.addProj(createdProj)
    writeConf(confObj)

def writeProj(projObj):
    projDat, projFile = projObj.dumpProj()
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

    output = makeProj(confObj, newProjName, storeType, storeLoc, None, dat=proj.dumpProj()[0])
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

def copyTask(confObj, projObj, taskName, newProjObj=None, newTaskName=None, *args, **kwargs):
    pass

def updateFiles(confObj, projName=None, *args, **kwargs):
    if not projName:
        for key, value in confObj.confDat['session']['projs'].items():
            proj = loadProj(confObj,projName)
            if isinstance(proj, str):
                return proj

            writeProj(proj)

    else:
        proj = loadProj(confObj,projName)
        writeProj(proj)

def makeMilestone(projName):
    pass

def promote(confObj, projName, taskParProj, taskName):
    check = projCheck(confObj, taskParProj.projName, None, None)
    if isinstance(check, str) and not check == confObj.projValid[3]:
        return check

    check = projStoreCheck(confObj, taskParProj.projName, None, None)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]
    else:
        return check
    
    output = makeProj(confObj, projName, storeType, storeLoc, None, None)
    if isinstance(output, str):
        return output

    newProj = loadProj(confObj, projName)
    if isinstance(output, str):
        return newProj

    for key, value in taskParProj.projDat['tasks'][taskName].items():
        if (key in newProj.projDat\
                and not key == 'parent'\
                and not key == 'children'\
                and not key == 'assignee'\
                and not key == 'name'):
            newProj.projDat[key]=value
        if key == 'assignee':
            for i, j in taskParProj.projDat['tasks'][taskName]['assignee'].items():
                newProj.projDat['team'][i]=j

    writeProj(newProj)

def demote(confObj, proj, parentproj, taskname):
    output = makeTask(parentproj, taskname, None, None)
    if isinstance(output, str):
        raise click.ClickException(output)

    parentproj = loadProj(confObj, parentproj.projName)
    if isinstance(parentproj, str):
        return parentproj

    for key, value in proj.projDat.items():
        if (key in parentproj.projDat\
                and not key == 'parent'\
                and not key == 'children'\
                and not key == 'assignee'\
                and not key == 'name'):
            parentproj.projDat['tasks'][taskname][key]=value
