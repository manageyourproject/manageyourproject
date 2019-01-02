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

class confObj:
    def __init__(self, cfg):
        self.cfg = cfg     # getting default path
        self.cfgFile = os.path.join(self.cfg, 'config.yaml')           # default file location
        self.cfgProj = os.path.join(self.cfg, 'projects')             # default project path
        self.confDat = {}                               # the confdat "dict"

    def defaultConf(self):
        defaultConf = {
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
        return defaultConf

    def newConf(self, name, email):
        self.confDat = self.defaultConf()

        self.confDat['user']['name'] = name
        self.confDat['user']['email'] = email
        self.confDat['session']['defaultprojpath']=self.cfgProj

    def loadDat(self, dat):
        self.confDat = dat

    def dumpDat(self):
        return [self.confDat, self.cfgFile]

    def trackProj(projName, storeType, storeLoc):
        self.confDat['session']['projs'][projName]={
                'storeType':storeType,
                'storeLoc':storeLoc,
                }
