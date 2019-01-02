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
    def __init__(self, progPath):
        self.cfg = progPath     # getting default path
        self.cfgFile = os.path.join(self.cfg, 'config.yaml')           # default file location
        self.cfgProj = os.path.join(self.cfg, 'projects')             # default project path
        self.confDat = {}

    def defaultConf(self):
        defaultConf = {
                'user':{
                'name':'',
                'email':'',
                'cost':0,
            },
            'session':{
                'defaultprojpath':'',
                'projs':{},
                'active':'',
                'listformat':{
                    'Project Name': 'name',
                    'Owner': 'creator',
                    'Created': 'datecreated',
                },
                'filestore':'yaml',
            }
        }
        return defaultConf

    def loadDat(self, dat):
        self.confDat = dat

    def getDat(self):
        return self.confDat

    def getConfLoc(self):
        return self.cfgFile

    def newConfDat(self, name, email):
        if not os.path.exists(self.cfg):                # check if the config file exists
            os.makedirs(self.cfg)                       # create it if unfound

        self.confDat = self.defaultConf()

        self.confDat['user']['name'] = name
        self.confDat['user']['email'] = email
        self.confDat['session']['defaultprojpath']=self.cfgProj

    def confExists(self):
        return os.path.isfile(self.cfgFile)

    def makeActive(self, projname=None):                # mark a project as active
        self.confDat['session']['active']=projname
        self.writeConf()

    def giveActive(self):                              # print the active project
        return self.confDat['session']['active']

    def projExists(self):

        return os.path.isfile(self.projFile)
