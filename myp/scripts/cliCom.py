# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3


import click

def printActive(active):
    if active:
        click.echo('Current active project: ' + active)
    else:
        click.echo('There are currently no active projects')     # ...if there is one
