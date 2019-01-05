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

def writeConf(confObj):
    confDat, confLoc = confObj.dumpDat()
    datIO.yamlWrite(confDat, confLoc)

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

def makeProj(confObj, projName, storeType, storeLoc, overwrite, dat=None):
    names=projName.split('.')
    check = projCheck(confObj, projName)
    if isinstance(check, str) and (check == this.projValid[0] or\
                                   check == this.projValid[1]):
        return check
    
    elif check == this.projValid[3]:
        if not overwrite and not dat and not click.confirm('Project already exists.\n'+\
                'Would you like to overwrite it?'):
            return check
        elif dat and not overwrite:
            return check
        else:
            deleteProj(confObj, projName)

    check = projStoreCheck(confObj, projName)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]
    else:
        return check

    if len(names)>1:
        check = projCheck(confObj, names[0])
        if check == this.projValid[2] and click.confirm(\
                'Parent project doesn\'t exists.\n'+\
                'Would you like to create it?', abort=True):
            output = makeProj(confObj, names[0], storeType, storeLoc, overwrite, None)
            if isinstance(output, str):
                return output

        elif not check == this.projValid[3]:
            return check

    confObj.trackProj(projName, storeType, storeLoc)
    if not dat:
        createdProj = projObj.projObj(projName, projFile)
        createdProj.newProj(confObj)
    else:
        createdProj = projObj.projObj(projName, projFile, dict(dat))
        createdProj.projDat['name'] = projName
    
    if len(names)>1:
        createdProj.giveParent(names[0])
        parProj = loadProj(confObj, names[0])
        if isinstance(parProj, str):
            return parProj
        else:
            parProj.giveChild(names[-1])
            writeProj(parProj)
    else:
        if 'parent' in createdProj.projDat:
            del createdProj.projDat['parent']
        if not 'children' in createdProj.projDat:
            createdProj.projDat['children'] = []


    writeProj(createdProj)
    writeConf(confObj)

def writeProj(projObj):
    projDat, projFile = projObj.dumpProj()
    datIO.yamlWrite(projDat, projFile)

def loadProj(confObj, projName, storeType=None, storeLoc=None):
    check = projCheck(confObj, projName)
    if isinstance(check, str) and not check == this.projValid[3]:
        return check

    check = projStoreCheck(confObj, projName, storeType, storeLoc)
    if isinstance(check, list):
        storeType = check[0]
        storeLoc = check[1]
        projFile = check[2]
    else:
        return check

    loadedProj = projObj.projObj(projName, projFile, datIO.yamlRead(projFile))
    return loadedProj

def copyProj(confObj, projName, newProjName, deleteold):
    proj = loadProj(confObj,projName)
    if isinstance(proj, str):
        return proj

    check = projStoreCheck(confObj, projName)
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

    output = makeProj(confObj, newProjName, storeType, storeLoc, None, proj.dumpProj()[0])
    if isinstance(output, str):
        return output

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

def projCheck(confObj, projName, storeType=None, storeLoc=None):
    names=projName.split('.')
    if len(names) > 1:
        if len(names) > 2:
            return this.projValid[0]
        elif names[0]==names[-1]:
            return this.projValid[1]

    if not projName in confObj.confDat['session']['projs']:
        return this.projValid[2]
    else:
        return this.projValid[3]

def projStoreCheck(confObj, projName, storeType=None, storeLoc=None):
    names=projName.split('.')
    if projName in confObj.confDat['session']['projs']:
        storeType = confObj.confDat['session']['projs'][projName]['storeType']
        storeLoc = confObj.confDat['session']['projs'][projName]['storeLoc']
        projFile = os.path.join(storeLoc, names[-1]+'.yaml')
        return [storeType, storeLoc, projFile]

    elif not storeType:
        storeType = confObj.confDat['session']['defaultstoretype']

    if storeType == 'yaml':
        if not storeLoc:
            storeLoc = os.path.join(confObj.confDat['session']['defaultprojpath'], names[0])
        elif storeLoc:
            storeLoc = os.path.normpath(storeLoc)

        projFile = os.path.join(storeLoc, names[-1]+'.yaml')
        if not os.path.exists(storeLoc):
            os.makedirs(storeLoc)

    if storeType == 'yaml':
        return [storeType, storeLoc, projFile]
    else:
        return 'Can\'t load that store type'

def makeTask(projObj, taskName, assignee, dat=None):
    names = taskName.split('.')
    check = taskCheck(projObj, taskName)
    if isinstance(check, str) and (check==this.taskValid[0] or\
                                   check==this.taskValid[1]):
        return check
    elif isinstance(check, str) and check==this.taskValid[3]:
        if projObj.projDat['tasks'][taskName]['status'] == 'finished':
            if not dat and click.confirm('A finished task by that name already exists\n'+\
                    'would you like to restart it?', abort=True):
                projObj.projDat['tasks'][taskName]['status'] = 'in-progress'
            else:
                return check
        else:
            return check
    else:
        if len(names) > 1:
            if not names[0] in projObj.projDat['tasks']:
                if click.confirm('Parent task doesn\'t exists.\n'+\
                        'Would you like to create it?', abort=True):
                    makeTask(projObj, names[0], assignee, None)

        if not assignee:
            assignee, assigneeDeet = list(projObj.projDat['team'].items())[0]
        elif assignee in projObj.projDat['team']:
            assigneeDeet=projObj.projDat['team'][assignee]
        else:
            return 'That name isn\'t in the team list'
        
        if not dat:
            newTask = taskObj.taskObj(taskName)
            newTask.newTask(assignee)
            newTask.taskDat['assignee'][assignee]=dict(assigneeDeet)
        elif dat:
            newTask = taskObj.taskObj(taskName, dict(dat))

        projObj.projDat['tasks'][taskName] = newTask.dumpTask()
        if len(names) > 1:
            projObj.projDat['tasks'][taskName]['parent'] = names[0]
            projObj.projDat['tasks'][names[0]]['children'].append(names[-1])

        writeProj(projObj)

