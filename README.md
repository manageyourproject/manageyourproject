# Manage Your Project! A Complete Commandline Project Manager
---
## A Commandline Project Manager with Bells and Whistles
myp aims to provide a free and open source commandline project management experience that can serve to organize your projects, teams, and provide visualization of your entire project, progress, and goals.

This project is currently under heavy development and stuff changes a lot from commit to commit. Many features are yet to be implemented and things may not always work right.

If there are things not implemented that you feel would make this a better tool, please open an issue.

## Installation
myp requires python 3 to run, and manages dependancies using pip. In the future, myp will be installable via pip, but as of right now it is only installable using the following commands. 

```bash
git clone https://github.com/manageyourproject/manageyourproject
cd manageyourproject
pip3 install --user --editable ./
```

NOTE: myp has only been tested with python 3 on a unix system. It is unknown if it will work on a windows machine, and suspected that it will not work with python <3.x

## Usage
MYP is run through the commandline. Once installed through pip, it is executed using 
```bash
myp <command> <arguments> <options>
```
Typing 
```bash
myp --help
```
will give a list of commands and basic information on them. 

Note: not all commands will work, and some have yet to be implemented. Future versions may also change their operaton.

## Why?
I like working from terminal. As my projects grew more complex and I needed to provide visuals like gantt charts, I wanted a project management/time tracking/todo list that i could use from the command line. While there are a variety of tools that do pieces of this, (see [taskwarrior](https://github.com/GothenbugBitFactory/taskwarrior), its related project [timewarrior](https://github.com/GothenburgBitFactory/timewarrior), and [taskjuggler](https://github.com/taskjuggler/taskjuggler) etc.) the options for a complete tool with all the features I needed/wanted was lacking.

## How?
The project files and config files are all stored as YAML files so that they are human readable, and easily modified in your favourite text editor. 
