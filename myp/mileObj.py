import os
import shutil
import datetime

from myp.scripts import cliUtils

class mileObj:
    def __init__(self, mileName, mileDat=None, *args, **kwargs):
        self.name=mileName
        self.mileDat={
            'name':'',
            'description':'',
            'contributesto':[],
            'dependson':[],
            'datecreated':'',
            'deadline':'',
            'notes':[],
        }
        if not mileDat:
            self.newMile()
        else:
            self.update(dict(mileDat))
            self.taskDat['name']=taskName

    def newTask(self):
        mileDat = {'name':self.name}
        self.mileDat.update(mileDat)

    def dumpDat(self):
        return self.mileDat

    def update(self, dat):
        self.mileDat.update(dat)

    def addDepends(self, depends):
        if not isinstance(depends, list):
            depends = [depends]
        for i in depends:
            self.mileDat['dependson'].append(depends)

    def addContributes(self, contributes):
        if not isinstance(contributes, list):
            contributes = [contributes]
        for i in contributes:
            self.mileDat['contributesto'].append(contributes)
