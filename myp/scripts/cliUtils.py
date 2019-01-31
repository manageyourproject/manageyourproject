import math
import click
import textwrap

from colorama import Fore, Back, Style
from myp.utilities import datIO
from myp.utilities import dictUpdate as du

def printToCli(message):
    click.echo(message)

def getInput(message, inputType=str, *args, **kwargs):
    return click.prompt(message, type=inputType)

def getConfirmation(message, abort=True, *args, **kwargs):
    return click.confirm(message, abort=abort)

def showError(message):
    raise click.ClickException(message)

def editObj(obj, cfg):
    cfg = os.path.join(cfg, 'temp.yaml')
    datIO.yamlWrite(obj.dumpDat(), cfg)
    click.edit(filename=cfg)
    returnDat = datIO.yamlRead(cfg)
    obj.update(returnDat)

def getTaskPrintList(proj):
    colAlt = False
    termWidth, _ = click.get_terminal_size()
    cellWidth=int(math.floor(termWidth/len(proj.projDat['currentformat']))-2)
    cellWide= int(math.floor(termWidth/len(proj.projDat['currentformat']))-\
                 2+(0.5*cellWidth))
    cellThin= int(math.floor(termWidth/(len(proj.projDat['currentformat'])))-\
                 2-(0.5*cellWidth))

    listDict={}
    listHead = []
    for i in proj.projDat['currentformat']:
        if i == 'Total Time':
            listHead.append({'lead':'| ',
                             'width':cellThin,
                             'text':i,
                             })
        elif i == 'Task Name':
            listHead.append({'lead':'| ',
                             'width':cellWide,
                             'text':i,
                             })
        else:
            listHead.append({'lead':'| ',
                             'width':cellWidth,
                             'text':i,
                             })

    click.echo(Fore.WHITE+Back.BLACK+click.style(\
            '{:{width}}'.format('-'*termWidth,\
            width=termWidth),bold=True, reverse=colAlt))
    click.echo(Fore.WHITE+Back.BLACK+click.style(\
            formatPrint(termWidth, listHead),\
            bold=True, reverse=colAlt))
    click.echo(Fore.WHITE+Back.BLACK+click.style(\
            '{:{width}}'.format('-'*termWidth,\
            width=termWidth),bold=True, reverse=colAlt))
    colAlt = not colAlt
    for key, value in proj.projDat['tasks'].items():
        listVals = []
        if not value.status() == 'finished':
            for i, j in proj.projDat['currentformat'].items():
                # listVals = listVals+'| '
                if j == 'name':
                    listDictKey = key
                    field = key
                else:
                    field = value.taskDat[j]

                if j == 'datecreated':
                    field = dt.datetime.fromisoformat(field).\
                            strftime('%Y/%m/%d')
                elif j == 'timeSpent':
                    timeraw = float(field)
                    if timeraw > 60 and timeraw < 60*60:
                        timemin = math.floor(timeraw/60)
                        timesec = timeraw%60
                        field = str(timemin)+'m '+str(timesec)+'s'
                    elif timeraw > 60*60 and timeraw < 24*60*60:
                        timehour = math.floor(timeraw/(60*60))
                        timemin = math.floor((timeraw-(timehour*(60*60)))/60)
                        timesec = timeraw%60
                        field = str(timehour)+'h '+str(timemin)+'m'
                    elif timeraw > 24*60*60:
                        timeday = math.floor(timeraw/(24*60*60))
                        timehour = math.floor((timeraw-(timeday*(24*60*60)))/(60*60))
                        timemin = math.floor((timeraw-(timehour*(60*60))-\
                                              (timeday*(24*60*60)))/60)
                        timesec = timeraw%60
                        field = str(timeday)+'d '+str(timehour)+'h'
                    else:
                        field = str(timeraw)+'s'
                elif j == 'assignee':
                    assignees = ''
                    for k in dict(value.taskDat[j]).keys():
                        assignees = assignees + k
                    field = assignees

                if j == 'timeSpent':
                    listVals.append({'lead':'| ',
                                     'width':cellThin,
                                     'text':field,
                                     })
                elif j == 'name':
                    if 'parent' in value.taskDat:
                        field = field.split('.')[-1]
                        listVals.append({'lead':'|   ',
                                         'width':cellWide-2,
                                         'text':field,
                                         })
                    else:
                        listVals.append({'lead':'| ',
                                         'width':cellWide,
                                         'text':field,
                                         })
                else:
                    listVals.append({'lead':'| ',
                                     'width':cellWidth,
                                     'text':field,
                                     })

            listDict[listDictKey]=formatPrint(termWidth, listVals)

    return listDict

def formatPrint(termWidth, rowDict):
    row=[]
    formattedStr = ''
    widUsed = 0
    for count, i in enumerate(rowDict):
        widUsed += i['width']+len(i['lead'])
        if count == len(rowDict)-1:
            if not widUsed == termWidth:
                remain = termWidth - widUsed
                i['width'] += remain

        row.append(textwrap.wrap(i['text'],i['width']))
    for n in range(max([len(i) for i in row])):
        for count, col in enumerate(row):
            formattedStr += rowDict[count]['lead']
            if n < len(col):
                formattedStr += '{i:<{width}}'.\
                    format(i=col[n], width=rowDict[count]['width'])
            else:
                formattedStr += ' '*rowDict[count]['width']

    return formattedStr

