# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import click
import datetime
from ruamel.yaml import YAML

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

    def newProj(self, confObj):
        if not os.path.exists(self.projDir):
            os.makedirs(self.projDir)

        if len(self.names) > 1 and \
                self.names[0]==self.names[-1]:
            raise click.ClickException(\
                    'Can\'t have identically '+\
                    'named project and subproject')

        if os.path.isfile(self.projPath):
            if click.confirm('Project Already Exists.' +
                    '\nWould you like to overwrte it?',
                    abort=True):
                shutil.rmtree(self.projPath)
                os.makedirs(self.projPath)

        elif not os.path.exists(self.projPath):
            os.makedirs(self.projPath)

        self.projDat={
                'name':self.names[-1],
                'parent':'none',
                'children':[],
                'creator':confObj.confDat['user']['name'],
                'datecreated':datetime.datetime.now(\
                        datetime.timezone.utc).isoformat(),
                'team':{
                    confObj.confDat['user']['name']:{
                        'cost':'0'
                    },
                },
                'completion':'',
                'tasks':{},
                'notes':{}
                }
        if len(self.names) > 1:
            self.projDat['parent']=self.names[0]
            parObj = projObj(confObj, self.names[0], None)
            if not os.path.isfile(self.projPath):
                parObj.newProj(confObj)

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
        if not os.path.isfile(self.projFile):
            raise click.ClickException(\
                    'No project/subproject by that name')
        else:
            with open(self.projFile, 'r') as fp:
                self.projDat = yaml.load(fp)

    def newTask(self, taskName):
        taskName=taskName.split('.')
        if len(taskName) > 1 and taskName[0]==taskName[-1]:
            raise click.ClickException(\
                    'Can\'t have identically'+\
                    ' named task and subtask')

        if taskName[-1] in self.projDat['tasks']:
            raise click.ClickException(\
                    'A task by that name already exists')
        else:
            self.projDat['tasks'][taskName[-1]]={
                    'parent':[],
                    'children':[],
                    'dependency':[],
                    'datecreated':datetime.datetime.\
                            now(datetime.timezone.utc\
                            ).isoformat(),
                    'status':'',
                    'started':'',
                    'timeSpent':0,
                    'sessions':[],
                    'assignee':'',
                    'deadline':'',
                    }
            if len(taskName) > 1:
                self.projDat['tasks'][taskName[-1]\
                        ]['parent'].append(taskName[0])
                self.projDat['tasks'][taskName[0]\
                        ]['children'].append(taskName[-1])
            self.writeProj()

    def startTask(self, taskName):
        if taskName not in self.projDat['tasks']:
            if click.confirm('No task by that name'+\
                    ' exists. Would you like to create it?',\
                    abort=True):
                self.newTask(taskName)

        self.projDat['tasks'][taskName]['status'] =\
                'active'
        self.projDat['tasks'][taskName]['started'] =\
                datetime.datetime.now(datetime.\
                timezone.utc).isoformat()
        self.writeProj()

    def stopTask(self, taskName):
        if not self.\
                projDat['tasks'][taskName]['started']:
            self.projDat['tasks'][taskName]['status']=\
                    'in-progress'
            raise click.ClickException('That task isn\'t running')
        else:
            self.projDat['tasks'][taskName]['status']=\
                    'in-progress'
            timeDuo = [self.projDat['tasks'][taskName]['started'],\
                    datetime.datetime.now(datetime.timezone.\
                    utc).isoformat()]
            self.projDat['tasks'][taskName]['sessions'].\
                    append(timeDuo)
            self.projDat['tasks'][taskName]['started']=''
            self.projDat['tasks'][taskName]['timeSpent']=\
                    self.projDat['tasks'][taskName\
                    ]['timeSpent']+((datetime.datetime.\
                    fromisoformat(timeDuo[1])-datetime.\
                    datetime.fromisoformat(timeDuo[0])).\
                    total_seconds())
            self.writeProj()

    def finishTask(self, taskName):
        if 'finished' == self.projDat['tasks'][taskName\
                ]['status']:
            raise click.ClickException('That task is'+\
                    ' already finished')
        else:
            self.projDat['tasks'][taskName]['status']='finished'
            if self.projDat['tasks'][taskName]['started']:
                timeDuo = [self.projDat['tasks'][taskName\
                        ]['started'],datetime.datetime.\
                        now(datetime.timezone.utc).\
                        isoformat()]
                self.projDat['tasks'][taskName\
                        ]['sessions'].append(timeDuo)
                self.projDat['tasks'][taskName\
                        ]['timeSpent']=self.projDat['tasks'\
                        ][taskName]['timeSpent']+((datetime.\
                        datetime.fromisoformat(timeDuo[1])-\
                        datetime.datetime.fromisoformat(\
                        timeDuo[0])).total_seconds())

            if self.projDat['tasks'][taskName]['children']:
                for i in self.projDat['tasks'][taskName\
                        ]['children']:
                    self.finishTask(i)

            self.projDat['tasks'][taskName]['started']=''
            self.writeProj()
