# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import click
import shutil
import datetime
from ruamel.yaml import YAML
from collections import OrderedDict

class projObj:
    def __init__(self, confObj, projName, projpath):
        self.names=projName.split('.')
        if not projName in confObj.\
                confDat['session']['projpath']:
            if projpath:
                self.projDir = os.path.normpath(projpath)
                confObj.confDat['session']['projpath'\
                        ][projName]=projpath
            else:
                self.projDir = confObj.\
                        confDat['session']['defaultprojpath']
                confObj.confDat['session']['projpath'\
                        ][projName]=confObj.confDat['session'\
                        ]['defaultprojpath']
        else:
            self.projDir=confObj.confDat['session']['projpath'\
                        ][projName]

        self.projPath = os.path.\
            join(self.projDir,self.names[0])
        self.projFile = os.path.\
                join(self.projPath,\
                self.names[-1]+'.yaml')

        self.projDat=None

    def defaultProj(self):
        defaultProj = {
            'name':'',
            'parent':None,
            'children':[],
            'creator':'',
            'datecreated':'',
            'team':{},
            'completion':'',
            'tasks':{},
            'notes':[],
            'progress':{},
            'milestones':{},
            'assets':{},
            'currentformat':{\
                'Task Name':'name',
                'Total Time': 'timeSpent',
                'Assigned To': 'assignee'
                }
        }
        return defaultProj


    def defaultTask(self):
        defaultTask = {
            'parent':None,
            'children':[],
            'dependency':[],
            'datecreated':'',
            'status':'in-progress',
            'started':'',
            'timeSpent':0,
            'sessions':[],
            'assignee':{},
            'assetsused':{},
            'deadline':'',
            'recurs':{
                'rate':0,
                'frame':'day'
                    },
            'timeinfo':{
                'optimisticComp':'',
                'probableComp':'',
                'pessimisticComp':'',
                'slack':'',
            },
            'notes':[],
            }
        return defaultTask

    def taskExists(self, taskName):
        if len(taskName) > 1 and taskName[0]==taskName[-1]:
            raise click.ClickException(\
                    'Can\'t have identically'+\
                    ' named task and subtask')

        return taskName[-1] in self.projDat['tasks']

    def projExists(self):
        if len(self.names) > 1 and \
                self.names[0]==self.names[-1]:
            raise click.ClickException(\
                    'Can\'t have identically '+\
                    'named project and subproject')

        return os.path.isfile(self.projFile)

    def newProj(self, confObj):

        if len(self.names) > 1:
            parObj = projObj(confObj, self.names[0], None)
            if not parObj.projExists():
                if click.confirm('Parent project doesn\'t exists.\n'+\
                        'Would you like to create it?', abort=True):
                    parObj.newProj(confObj)

        if not os.path.exists(self.projPath):
            os.makedirs(self.projPath)

        self.projDat=self.defaultProj()
        self.projDat['name'] = self.names[-1]
        self.projDat['creator'] = confObj.confDat['user']['name']
        self.projDat['datecreated'] = datetime.datetime.now(\
                        datetime.timezone.utc).isoformat()
        self.projDat['team'][confObj.confDat['user']['name']]={
                'contact': confObj.confDat['user']['email'],
                'cost': confObj.confDat['user']['cost'],
                }

        if len(self.names) > 1:
            self.projDat['parent']=self.names[0]

            parObj.readProj()
            parObj.projDat['children'].append(self.names[-1])
            parObj.writeProj()

        self.writeProj()
        
    def writeProj(self):
        yaml = YAML()
        with open(self.projFile, 'w') as fp:
            yaml.dump(self.projDat, fp)

    def readProj(self):
        yaml = YAML()
        if not self.projExists():
            raise click.ClickException(\
                    'No project/subproject by that name')
        else:
            with open(self.projFile, 'r') as fp:
                self.projDat = yaml.load(fp)

    def newTask(self, taskName, assignee):
        taskName=taskName.split('.')

        if self.taskExists(taskName):
            if self.projDat['tasks'][taskName[-1]]['status'] == 'finished':
                if click.confirm('A finished task by that name already exists\n'+\
                        'would you like to restart it?', abort=True):
                    self.projDat['tasks'][taskName[-1]]['status'] = 'in-progress'
            else:
                raise click.ClickException('A task by that name already exists')
        else:
            if len(taskName) > 1:
                if not taskName[0] in self.projDat['tasks']:
                    if click.confirm('Parent task doesn\'t exists.\n'+\
                            'Would you like to create it?', abort=True):
                        self.newTask(taskName[0], assignee)

            self.projDat['tasks'][taskName[-1]] = self.defaultTask()
            self.projDat['tasks'][taskName[-1]]['datecreated']=\
                    datetime.datetime.now(datetime.timezone.utc\
                    ).isoformat(),

            if not assignee:
                assignee, assigneeDeet = list(self.projDat['team'].items())[0]
            elif assignee in self.projDat['team']:
                assigneeDeet=self.projDat['team'][assignee]
            else:
                raise click.ClickException('That name isn\'t in the team list')

            self.projDat['tasks'][taskName[-1]]['assignee'][assignee]=dict(assigneeDeet)
            
            if len(taskName) > 1:
                self.projDat['tasks'][taskName[-1]\
                        ]['parent'] = taskName[0]
                self.projDat['tasks'][taskName[0]\
                        ]['children'].append(taskName[-1])

            self.writeProj()

    def startTask(self, taskName):
        taskName=taskName.split('.')
        if not self.taskExists(taskName):
            if click.confirm('No task by that name'+\
                    ' exists. Would you like to create it?',\
                    abort=True):
                self.newTask('.'.join(taskName), None)
        elif self.projDat['tasks'][taskName[-1]]['status'] == 'finished':
            if click.confirm('That task is already finished.\n'+\
                    'would you like to restart it?', abort=True):
                self.projDat['tasks'][taskName[-1]]['status'] = 'in-progress'
        elif self.projDat['tasks'][taskName[-1]]['started']:
            raise click.ClickException('Task already running')

        self.projDat['tasks'][taskName[-1]]['status'] =\
                'active'
        self.projDat['tasks'][taskName[-1]]['started'] =\
                datetime.datetime.now(datetime.\
                timezone.utc).isoformat()
        self.writeProj()

    def stopTask(self, taskName, confObj):
        taskName=taskName.split('.')
        if not self.taskExists(taskName):
            raise click.ClickException('No task by that name exists')
        elif not self.projDat['tasks'][taskName[-1]]['started']:
            if self.projDat['tasks'][taskName[-1]]['status']=='finished':
                raise click.ClickException('That task is already completed')
            else: 
                self.projDat['tasks'][taskName[-1]]['status']=\
                        'in-progress'
                raise click.ClickException('That task isn\'t running')
        else:
            self.projDat['tasks'][taskName[-1]]['status']=\
                    'in-progress'
            timeDuo = [self.projDat['tasks'][taskName[-1]]['started'],\
                    datetime.datetime.now(datetime.timezone.\
                    utc).isoformat()]
            self.projDat['tasks'][taskName[-1]]['sessions'].\
                    append({
                        'user': confObj.confDat['user']['name'],
                        'contact': confObj.confDat['user']['email'],
                        'cost': self.projDat['team'][confObj.confDat[\
                                'user']['name']]['cost'],
                        'started':timeDuo[0],
                        'stopped':timeDuo[-1],})
            self.projDat['tasks'][taskName[-1]]['started']=''
            self.projDat['tasks'][taskName[-1]]['timeSpent']=\
                    self.projDat['tasks'][taskName[-1]\
                    ]['timeSpent']+((datetime.datetime.\
                    fromisoformat(timeDuo[1])-datetime.\
                    datetime.fromisoformat(timeDuo[0])).\
                    total_seconds())
            self.writeProj()

    def finishTask(self, taskName, confObj):
        taskName=taskName.split('.')
        if not self.taskExists(taskName):
            raise click.ClickException('No task by that name exists')
        elif not self.projDat['tasks'][taskName[-1]]['status'] == 'in-progress':
            if self.projDat['tasks'][taskName[-1]]['status'] == 'finished':
                raise click.ClickException('That task is already completed')
            else: 
                self.stopTask('.'.join(taskName), confObj)

        if self.projDat['tasks'][taskName[-1]]['children']:
            for i in self.projDat['tasks'][taskName[-1]\
                    ]['children']:
                self.finishTask(i, confObj)

        self.projDat['tasks'][taskName[-1]]['status']='finished'
        self.writeProj()

    def deleteTask(self, taskName):
        taskName=taskName.split('.')
        if not self.taskExists(taskName):
            raise click.ClickException('No task by that name exists')
        
        if self.projDat['tasks'][taskName[-1]]['parent']:
            if click.confirm('Are you sure you want to delete this subtask?',\
                    abort=True):
                parTask = self.projDat['tasks'][taskName[-1]]['parent']
                self.projDat['tasks'][parTask]['children'].remove(taskName[-1])
        elif self.projDat['tasks'][taskName[-1]]['children']:
            if click.confirm('Are you sure you want to delete this task and subtasks?',\
                    abort=True):
                children = self.projDat['tasks'][taskName[-1]]['children']
                for i in children:
                    del self.projDat['tasks'][i]
        else:
            if click.confirm('Are you sure you want to delete this task?',\
                    abort=True):
                pass

        del self.projDat['tasks'][taskName[-1]]
        self.writeProj()
