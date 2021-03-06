# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3

import os
import math
import click
import shutil
import textwrap
import datetime as dt
from colorama import Fore, Back, Style

from myp import main
from myp.scripts import cliUtils

@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx):
    APP_NAME = 'myp'                           # required for default path
    cfg = click.get_app_dir(APP_NAME)     # getting default path
    if ctx.obj is None:
        ctx.obj = dict()

    ctx.obj['confObj'] = main.initConf(cfg)
    ctx.obj['cfg'] = cfg

    if ctx.invoked_subcommand is None:
        click.echo('Type '+click.style('myp --help',\
                fg='red',bold=True)+' for usage')
        click.echo(main.getActive(ctx.obj['confObj']))

        projname = ctx.obj['confObj'].confDat['session']['active']
        proj = main.loadProj(ctx.obj['confObj'],projname)
        if isinstance(proj, str):
            raise click.ClickException(proj)

        colAlt = False
        listDict = cliUtils.getTaskPrintList(proj)
        colAlt = not colAlt

        for key, value in sorted(listDict.items()):
            click.echo(Fore.WHITE+Back.BLACK+click.style(\
                    value, reverse=colAlt))

            colAlt = not colAlt

@cli.command(help=\
        'Get currently active project, or activate a project')
@click.pass_obj
@click.argument('projname', required=False, default=None, type=str)
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
@click.argument('projname', nargs=-1, type=str)
@click.option('-st', '--storetype', default=None,\
        help='Type of store for the project', type=str)
@click.option('-sl', '--storeloc', default=None,\
        help='Location of the store for the project', type=str)
@click.option('-f', '--force', is_flag=True,\
        help='Force project creation (will overwrite any projects with the same name)')
@click.option('-e', '--edit', is_flag=True, \
              help='Manually fill in a project\'s fields')
def proj(ctxObjs, projname, storetype, storeloc, force, edit):
    for i in projname:
        output = main.makeProj(ctxObjs['confObj'], i, storetype, storeloc, force, None)
        if isinstance(output, str):
            raise click.ClickException(output)
        if edit:
            cliUtils.editObjs(output, ctxObjs['cfg'])

        active = main.makeActive(ctxObjs['confObj'], i)
        if isinstance(active, str):
            raise click.ClickException(active)
    
@new.command(help='Create a new task')
@click.pass_obj
@click.argument('taskname', nargs=-1, type=str)
@click.option('-pn', '--projname', default=None,\
        help='Name of the project to add the task to', type=str)
@click.option('-ta', '--assignee', default=None, help=\
        'Team member the task is assigned to', type=str)
@click.option('-e', '--edit', is_flag=True, \
              help='Manually fill in a tasks fields')
def task(ctxObjs,taskname,projname, assignee, edit):
    if not projname:
        projname = ctxObjs['confObj'].confDat['session']['active']
        if not projname:
            projname = click.prompt('Enter a project to add the task to')
    else:
        active = main.makeActive(ctxObjs['confObj'], projname)
        if isinstance(active, str):
            raise click.ClickException(active)

    proj = main.loadProj(ctxObjs['confObj'],projname)
    if isinstance(proj, str):
        raise click.ClickException(proj)

    for i in taskname:
        output = proj.addTask(i, assignee)
        if isinstance(output, str):
            raise click.ClickException(output)
        if edit:
            cliUtils.editObjs(output, ctxObjs['cfg'])

        main.writeProj(proj)

@cli.group()
@click.pass_context
def edit(ctx):
    pass

@edit.command(help='Edit a project')
@click.pass_obj
@click.argument('projname', nargs=-1, type=str)
def proj(ctxObjs):
    pass

@edit.command(help='Edit a project')
@click.pass_obj
@click.argument('taskname', nargs=-1, type=str)
@click.option('-pn', '--projname', default=None,\
        help='Name of the project to add the task to', type=str)
def task(ctxObjs):
    pass

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

        for i, j in ctxObjs['confObj'].\
                confDat['session']['listformat'].items():
            
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
        help='Name of project to get tasks from', type=str)
