# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import datetime

class projObj:
    def __init__(self, projName, projFile):
        self.projName = projName
        self.projFile = projFile
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

    def newProj(self, confObj):
        self.projDat=self.defaultProj()
        self.projDat['name'] = self.projName
        self.projDat['creator'] = confObj.confDat['user']['name']
        self.projDat['datecreated'] = datetime.datetime.now(\
                        datetime.timezone.utc).isoformat()
        self.projDat['team'][confObj.confDat['user']['name']]={
                'contact': confObj.confDat['user']['email'],
                'cost': confObj.confDat['user']['cost'],
                }
        
    def dumpProj(self):
        return [self.projDat, self.projFile]

    def loadProj(self, dat):
        self.projDat = dat

    def giveParent(self, parName):
        self.projDat['parent'] = parName
        if 'children' in self.projDat:
            del self.projDat['children']

    def giveChild(self, childName):
        self.projDat['children'].append(childName)
        if 'parent' in self.projDat:
            del self.projDat['parent']
