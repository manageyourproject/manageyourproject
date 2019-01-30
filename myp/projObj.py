# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import datetime

from myp import taskObj
from myp.scripts import cliUtils
from myp.utilities import dictUpdate as du

class projObj:
    def __init__(self, projName, projFile, confObj=None, dat=None, *args, **kwargs):
        self.name = projName
        self.taskValid = [\
                'Subtasks can\'t have children',
                'Can\'t have identically named task and subtask',
                ' does not exist',
                ' already exists',
                ]
        self.mileValid = [\
                'Milestones can\'t have children',
                ' does not exist',
                ' already exists',
                ]
        self.projFile = projFile
        self.projDat = {
            'name':'',
            'creator':'',
            'description':'',
            'dependson':[],
            'contributesto':[],
            'datecreated':'',
            'team':{},
            'completion':'',
            'tasks':{},
            'notes':[],
            'progress':{},
            'milestones':{},
            'overallUrg':'',
            'assets':{},
            'currentformat':{
                'Task Name':'name',
                'Total Time': 'timeSpent',
                'Assigned To': 'assignee'
            }
        }
        if not dat and confObj:
            self.newProj(confObj, projName)
        elif dat:
            self.loadDat(dict(dat))
            self.projDat['name']=projName

    def newProj(self, confObj, projName):
        projDat={
            'name':'',
            'creator':'',
            'datecreated':'',
            'team':{},
        }
        projDat['name'] = projName
        projDat['creator'] = confObj.confDat['user']['name']
        projDat['datecreated'] = datetime.datetime.now(\
                        datetime.timezone.utc).isoformat()
        projDat['team'][confObj.confDat['user']['name']]={
                'contact': confObj.confDat['user']['email'],
                'cost': confObj.confDat['user']['cost'],
                }
        self.update(projDat)
        
    def dumpDat(self):
        datDump = self.projDat
        for key, value in datDump['milestones'].items():
            datDump['milestones'][key]=value.dumpDat()

        for key, value in datDump['tasks'].items():
            datDump['tasks'][key]=value.dumpDat()

        return [datDump, self.projFile]

    def loadDat(self, dat=None, *args, **kwargs):
        if dat:
            self.update(dat)

        for key, value in self.projDat['milestones'].items():
            if not isinstance(value, mileObj.mileObj):
                self.projDat['milestones'][key]=mileObj.mileObj(mileName=key, mileDat=value)

        for key, value in self.projDat['tasks'].items():
            if not isinstance(value, taskObj.taskObj):
                self.projDat['tasks'][key]=taskObj.taskObj(taskName=key, taskDat=value)

    def update(self, dat):
        self.projDat.update(du.update(self.projDat, dat))
        self.loadDat()
    
    def giveParent(self, parName):
        par = {'parent': parName}
        self.update(par)
        if 'children' in self.projDat:
            del self.projDat['children']

    def giveChild(self, childName):
        if not 'children' in self.projDat:
            chil = {'children':[childName]}
            self.update(chil)
        else:
            self.projDat['children'].append(childName)

    def addDepends(self, depends):
        if not isinstance(depends, list):
            depends = [depends]
        for i in depends:
            self.projDat['dependson'].append(depends)

    def addContributes(self, contributes):
        if not isinstance(contributes, list):
            contributes = [contributes]
        for i in contributes:
            self.projDat['contributesto'].append(contributes)

    def addMilestone(self, mileName, depends=None, contributes=None, *args, **kwargs):
        check = self.mileCheck(mileName)
        if isinstance(check, str) and (self.mileValid[0] in check) or\
                (self.mileValid[2] in check):
            return check
        else:
            newMile = mileObj.mileObj(mileName)

        if depends:
            newMile.addDepends(depends)
        
        if contributes:
            newMile.addContributes(contributes)

        self.projDat['milestones'][mileName]=newMile

    def addTask(self, taskName, assignee=None, dat=None, force=None, *args, **kwargs):
        names = taskName.split('.')
        check = self.taskCheck(taskName)
        if isinstance(check, str) and (check.endswith(self.taskValid[0]) or\
                                       check.endswith(self.taskValid[1])):
            return check
        elif isinstance(check, str) and check.endswith(self.taskValid[3]):
            if self.projDat['tasks'][taskName].status() == 'finished':
                if not dat:
                    cli.getConfirmation('A finished task by that name already exists\n'+\
                        'would you like to restart it?')
                    self.projDat['tasks'][taskName].status('in-progress')
            else:
                return check
        else:
            assigneeDeet=None
            if not assignee:
                assignee, assigneeDeet = list(self.projDat['team'].items())[0]
            elif assignee in self.projDat['team']:
                assigneeDeet=self.projDat['team'][assignee]
            else:
                return 'That name isn\'t in the team list'

            newTask = taskObj.taskObj(taskName=taskName, taskDat=dat,\
                                      assignee=assignee, assigneeDeet=assigneeDeet)
            if len(names) > 1:
                if not names[0] in self.projDat['tasks']:
                    if not force:
                        cli.getConfirmation('Parent task doesn\'t exists.\n'+\
                            'Would you like to create it?')

                    parTask = self.makeTask(names[0], assignee)
                else:
                    parTask = self.loadTask(names[0])
                        
                newTask.giveParent(names[0])
                parTask.giveChildren(names[-1])

            self.projDat['tasks'][taskName]=newTask
        
        return newTask

    def loadTask(self, taskName):
        names = taskName.split('.')
        check = self.taskCheck(taskName)
        if isinstance(check, str) and (check.endswith(self.taskValid[0]) or\
                                       check.endswith(self.taskValid[1]) or\
                                       check.endswith(self.taskValid[2])):
            return check

        elif isinstance(check, str) and check.endswith(self.taskValid[3]):
            return self.projDat['tasks'][taskName]

    def deleteTask(self, taskName, force=None):
        names = taskName.split('.')
        check = self.taskCheck(taskName)
        task = self.loadTask(taskName).dumpDat()
        if isinstance(check, str) and (check.endswith(self.taskValid[0]) or\
                                       check.endswith(self.taskValid[1]) or\
                                       check.endswith(self.taskValid[2])):
            return check

        elif isinstance(check, str) and check.endswith(self.taskValid[3]):
            if len(names)>1:
                if not force:
                    cliUtils.getConfirmation('Are you sure you want to delete this subtask?')

                parTask = self.loadTask(names[0]).dumpDat()
                parTask['children'].remove(names[-1])
                if not parTask['children']:
                    del parTask['children']
            elif 'children' in task:
                if not force:
                    cliUtils.getConfirmation('Are you sure you want to delete this task and subtasks?')

                children = task['children']
                for i in children:
                    childName = '.'.join([taskName, i])
                    self.deleteTask(childName, force=True)

            else:
                if not force:
                    cliUtils.getConfirmation('Are you sure you want to delete this task?')

            del self.projDat['tasks'][taskName]

    def taskCheck(self, taskName):
        names=taskName.split('.')
        if len(names) > 1:
            if len(names) > 2:
                outStr = self.taskValid[0]
            elif names[0]==names[-1]:
                outStr = self.taskValid[1]

        if not taskName in self.projDat['tasks']:
            outStr = 'Task ' + taskName + self.taskValid[2]
        else:
            outStr = 'Task ' + taskName + self.taskValid[3]

        return outStr

    def mileCheck(self, mileName):
        names=mileName.split('.')
        if len(names) > 1:
            outStr = self.mileValid[0]

        if not mileName in self.projDat['tasks']:
            outStr = 'Milestone ' + mileName + self.mileValid[1]
        else:
            outStr = 'Milestone ' + mileName + self.mileValid[2]

        return outStr
