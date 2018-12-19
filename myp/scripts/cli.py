# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import math
import click
import shutil
import datetime as dt
from colorama import Fore, Back, Style

from myp import projObj
from myp import confObj

@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx):
    if ctx.obj is None:
        ctx.obj = dict()

    ctx.obj['confObj'] = confObj.confObj()
    if ctx.invoked_subcommand is None:
        ctx.obj['confObj'].printActive()
        click.echo('Type '+click.style('myp --help',\
                fg='red',bold=True)+' for usage')

@cli.command(help='Initialize a new project')
@click.pass_obj
@click.argument('projname')
@click.option('-pp', '--projpath', default=None,\
        help="Provide a separate path for the project files")
def proj(ctxObjs, projname, projpath):
    ctxObjs['projObj'] = projObj.projObj(\
            ctxObjs['confObj'],projname,projpath)
    ctxObjs['projObj'].newProj(ctxObjs['confObj'])
    ctxObjs['confObj'].makeActive(projname)

@cli.command(help=\
        'List all projects in the project directory')
@click.pass_obj
def list(ctxObjs):
    projs = ctxObjs['confObj'].\
            confDat['session']['projpath']
    termWidth, _ = click.get_terminal_size()
    colAlt = False
    if not projs.items():
        click.echo('No known projects')

    listHead = ''
    cellWidth=int(math.floor(termWidth/\
            len(ctxObjs['confObj'].\
            confDat['session']['listformat']))-\
            len(ctxObjs['confObj'].confDat[\
            'session']['listformat']))

    for i in ctxObjs['confObj'].confDat['session']['listformat']:
        listHead = listHead +'| ' + '{i:<{width}}'.\
                format(i=i, width=cellWidth)

    click.echo(Fore.WHITE+Back.BLACK+click.style(\
            '{:{width}}'.format('='*termWidth,\
            width=termWidth),bold=True, reverse=colAlt))
    click.echo(Fore.WHITE+Back.BLACK+click.style(listHead,\
            bold=True, reverse=colAlt))
    click.echo(Fore.WHITE+Back.BLACK+click.style(\
            '{:{width}}'.format('='*termWidth,\
            width=termWidth),bold=True, reverse=colAlt))
    colAlt = not colAlt
    for keys, value in projs.items():
        listVals = ''
        proj = projObj.projObj(ctxObjs['confObj'],keys, None)
        proj.readProj()
        for i, j in ctxObjs['confObj'].confDat[\
                'session']['listformat'].items():
            field=proj.projDat[j]
            if j == 'datecreated':
                field = dt.datetime.fromisoformat(field).\
                        strftime('%Y/%m/%d')
            listVals = listVals + '| ' + '{i:<{width}}'.format(\
                    i=field, width=cellWidth)

        click.echo(Fore.WHITE+Back.BLACK+click.style(\
                listVals,reverse=colAlt))

        colAlt = not colAlt


@cli.command(help=\
        'Get currently active project, or activate a project')
@click.pass_obj
@click.option('-pn', '--projname', default=None)
def active(ctxObjs, projname):
    if projname:
        ctxObjs['confObj'].makeActive(projname)
    else:
        ctxObjs['confObj'].printActive()

@cli.command(help=\
        'Remove a project and delete the containing folder')
@click.pass_obj
@click.argument('projname')
def remove(ctxObjs, projname):
    if not projname in ctxObjs['confObj'].\
            confDat['session']['projpath']:
        raise click.ClickException('No project by that name')

    elif click.confirm('Are you sure you want to'+\
            ' delete this project, its folder,'+\
            ' and contents?', abort=True):
        
        projDir = os.path.join(ctxObjs['confObj'].\
            confDat['session']['projpath'][\
            projname], projname)
        shutil.rmtree(projDir)
        del ctxObjs['confObj'].\
            confDat['session']['projpath'][\
            projname]
        ctxObjs['confObj'].writeConf()

@cli.command(help='Reset active project')
@click.pass_obj
def reset(ctxObjs):
    ctxObjs['confObj'].makeActive()

@cli.command(help='Create a new task')
@click.pass_obj
@click.argument('taskname', required=True)
@click.option('-pn', '--projname', default=None,\
        help='Name of the project to add the task to')
def task(ctxObjs,taskname,projname):
    if not projname:
        if ctxObjs['confObj'].\
                confDat['session']['active']:
            projname = ctxObjs['confObj'].\
                    confDat['session']['active']
        else:
            projname = click.prompt(\
                    'Enter a project to add the task to')

    ctxObjs['projObj'] = projObj.\
            projObj(ctxObjs['confObj'],projname, None)
    ctxObjs['projObj'].readProj()
    ctxObjs['projObj'].newTask(taskname)
    ctxObjs['confObj'].makeActive(projname)

@cli.command(help='List tasks in active project')
@click.pass_obj
@click.option('-pn', '--projname', default=None,\
        help='Name of project to get tasks from')
