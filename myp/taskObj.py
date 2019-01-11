import os
import shutil
import datetime

class taskObj:
    def __init__(self, taskName, taskDat={}):
        self.taskDat = taskDat
        self.name=taskName

    def defaultTask(self):
        defaultTask = {
            'name':'',
            'parent':None,
            'children':[],
            'contributesto':[],
            'depends':[],
            'datecreated':'',
            'status':'in-progress',
            'started':'',
            'timeSpent':0,
            'sessions':[],
            'assignee':{},
            'assetsused':{},
            'deadline':'',
            'urgency':'',
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

    def newTask(self, assignee):
        self.taskDat = self.defaultTask()
        self.taskDat['name']=self.name
        self.taskDat['assignee'] = {assignee:{},}
        self.taskDat['datecreated']=datetime.\
            datetime.now(datetime.timezone.utc).isoformat()

    def dumpTask(self):
        return self.taskDat


