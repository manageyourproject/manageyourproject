import os
import math
import shutil
import datetime as dt

from myp import projObj
from myp import confObj
from myp.utilities import datIO

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
        if isinstance(check, str):
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

def newProj():
    pass

def deleteProj():
    pass

def getProjDat():
    pass

def writeProjDat():
    pass

def projCheck(confObj, projName):
    names = projName.split('.')
    if len(names) > 1:
        if len(names) > 2:
            return 'Can\'t subprojects can\'t have children'
        elif names[0]==names[-1]:
            return 'Can\'t have identically named project and subproject'
    elif not projName in confObj.confDat['session']['projs']:
        return 'Project does not exist'
    else:
        return True
