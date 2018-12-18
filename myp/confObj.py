# To install, run pip3 install --user --editable ./
# in the same directory as setup.py or dl from pip using myp

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
import configparser
from colorama import Fore, Back, Style

class confObj:
    def __init__(self):
        self.APP_NAME = 'myp'                           # required for default path
        self.cfg = click.get_app_dir(self.APP_NAME)     # getting default path
        self.cfgFile = os.path.join(click.get_app_dir(\
                self.APP_NAME), 'config.ini')           # default file location
        self.cfgProj = os.path.join(click.get_app_dir(\
                self.APP_NAME), 'projects')             # default project path
        self.confDat = configparser.ConfigParser(\
                allow_no_value=True)                    # the confdat "dict"
        self.readConf()                                 # calls the read function

    def newConf(self):
        if not os.path.exists(self.cfg):                # check if the config file exists
            os.makedirs(self.cfg)                       # create it if unfound

        self.confDat['user'] = {                        # conf file structure
                    '; Required Parameters':None,
                    'name': '',
                    'email': ''}
        self.confDat['session'] = {
                '; Required Parameters':None,
                '; Runtime Set':None,
                'active': ''}
        self.confDat['projpath']={}

        self.confDat['user']['name'] = click.prompt(\
                'Full Name', type=str)                  # get user parameters
        self.confDat['user']['email'] = click.prompt(\
                'E-mail Address', type=str)
        self.confDat['session']['projpath'][\
                'default'] = self.cfgProj

        self.writeConf()                                # write the file

    def writeConf(self):                                # the write file function
        with open(self.cfgFile, 'w') as configFile:
            self.confDat.write(configFile)


    def readConf(self):                                 # the read file function
        if not os.path.isfile(self.cfgFile):
            if click.confirm('No Config file found.' +
                    '\nWould you like to create it ' +
                    'and enter a user and email address?',
                    abort=True):                        # if no file can be found
                self.newConf()                          # ask if one should be made

        else:
            self.confDat.read(self.cfgFile)             # if it is found, read it

    def makeActive(self, projname=None):                # mark a project as active
        self.confDat['session']['active']=projname
        self.writeConf()

    def printActive(self):                              # print the active project
        if self.confDat['session']['active']:
            click.echo('Current active project: ' +\
                    self.confDat['session']['active'])
        else:
            click.echo('There are no currently'+\       # ...if there is one
                    ' active projects')

