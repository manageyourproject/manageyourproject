# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import math
import click
import shutil
import datetime as dt
from colorama import Fore, Back, Style

from myp import main

@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx):
    APP_NAME = 'myp'                           # required for default path
    cfg = click.get_app_dir(APP_NAME)     # getting default path
    if ctx.obj is None:
        ctx.obj = dict()

    ctx.obj['confObj'] = main.initWConf(cfg)

    if isinstance(ctx.obj['confObj'], str):
        click.echo(ctx.obj['confObj'])
        if click.confirm('Would you like to create it ' +
                'and enter a user and email address?',
                abort=True):                        # if no file can be found

            if not os.path.exists(cfg):                # check if the config file exists
                os.makedirs(cfg)                       # create it if unfound

            name = click.prompt('Name', type=str)
            email = click.prompt('E-mail Address', type=str)
            ctx.obj['confObj'] = main.makeConf(cfg, name, email)

    if ctx.invoked_subcommand is None:
        click.echo(main.getActive(ctx.obj['confObj']))
        click.echo('Type '+click.style('myp --help',\
                fg='red',bold=True)+' for usage')

@cli.command(help=\
        'Get currently active project, or activate a project')
@click.pass_obj
@click.option('-pn', '--projname', default=None)
def active(ctxObjs, projname):
    if projname:
        active = main.makeActive(ctxObjs['confObj'], projname)
        if isinstance(active, str):
            raise click.ClickException(active)

    click.echo(main.getActive(ctxObjs['confObj']))

@cli.command(help='Reset active project')
@click.pass_obj
def reset(ctxObjs):
    active = main.makeActive(ctxObjs['confObj'], None)

@cli.group()
@click.pass_context
def new(ctx):
    pass

@new.command(help='Initialize a new project')
@click.pass_obj
@click.argument('projname')
@click.option('-st', '--storetype', default=None,\
        help='Type of store for the project')
@click.option('-sl', '--storeloc', default=None,\
        help='Location of the store for the project')
@click.option('-f', '--force', is_flag=True,\
        help='Location of the store for the project')
def proj(ctxObjs, projname, storetype, storeloc, force):
    output = main.makeProj(ctxObjs['confObj'], projname, storetype, storeloc, force)
    if isinstance(output, str):
        raise click.ClickException(output)
    
@new.command(help='Create a new task')
@click.pass_obj
@click.argument('taskname', required=True)
@click.option('-pn', '--projname', default=None,\
        help='Name of the project to add the task to')
@click.option('-ta', '--assignee', default=None, help=\
        'Team member the task is assigned to')
def task(ctxObjs,taskname,projname, assignee):
    if not projname:
        projname = main.getActive(ctxObjs['confObj'])
        if not projname:
            projname = click.prompt('Enter a project to add the task to')

    proj = main.loadProj(ctxObjs['confObj'],projname)
    if isinstance(proj, str):
        raise click.ClickException(proj)

    output = main.makeTask(proj, taskname, assignee)
    if isinstance(output, str):
        raise click.ClickException(output)

    active = main.makeActive(ctxObjs['confObj'], projname)
    if isinstance(active, str):
        raise click.ClickException(active)

@cli.group()
@click.pass_context
def list(ctx):
    pass

@list.command(help='List all projects in the project directory')
@click.pass_obj
def proj(ctxObjs):
    projs = ctxObjs['confObj'].\
            confDat['session']['projs']
    termWidth, _ = click.get_terminal_size()
    colAlt = False
    if not projs.items():
        click.echo('No known projects')

    listHead = ''
    cellWidth=int(math.floor(termWidth/\
            len(ctxObjs['confObj'].\
            confDat['session']['listformat']))-2)

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
    for keys, value in sorted(projs.items()):
        listVals = ''
        proj = main.loadProj(ctxObjs['confObj'],keys)
        if isinstance(proj, str):
            raise click.ClickException(proj)

        for i, j in ctxObjs['confObj'].confDat[\
                'session']['listformat'].items():
            
            field=proj.projDat[j]
            if j == 'datecreated':
                field = dt.datetime.fromisoformat(field).\
                        strftime('%Y/%m/%d')

            if j == 'name' and 'parent' in proj.projDat:
                field = field.split('.')[-1]
                listVals = listVals + '|   ' + '{i:<{width}}'.format(\
                        i=field, width=cellWidth-2)
            else:
                listVals = listVals + '| ' + '{i:<{width}}'.format(\
                        i=field, width=cellWidth)

        click.echo(Fore.WHITE+Back.BLACK+click.style(\
                listVals,reverse=colAlt))

        colAlt = not colAlt

@list.command(help='List tasks in active project')
@click.pass_obj
@click.option('-pn', '--projname', default=None,\
        help='Name of project to get tasks from')
