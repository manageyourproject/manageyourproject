import os
import shutil
import datetime

class taskObj:
    def __init__(self):
        self.names=projName.split('.')

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
