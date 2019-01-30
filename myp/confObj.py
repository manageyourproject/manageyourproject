# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

# confObj is the configuration object that gets instantiated
# then held for execution of different commands. It holds
# any configuration information like printout style, project
# paths, currently active projects, and user. It uses the
# python3 configparser module to read and create .ini files.
# The program never stays running after completeying a task
# so everything is done through files

import os
import sys

from myp.utilities import dictUpdate as du

class confObj:
    def __init__(self, cfg, name=None, email=None, dat=None, *args,**kwargs):
        self.projValid = [\
                'Subprojects can\'t have children',
                'Can\'t have identically named project and subproject',
                ' does not exist',
                ' already exists',
                ]
        self.cfg = cfg     # getting default path
        self.cfgFile = os.path.join(self.cfg, 'config.yaml')           # default file location
        self.cfgProj = os.path.join(self.cfg, 'projects')             # default project path
        self.confDat = {                               # the confdat "dict"
            'user':{
                'name':'',
                'email':'',
                'cost':0,
            },
            'session':{
                'defaultstoretype':'yaml',
                'defaultprojpath':'',
                'projs':{},
                'active':'',
                'listformat':{
                    'Project Name': 'name',
                    'Owner': 'creator',
                    'Created': 'datecreated',
                },
            }
        }
        if not dat and name and email:
            self.newConf(name, email)
        elif dat:
            self.confDat.update(du.update(self.confDat, dat))

    def newConf(self, name, email):
        confDat = {
            'user':{
                'name':'',
                'email':''
            },
            'session':{
                'defaultprojpath':''
            }
        }
        confDat['user']['name'] = name
        confDat['user']['email'] = email
        confDat['session']['defaultprojpath']=self.cfgProj
        self.confDat.update(du.update(self.confDat, confDat))

    def dumpDat(self):
        return [self.confDat, self.cfgFile]

    def addProj(self, projObj, storeType, storeLoc, *args, **kwargs):
        storeType = projObj.projDat['storeType']
        storeLoc = projObj.projDat['storeLoc']
        self.confDat['session']['projs'][projObj.name]={
            'storeType':storeType,
            'storeLoc':storeLoc,
        }

    def projCheck(self, projName, storeType=None, storeLoc=None,\
                  *args, **kwargs):
        names=projName.split('.')
        outStr = ''
        if len(names) > 1:
            if len(names) > 2:
                outStr = self.projValid[0]
            elif names[0]==names[-1]:
                outStr = self.projValid[1]

        if not projName in self.confDat['session']['projs']:
            outStr = 'Project ' + projName + self.projValid[2]
        else:
            outStr = 'Project ' + projName + self.projValid[3]

        return outStr

    def projStoreCheck(self, projName, storeType=None, storeLoc=None):
        names=projName.split('.')
        if projName in self.confDat['session']['projs']:
            storeType = self.confDat['session']['projs'][projName]['storeType']
            storeLoc = self.confDat['session']['projs'][projName]['storeLoc']
            projFile = os.path.join(storeLoc, names[-1]+'.yaml')
            return [storeType, storeLoc, projFile]

        elif not storeType:
            storeType = self.confDat['session']['defaultstoretype']

        if storeType == 'yaml':
            if not storeLoc:
                storeLoc = os.path.join(self.confDat['session']['defaultprojpath'], names[0])
            elif storeLoc:
                storeLoc = os.path.normpath(storeLoc)

            projFile = os.path.join(storeLoc, names[-1]+'.yaml')
            if not os.path.exists(storeLoc):
                os.makedirs(storeLoc)

        if storeType == 'yaml':
            return [storeType, storeLoc, projFile]
        else:
            return 'Can\'t load that store type'