def makeTaskFromDat(projObj, taskName, dat):
    pass

def loadTask(projObj, taskName):
    check = taskCheck(projObj, taskName)
    if isinstance(check, str) and (check==this.taskValid[0] or\
                                   check==this.taskValid[1] or\
                                   check==this.taskValid[2]):
        return check
    else:
        return projObj.projDat['tasks'][taskName]

def deleteTask(projObj, taskName):
    names = taskName.split('.')
    check = taskCheck(projObj, taskName)
    if isinstance(check, str) and (check==this.taskValid[0] or\
                                   check==this.taskValid[1] or\
                                   check==this.taskValid[2]):
        return check

    elif isinstance(check, str) and check==this.taskValid[3]:
        if len(names)>1:
            if click.confirm('Are you sure you want to delete this subtask?',\
                    abort=True):
                projObj.projDat['tasks'][names[0]]['children'].remove(names[-1])
        elif projObj.projDat['tasks'][taskName]['children']:
            if click.confirm('Are you sure you want to delete this task and subtasks?',\
                    abort=True):
                children = projObj.projDat['tasks'][taskName]['children']
                for i in children:
                    childName = '.'.join([taskName, i])
                    del projObj.projDat['tasks'][childName]
        else:
            if click.confirm('Are you sure you want to delete this task?',\
                    abort=True):
                pass

        del projObj.projDat['tasks'][taskName]
        writeProj(projObj)

def taskCheck(projObj, taskName):
    names=taskName.split('.')
    if len(names) > 1:
        if len(names) > 2:
            return this.taskValid[0]
        elif names[0]==names[-1]:
            return this.taskValid[1]

    if not taskName in projObj.projDat['tasks']:
        return this.taskValid[2]
    else:
        return this.taskValid[3]

def taskStatus(projObj, taskName):
    pass

def startTask(projObj, taskName):
    if projObj.projDat['tasks'][taskName]['status'] == 'finished':
        if click.confirm('That task is already finished.\n'+\
                'would you like to restart it?', abort=True):
            projObj.projDat['tasks'][taskName]['status'] = 'in-progress'
    elif projObj.projDat['tasks'][taskName]['started']:
        return 'Task already running'

    projObj.projDat['tasks'][taskName]['status'] =\
            'active'
    projObj.projDat['tasks'][taskName]['started'] =\
            datetime.datetime.now(datetime.\
            timezone.utc).isoformat()
    writeProj(projObj)

def stopTask(projObj, taskName, confObj):
    if not projObj.projDat['tasks'][taskName]['started']:
        if projObj.projDat['tasks'][taskName]['status']=='finished':
            return 'That task is already completed'
        else: 
            projObj.projDat['tasks'][taskName]['status']=\
                    'in-progress'
            return 'That task isn\'t running'
    else:
        projObj.projDat['tasks'][taskName]['status']=\
                'in-progress'
        timeDuo = [projObj.projDat['tasks'][taskName]['started'],\
                datetime.datetime.now(datetime.timezone.\
                utc).isoformat()]
        projObj.projDat['tasks'][taskName]['sessions'].\
                append({
                    'user': confObj.confDat['user']['name'],
                    'contact': confObj.confDat['user']['email'],
                    'cost': projObj.projDat['team'][confObj.confDat[\
                            'user']['name']]['cost'],
                    'started':timeDuo[0],
                    'stopped':timeDuo[-1],})
        projObj.projDat['tasks'][taskName]['started']=''
        projObj.projDat['tasks'][taskName]['timeSpent']=\
                projObj.projDat['tasks'][taskName\
                ]['timeSpent']+((datetime.datetime.\
                fromisoformat(timeDuo[1])-datetime.\
                datetime.fromisoformat(timeDuo[0])).\
                total_seconds())
        writeProj(projObj)

def finishTask(projObj, taskName, confObj):
    if not projObj.projDat['tasks'][taskName]['status'] == 'in-progress':
        if projObj.projDat['tasks'][taskName]['status'] == 'finished':
            return 'That task is already completed'
        else: 
            stopTask(projObj, taskName, confObj)

    if projObj.projDat['tasks'][taskName]['children']:
        for i in projObj.projDat['tasks'][taskName\
                ]['children']:
            finishTask(projObj, '.'.join([taskName,i]), confObj)

    projObj.projDat['tasks'][taskName]['status']='finished'
    writeProj(projObj)

def promote(projName, taskParProj, taskName, confObj):
    for key, value in proj.projDat['tasks'][taskName].items():
        if (key in newProj.projDat\
                and not key == 'parent'\
                and not key == 'children'\
                and not key == 'assignee'):
            newProj.projDat[key]=value

def demote(projName, taskParProj, taskName, confObj):
    for key, value in proj.projDat.items():
        if (key in newProj.projDat\
                and not key == 'parent'\
                and not key == 'children'\
                and not key == 'assignee'):
            newParProj.projDat['tasks'][taskName][key]=value