def current(ctxObjs,projname):
    if not projname:
        if ctxObjs['confObj'].\
                confDat['session']['active']:
            projname = ctxObjs['confObj'].\
                    confDat['session']['active']
        else:
            projname = click.prompt(\
                    'Enter a project to view its tasks')

    colAlt = False
    termWidth, _ = click.get_terminal_size()
    ctxObjs['projObj'] = projObj.projObj(\
            ctxObjs['confObj'],projname, None)
    ctxObjs['projObj'].readProj()
    ctxObjs['confObj'].makeActive(projname)
    print(ctxObjs['projObj'].projDat[\
            'currentformat'])
    cellWidth=int(math.floor(termWidth/\
            len(ctxObjs['projObj'].projDat[\
            'currentformat']))-len(ctxObjs[\
            'projObj'].projDat['currentformat']))
    listHead = ''
    for i in ctxObjs['projObj'].projDat['currentformat']:
        listHead = listHead + '| ' + '{i:<{width}}'.format(\
                i=i, width=cellWidth)

    click.echo(Fore.WHITE+Back.BLACK+click.style(\
            '{:{width}}'.format('-'*termWidth,\
            width=termWidth),bold=True, reverse=colAlt))
    click.echo(Fore.WHITE+Back.BLACK+click.style(listHead,\
            bold=True, reverse=colAlt))
    click.echo(Fore.WHITE+Back.BLACK+click.style(\
            '{:{width}}'.format('-'*termWidth,\
            width=termWidth),bold=True, reverse=colAlt))
    colAlt = not colAlt
    for key, value in ctxObjs['projObj'].projDat['tasks'].items():
        listVals = ''
        if not value['status'] == 'finished':
            for i, j in ctxObjs['projObj'].\
                    projDat['currentformat'].items():
                listVals = listVals+'| '
                if j == 'name':
                    field = key
                else:
                    field = value[j]

                if j == 'datecreated':
                    field = dt.datetime.fromisoformat(field).\
                            strftime('%Y/%m/%d')
                elif j == 'timeSpent':
                    field = float(field)

                if type(field) is float:
                    listVals = listVals + '{i:<{width}}'.format(\
                            i=field, width=cellWidth, prec=3)
                elif type(field) is int:
                    listVals = listVals + '{i:<{width}}'.format(\
                            i=field, width=cellWidth, prec=2)
                else:
                    listVals = listVals + '{i:<{width}}'.format(\
                            i=field, width=cellWidth)

            click.echo(Fore.WHITE+Back.BLACK+click.style(\
                    listVals, reverse=colAlt))

            colAlt = not colAlt

@cli.command(help='Start tracking time for task')
@click.pass_obj
@click.argument('taskname', required=True)
@click.option('-pn', '--projname', default=None,\
        help='Name of the project holding the task')
def start(ctxObjs, taskname, projname):
    if not projname:
        if ctxObjs['confObj'].\
                confDat['session']['active']:
            projname = ctxObjs['confObj'].\
                    confDat['session']['active']
        else:
            projname = click.prompt(\
                    'Enter a project to add the task to')

    ctxObjs['projObj'] = projObj.\
            projObj(ctxObjs['confObj'],projname, None)
    ctxObjs['projObj'].readProj()
    ctxObjs['projObj'].startTask(taskname)

@cli.command(help='Stop tracking time for task')
@click.pass_obj
@click.argument('taskname')
@click.option('-pn', '--projname', default=None,\
        help='Name of the project holding the task')
def stop(ctxObjs, projname, taskname):
    if not projname:
        if ctxObjs['confObj'].\
                confDat['session']['active']:
            projname = ctxObjs['confObj'].\
                    confDat['session']['active']
        else:
            projname = click.prompt(\
                    'Enter a project to add the task to')

    ctxObjs['projObj'] = projObj.\
            projObj(ctxObjs['confObj'],projname, None)
    ctxObjs['projObj'].readProj()
    ctxObjs['projObj'].stopTask(taskname)

@cli.command(help='Stop tracking time for task')
@click.pass_obj
@click.argument('taskname')
@click.option('-pn', '--projname', default=None,\
        help='Name of the project holding the task')
def finish(ctxObjs, projname, taskname):
    if not projname:
        if ctxObjs['confObj'].\
                confDat['session']['active']:
            projname = ctxObjs['confObj'].\
                    confDat['session']['active']
        else:
            projname = click.prompt(\
                    'Enter a project to add the task to')

    ctxObjs['projObj'] = projObj.\
            projObj(ctxObjs['confObj'],projname, None)
    ctxObjs['projObj'].readProj()
    ctxObjs['projObj'].finishTask(taskname)

@cli.group(help=\
        'Show a gantt chart with current progress')
@click.pass_obj
def gantt(confObj):
    pass

@cli.group(help=\
        'Show a kanban representation of current tasks')
@click.pass_obj
def kanban(confObj):
    pass

@cli.group(help='Show a burndown chart for the defined time')
@click.pass_obj
def burndown(confObj):
    pass

@cli.group(help='Produce a report in selected format')
@click.pass_obj
def publish(confObj):
    pass

@cli.group(help='List all tracked projects')
@click.pass_obj
def listproj(confObj):
    pass

@cli.group(help='Show status of project')
@click.pass_obj
def status(confObj):
    pass

@cli.group(help='Show upcoming work to be done')
@click.pass_obj
def next(confObj):
    pass

@cli.group(help='show a summary for the past week')
@click.pass_obj
def week(confObj):
    pass

@cli.group(help='Show a summary for the past day')
@click.pass_obj
def day(confObj):
    pass

@cli.group(help='Show a summary of the past month')
@click.pass_obj
def month(confObj):
    pass

if __name__ == '__main__':
    cli()
