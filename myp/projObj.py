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
            'notes':{},
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

    def projFromDict(self, confObj, projDict):
        pass


    def newProj(self, confObj):
        if self.projExists():
            if click.confirm('Project already Exists.' +
                    '\nWould you like to overwrte it?',
                    abort=True):
                shutil.rmtree(self.projPath)
                os.makedirs(self.projPath)

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

    def projAddTask(self, task):
        self.projDat['tasks']
