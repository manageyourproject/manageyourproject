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
import click
from ruamel.yaml import YAML
from colorama import Fore, Back, Style

class confObj:
    def __init__(self, progPath):
        self.cfg = progPath     # getting default path
        self.cfgFile = os.path.join(self.cfg, 'config.yaml')           # default file location
        self.cfgProj = os.path.join(self.cfg, 'projects')             # default project path
        self.confDat = {}                               # the confdat "dict"
        self.readConf()                                 # calls the read function

    def defaultConf(self):
        defaultConf = {
                'user':{
                'name':'',
                'email':'',
                'cost':0,
            },
            'session':{
                'defaultprojpath':'',
                'projpath':{},
                'active':'',
                'listformat':{
                    'Project Name': 'name',
                    'Owner': 'creator',
                    'Created': 'datecreated',
                },
            }
        }
        return defaultConf

    def newConf(self):
        yaml=YAML()
        if not os.path.exists(self.cfg):                # check if the config file exists
            os.makedirs(self.cfg)                       # create it if unfound

        self.confDat = self.defaultConf()

        self.confDat['user']['name'] = click.prompt(\
                'Full Name', type=str)                  # get user parameters
        self.confDat['user']['email'] = click.prompt(\
                'E-mail Address', type=str)
        self.confDat['session']['defaultprojpath']=self.cfgProj

        self.writeConf()                                # write the file

    def writeConf(self):                                # the write file function
        yaml=YAML()
        with open(self.cfgFile, 'w') as fp:
            yaml.dump(self.confDat, fp)


    def readConf(self):                                 # the read file function
        yaml=YAML()
        if not os.path.isfile(self.cfgFile):
            if click.confirm('No Config file found.' +
                    '\nWould you like to create it ' +
                    'and enter a user and email address?',
                    abort=True):                        # if no file can be found
                self.newConf()                          # ask if one should be made

        else:
            with open(self.cfgFile, 'r') as fp:
                self.confDat = yaml.load(fp)             # if it is found, read it

    def makeActive(self, projname=None):                # mark a project as active
        self.confDat['session']['active']=projname
        self.writeConf()

    def printActive(self):                              # print the active project
        if self.confDat['session']['active']:
            click.echo('Current active project: ' +\
                    self.confDat['session']['active'])
        else:
            click.echo('There are no currently'+\
                    ' active projects')                 # ...if there is one

