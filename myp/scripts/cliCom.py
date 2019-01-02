# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3


import click

def proTaExist():
    if len(self.names) > 1 and \
            self.names[0]==self.names[-1]:
        raise click.ClickException(\
                'Can\'t have identically '+\
                'named project and subproject')

def printActive(active):
    if active:
        click.echo('Current active project: ' + active)
    else:
        click.echo('There are currently no active projects')     # ...if there is one