def task(ctxObjs,projname):
    if not projname:
        projname = ctxObjs['confObj'].confDat['session']['active']
        if not projname:
            projname = click.prompt('Enter a project to add the task to')

    proj = main.loadProj(ctxObjs['confObj'],projname)
    if isinstance(proj, str):
        raise click.ClickException(proj)

    colAlt = False
    listDict = cliUtils.getTaskPrintList(proj)
    colAlt = not colAlt

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
@click.argument('projname', nargs=-1, required=True, type=str)
def proj(ctxObjs, projname):
    for i in projname:
        output = main.deleteProj(ctxObjs['confObj'], i)
        if isinstance(output, str):
            raise click.ClickException(output)

@delete.command(help='Delete a task')
@click.pass_obj
@click.argument('taskname', nargs=-1, required=True, type=str)
@click.option('-pn', '--projname', default=None,\
        help='Name of the project to delete the task from', type=str)
def task(ctxObjs,taskname,projname):
    if not projname:
        projname = ctxObjs['confObj'].confDat['session']['active']
        if not projname:
            projname = click.prompt('Enter a project to delete the task from') 

    proj = main.loadProj(ctxObjs['confObj'],projname)
    if isinstance(proj, str):
        raise click.ClickException(proj)

    for i in taskname:
        output = proj.deleteTask(i, force=None)
        if isinstance(output, str):
            raise click.ClickException(output)

    main.writeProj(proj)

@cli.group()
@click.pass_context
def copy(ctx):
    pass

@copy.command(help='Create a copy project. Also can be used'+\
              ' to make a project parent-less or make it a child of another project')
@click.pass_obj
@click.argument('projname', required=True, type=str)
@click.argument('newprojname', required=True, type=str)
@click.option('--delete', 'deleteold', is_flag=True,\
        help='Delete the source project')
def proj(ctxObjs, projname, newprojname, deleteold):
    output = main.copyProj(ctxObjs['confObj'], projname, newprojname, deleteold)
    if isinstance(output, str):
        raise click.ClickException(output)

@copy.command(help='Create a duplicate task.'+\
              ' Also used to make a task parent-less or a child of another one')
@click.pass_obj
@click.argument('taskname', type=str)
@click.argument('newtaskname', required=False, default=None, type=str)
@click.option('-pn', '--projname', default=None,\
        help='Name of the project holding the task', type=str)
@click.option('-npn', '--newtaskproj', default=None,\
        help='Name of the new task', type=str)
@click.option('--delete', 'deleteold', is_flag=True,\
        help='Delete the source task')
def task(ctxObjs, taskname, newtaskname, projname, newtaskproj, deleteold):
    if not projname:
        projname = ctxObjs['confObj'].confDat['session']['active']
        if not projname:
            projname = click.prompt('Enter a project to add the task to')

    proj = main.loadProj(ctxObjs['confObj'],projname)
    if isinstance(proj, str):
        raise click.ClickException(proj)

    task = proj.loadTask(taskname)
    if isinstance(task, str):
        raise click.ClickException(task)

    if not newtaskname:
        newtaskname = taskname

    if newtaskproj:
        newproj = main.loadProj(ctxObjs['confObj'],newtaskproj)
        if isinstance(newproj, str):
            raise click.ClickException(proj)

        output = newproj.makeTask(newtaskname, dat=task.dumpDat())
        if isinstance(output, str):
            raise click.ClickException(output)
    else:
        output = proj.makeTask(newtaskname, dat=task.dumpDat())
        if isinstance(output, str):
            raise click.ClickException(output)

    if deleteold:
        output = proj.deleteTask(taskname)
        if isinstance(output, str):
            raise click.ClickException(output)

@cli.group()
@click.pass_obj
@click.argument('taskname', required=True, type=str)
@click.option('-pn', '--projname', required=False, default=None, type=str)
def task(ctxObjs, taskname, projname):
    if not projname:
        projname = ctxObjs['confObj'].confDat['session']['active']
        if not projname:
            projname = click.prompt('Enter a project to add the task to')

    proj = main.loadProj(ctxObjs['confObj'],projname)
    if isinstance(proj, str):
        raise click.ClickException(proj)

    task = proj.loadTask(taskname) 
    if isinstance(task, str):
        raise click.ClickException(task)

    ctxObjs['taskObj']=task
    ctxObjs['projObj']=proj

