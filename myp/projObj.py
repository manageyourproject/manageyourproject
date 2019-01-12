# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import datetime

class projObj:
    def __init__(self, projName, projFile, confObj=None, dat=None, *args, **kwargs):
        self.name = projName
        self.projFile = projFile
        self.projDat = {
            'name':'',
            'parent':None,
            'children':[],
            'creator':'',
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
            self.projDat.update(dat)

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
        return [self.projDat, self.projFile]

    def loadProj(self, dat):
        self.projDat.update(dat)

    def giveParent(self, parName):
        self.projDat['parent'] = parName
        if 'children' in self.projDat:
            del self.projDat['children']

    def giveChild(self, childName):
        self.projDat['children'].append(childName)
        if 'parent' in self.projDat:
            del self.projDat['parent']

