import click
import textwrap

from colorama import Fore, Back, Style

def printToCli(message):
    click.echo(message)

def getInput(message, inputType=str, *args, **kwargs):
    return click.prompt(message, type=inputType)

def getConfirmation(message, abort=True, *args, **kwargs):
    return click.confirm(message, abort=abort)

def showError(message):
    raise click.ClickException(message)

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
    # print(termWidth)
    for n in range(max([len(i) for i in row])):
        for count, col in enumerate(row):
            formattedStr += rowDict[count]['lead']
            if n < len(col):
                formattedStr += '{i:<{width}}'.\
                    format(i=col[n], width=rowDict[count]['width'])
            else:
                formattedStr += ' '*rowDict[count]['width']


    return formattedStr

