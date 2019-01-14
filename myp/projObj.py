# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import datetime

from myp import taskObj
from myp.scripts import cliUtils

class projObj:
    def __init__(self, projName, projFile, confObj=None, dat=None, *args, **kwargs):
        self.name = projName
        self.taskValid = [\
                'Subtasks can\'t have children',
                'Can\'t have identically named task and subtask',
                ' does not exist',
                ' already exists',
                ]
        self.projFile = projFile
        self.projDat = {
            'name':'',
            'creator':'',
            'description':'',
            'depends':[],
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
            self.newProj(confObj)
        elif dat:
            self.loadProj(dat)
            self.projDat['name']=projName

    def newProj(self, confObj):
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
        self.projDat.update(projDat)
        
    def dumpProj(self):
        datDump = self.projDat
        for key, value in datDump['tasks'].items():
            datDump['tasks'][key]=value.dumpTask()

        return [datDump, self.projFile]

    def loadProj(self, dat):
        self.projDat.update(dat)
        for key, value in self.projDat['tasks'].items():
            self.projDat['tasks'][key]=taskObj.taskObj(taskName=key, taskDat=value)

    def giveParent(self, parName):
        par = {'parent': parName}
        self.projDat.update(par)
        if 'children' in self.projDat:
            del self.projDat['children']

    def giveChild(self, childName):
        if not 'children' in self.projDat:
            chil = {'children':[childName]}
            self.projDat.update(chil)
        else:
            self.projDat['children'].append(childName)

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
        if isinstance(check, str) and (check.endswith(self.taskValid[0]) or\
                                       check.endswith(self.taskValid[1]) or\
                                       check.endswith(self.taskValid[2])):
            return check

        elif isinstance(check, str) and check.endswith(self.taskValid[3]):
            if len(names)>1:
                if not force:
                    cliUtils.getConfirmation('Are you sure you want to delete this subtask?')

                self.projDat['tasks'][names[0]].taskDat['children'].remove(names[-1])
            elif 'children' in self.projDat['tasks'][taskName]:
                if not force:
                    cliUtils.getConfirmation('Are you sure you want to delete this task and subtasks?')

                children = self.projDat['tasks'][taskName].taskDat['children']
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
