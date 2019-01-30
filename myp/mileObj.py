import os
import shutil
import datetime

from myp.scripts import cliUtils
from myp.utilities import dictUpdate as du

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
            self.update(mileDat)
            self.mileDat['name']=mileName

    def newMile(self):
        mileDat = {'name':self.name}
        self.update(mileDat)

    def dumpDat(self):
        return self.mileDat

    def update(self, dat):
        self.mileDat.update(du.update(self.mileDat, dat))

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
