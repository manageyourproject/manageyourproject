import os
import shutil
import datetime

from myp.scripts import cli

class taskObj:
    def __init__(self, taskName, assignee=None, assigneeDeet=None,\
                 taskDat=None, *args, **kwargs):
        self.name=taskName
        self.taskDat={
            'name':'',
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
        }
        if not taskDat and assignee:
            self.newTask(assignee, assigneeDeet)
        else:
            self.taskDat.update(taskDat)
            self.taskDat['name']=taskName

    def newTask(self, assignee, assigneeDeet):
        taskDat = {}
        taskDat['name']=self.name
        taskDat['assignee'] = {assignee:assigneeDeet,}
        taskDat['datecreated']=datetime.datetime.\
            now(datetime.timezone.utc).isoformat()
        self.taskDat.update(taskDat)

    def dumpTask(self):
        return self.taskDat

    def giveParent(self, parName):
        par = {'parent': parName}
        self.taskDat.update(par)
        if 'children' in self.taskDat:
            del self.taskDat['children']

    def giveChild(self, childName):
        if not 'children' in self.taskDat:
            chil = {'children':[childName]}
            self.taskDat.update(chil)
        else:
            self.taskDat['children'].append(childName)

    def status(self, newStatus=None, *args, **kwargs):
        return self.taskDat['status']

    def startTask(self):
        if self.taskDat['status'] == 'finished':
            cli.getConfirmation('That task is already finished.\n would you like to restart it?')
            self.taskDat['status'] = 'in-progress'
        elif self.taskDat['started']:
            return 'Task already running'

        self.taskDat['status'] = 'active'
        self.taskDat['started'] = datetime.datetime.\
            now(datetime.timezone.utc).isoformat()

    def stopTask(self, confObj):
        if not self.taskDat['started']:
            if self.taskDat['status']=='finished':
                return 'That task is already completed'
            else: 
                self.taskDat['status']= 'in-progress'
                return 'That task isn\'t running'
        else:
            self.taskDat['status']='in-progress'
            timeDuo = [self.taskDat['started'],\
                    datetime.datetime.now(datetime.timezone.\
                    utc).isoformat()]
            self.taskDat['sessions'].\
                    append({
                        'user': confObj.confDat['user']['name'],
                        'contact': confObj.confDat['user']['email'],
                        'started':timeDuo[0],
                        'stopped':timeDuo[-1],})
            self.taskDat['started']=''
            self.taskDat['timeSpent'] = self.taskDat['timeSpent']+\
                ((datetime.datetime.fromisoformat(timeDuo[1])-\
                  datetime.datetime.fromisoformat(timeDuo[0])).total_seconds())

    def finishTask(self, projObj, confObj):
        if not self.taskDat['status'] == 'in-progress':
            if self.taskDat['status'] == 'finished':
                return 'That task is already completed'
            else: 
                self.stopTask(confObj)

        if self.taskDat['children']:
            for i in self.taskDat['children']:
                projObj.projDat['.'.join([taskName,i])].finishTask(projObj, confObj)

        self.taskDat['status']='finished'
