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

def newProj(confObj, projName, storeType, storeLoc, overwrite):
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
            newProj(confObj, names[0], storeType, storeLoc)
        else:
            return check

    confObj.trackProj(projName, storeType, storeLoc)

    self.projPath = os.path.\
        join(self.projDir,self.names[0])
    self.projFile = os.path.\
            join(self.projPath,\
            self.names[-1]+'.yaml')

def deleteProj():
    pass

def loadProjDat(confObj, ):
    
    pass

def writeProjDat():
    pass

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