def task(ctxObjs,projname):
    if not projname:
        projname = main.getActive(ctxObjs['confObj'])
        if not projname:
            projname = click.prompt('Enter a project to view its tasks')

    proj = main.loadProj(ctxObjs['confObj'],projname)
    if isinstance(proj, str):
        raise click.ClickException(proj)

    active = main.makeActive(ctxObjs['confObj'], projname)
    if isinstance(active, str):
        raise click.ClickException(active)

    colAlt = False
    termWidth, _ = click.get_terminal_size()
    cellWidth=int(math.floor(termWidth/len(proj.projDat['currentformat']))-2)
    listDict={}
    listHead = ''
    for i in proj.projDat['currentformat']:
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
    for key, value in proj.projDat['tasks'].items():
        listVals = ''
        if not value['status'] == 'finished':
            for i, j in proj.\
                    projDat['currentformat'].items():
                listVals = listVals+'| '
                if j == 'name':
                    listDictKey = key
                    field = key
                else:
                    field = value[j]

                if j == 'datecreated':
                    field = dt.datetime.fromisoformat(field).\
                            strftime('%Y/%m/%d')
                elif j == 'timeSpent':
                    field = float(field)
                elif j == 'assignee':
                    assignees = ''
                    for k in dict(value[j]).keys():
                        assignees = assignees + k
                    field = assignees

                if j == 'name' and value['parent']:
                    listDictKey = '.'.join([value['parent'], listDictKey])
                    listVals = listVals + '  ' + '{i:<{width}}'.format(\
                            i=field, width=cellWidth-2, prec=3)
                elif type(field) is float:
                    listVals = listVals + '{i:<{width}}'.format(\
                            i=field, width=cellWidth, prec=3)
                elif type(field) is int:
                    listVals = listVals + '{i:<{width}}'.format(\
                            i=field, width=cellWidth, prec=2)
                else:
                    listVals = listVals + '{i:<{width}}'.format(\
                            i=field, width=cellWidth)

            listDict[listDictKey]=listVals

    for key, value in sorted(listDict.items()):
        click.echo(Fore.WHITE+Back.BLACK+click.style(\
                value, reverse=colAlt))

        colAlt = not colAlt

@cli.group()
@click.pass_context
def delete(ctx):
    pass

@delete.command(help=\
        'Remove a project and delete the containing folder')
@click.pass_obj
@click.argument('projname')
def proj(ctxObjs, projname):
    output = main.deleteProj(ctxObjs['confObj'], projname)
    if isinstance(output, str):
        raise click.ClickException(output)

@delete.command(help='Delete a task')
@click.pass_obj
@click.argument('taskname', required=True)
@click.option('-pn', '--projname', default=None,\
        help='Name of the project to delete the task from')
def task(ctxObjs,taskname,projname):
    if not projname:
        if ctxObjs['confObj'].\
                confDat['session']['active']:
            projname = ctxObjs['confObj'].\
                    confDat['session']['active']
        else:
            projname = click.prompt(\
                    'Enter a project to delete the task from')

    
    proj = projObj.\
            projObj(ctxObjs['confObj'],projname, None)
    proj.readProj()
    proj.deleteTask(taskname)

@cli.group()
@click.pass_context
def copy(ctx):
    pass

@copy.command(help='Create a copy project. Also can be used to make a project parent-less or make it a child of another project')
@click.pass_obj
@click.argument('projname')
@click.option('-pn', '--newprojname', default=None,\
        help='Name of the new holding the task')
@click.option('--delete', 'deleteold', flag_value=True, default=True,\
        help='Delete the source project')
@click.option('--keep', 'deleteold', flag_value=False,\
        help='Keep the source project')
def proj(ctxObjs, projname, newprojname, deleteold):
    pass

@copy.command(help='Create a duplicate task. Also used to make a task parent-less or a child of another one')
@click.pass_obj
@click.argument('taskname')
@click.option('-pn', '--projname', default=None,\
        help='Name of the project holding the task')
@click.option('-tn', '--newtaskname', default=None,\
        help='Name of the new task')
@click.option('--delete', 'deleteold', flag_value=True, default=True,\
        help='Delete the source task')
@click.option('--keep', 'deleteold', flag_value=False,\
        help='Keep the source task')
def task(ctxObjs, taskname, projname, newtaskname, deleteold):
    pass

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
    ctxObjs['projObj'].stopTask(taskname, ctxObjs['confObj'])

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
    ctxObjs['projObj'].finishTask(taskname, ctxObjs['confObj'])

@cli.command(help='Promote a task/subtask to project/subproject')
@click.pass_obj
@click.argument('taskname')
@click.option('-pp', '--parentproj', default=None,\
        help='Name of parent project. (Promote to subproject)')
@click.option('-pn', '--projname', default=None,\
        help='Name of the project. If different from current name')
def promote(ctxObjs, taskname, projname, parentproj):
    pass

@cli.command(help='Demote a project/subproject to a task/subtask')
@click.pass_obj
@click.argument('projname')
@click.option('-pt', '--parenttask', default=None,\
        help='Name of parent task. (Demote to subtask)')
@click.option('-tn', '--taskname', default=None,\
        help='Name of the task')
def demote(ctxObjs, projname, taskname, parenttask):
    pass

@cli.group()
@click.pass_context
def show(ctx):
    pass

@show.command(help=\
        'Show a gantt chart with current progress')
@click.pass_obj
def gantt(confObj):
    pass

@show.command(help=\
        'Show a kanban representation of current tasks')
@click.pass_obj
def kanban(confObj):
    pass

@show.command(help='Show a burndown chart for the defined time')
@click.pass_obj
def burndown(confObj):
    pass

if __name__ == '__main__':
    cli()