@task.command(help='Start tracking time for task')
@click.pass_obj
def start(ctxObjs):
    output = ctxObjs['taskObj'].startTask()
    if isinstance(output, str):
        raise click.ClickException(output)

    main.writeProj(ctxObjs['projObj'])

@task.command(help='Stop tracking time for task')
@click.pass_obj
def stop(ctxObjs):
    output = ctxObjs['taskObj'].stopTask(ctxObjs['confObj'])
    if isinstance(output, str):
        raise click.ClickException(output)

    main.writeProj(ctxObjs['projObj'])

@task.command(help='Stop tracking time for task')
@click.pass_obj
def finish(ctxObjs):
    output = ctxObjs['taskObj'].finishTask(ctxObjs['confObj'], ctxObjs['projObj'])
    if isinstance(output, str):
        raise click.ClickException(output)

    main.writeProj(ctxObjs['projObj'])

@cli.command(help='Promote a task/subtask to project/subproject')
@click.pass_obj
@click.argument('taskname', type=str)
@click.argument('newprojname', required=False, default=None, type=str)
@click.option('-pn', '--parentprojname', default=None,\
        help='Name of the project holding the task', type=str)
@click.option('--delete', 'deleteold', is_flag=True,\
        help='Delete the source task')
def promote(ctxObjs, taskname, newprojname, parentprojname, deleteold):
    if not parentprojname:
        parentprojname = ctxObjs['confObj'].confDat['session']['active']
        if not parentprojname:
            parentprojname = click.prompt('Enter the name of the project holding the task')

    parproj = main.loadProj(ctxObjs['confObj'],parentprojname)
    if isinstance(parproj, str):
        raise click.ClickException(parproj)

    task = parproj.loadTask(taskname)
    if isinstance(task, str):
        raise click.ClickException(task)

    if not newprojname:
        names=taskname.split('.')
        newprojname = names[-1]

    output = main.promote(ctxObjs['confObj'],newprojname, parproj, taskObj)
    if isinstance(output, str):
        raise click.ClickException(output)

    if deleteold:
        output = parproj.deleteTask(taskname)
        if isinstance(output, str):
            raise click.ClickException(output)

        main.writeProj(parproj)

@cli.command(help='Demote a project/subproject to a task/subtask')
@click.pass_obj
@click.argument('projname', type=str)
@click.argument('parentprojname', type=str)
@click.option('-pn', '--taskname', default=None,\
        help='Name of the new task', type=str)
@click.option('--delete', 'deleteold', is_flag=True,\
        help='Delete the source task')
def demote(ctxObjs, projname, parentprojname, taskname, deleteold):
    if not projname:
        projname = ctxObjs['confObj'].confDat['session']['active']
        if not projname:
            projname = click.prompt('Enter the name of the project holding the task')

    proj = main.loadProj(ctxObjs['confObj'],projname)
    if isinstance(proj, str):
        raise click.ClickException(proj)

    parproj = main.loadProj(ctxObjs['confObj'],parentprojname)
    if isinstance(parproj, str):
        raise click.ClickException(parproj)

    if not taskname:
        names=projname.split('.')
        taskname = names[-1]

    output = main.demote(ctxObjs['confObj'], proj, parproj, taskname)
    if isinstance(output, str):
        raise click.ClickException(output)

    if deleteold:
        output = main.deleteProj(confObj, proj)
        if isinstance(output, str):
            raise click.ClickException(output)

@cli.command(help='Update all project or all files to current format')
@click.pass_obj
@click.argument('projname', required=False, type=str)
def update(ctxObjs, projname):
    output = main.updateFiles(ctxObjs['confObj'], projname)
    if isinstance(output, str):
        raise click.ClickException(output)

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
