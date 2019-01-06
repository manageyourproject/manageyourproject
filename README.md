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

Note: not all commands will work, and some have yet to be implemented. Future versions may also change their operation.

## Example
Say you've just installed MYP, and want to create a personal project to build a new cart. You would type:
```bash
myp new proj 'build cart'
```
Note the quotes around build cart. For names that have spaces in them, these are needed, otherwise myp will produce two projects: 'build' and 'cart'.

Since this is the first time you've issued an myp command, you will be prompted to allow myp to create a config file, and asked to enter your name and email address. It should be noted that myp is not doing anything with your email or name, except storing it in the config file to have labels of who is creating tasks, projects, and what work someone has done on a task, much like git does.

So now you have your project! Time to manage it. 
Add a task to it. (Note: because you just created it, it will be the 'active project' and so new tasks will by default be added to it, and not any other projects)
```bash
myp new task 'buy parts'
```
Then it occurs to you, you don't even know what your cart will look like! So you add a sub-project:
```bash
myp new proj 'build cart'.design
```
Now 'build cart'.design is the active project, so you add a couple more tasks to it:
```bash
myp new task sketch 'CAD model'
```
This will create both the tasks 'sketch' and 'CAD model'. (You can create as many projects and tasks at the same time as you want)
You then think to yourself that you don't actually know what CAD tool you're going to use, so you figure you'll have to explore that, so you add a subtask to 'CAD model':
```bash
myp new task 'CAD model'.'find CAD tool'
```
Now you figure thats good enough for the time being, so you get to work on finding the best CAD tool. So you start that task:
```bash
myp task 'CAD model'.'find CAD tool' start
```
You work for a little while, then decide its time to change it up. So you decide maybe you'll go to the store to buy the parts (despite not knowing what your cart will look like yet; a questionable decision) so you stop the 'find CAD tool' task and then start that task:
```bash
myp task 'CAD model'.'find CAD tool' stop
myp active 'build cart'
myp task 'buy parts' start
```
or
```bash
myp task 'CAD model'.'find CAD tool' stop
myp task 'buy parts' -pn 'build cart' start
```
Note: if you specify the project holding the task, that project will not be activated, and the current active project will remain active.

Before you can leave to go to the store, you realize you don't even know what you'd buy. You don't even know which store you'd go to, or for that matter, how much you'd have to budget! You quickly realize that this simple task is becoming more complex than you originally thought it would be. So you decide you want to promote the 'buy parts' task to a subproject of its own, and then add tasks for finding a low cost supplier, determining the budgetary constraints of the project, and going out to actually get the parts. Assuming that 'build cart' is active you first declare the task finished (for completeness) and then promote it:
```bash
myp task 'buy parts' finish
myp promote 'buy parts' 'build cart'.'buy parts'
myp active 'build cart'.'buy parts'
myp new task 'determine budget' 'find supplier' 'go to store'
```
If you don't want to keep the old task listed as finished, you can just delete the old task when promoting it:
```bash
myp promote 'buy parts' 'build cart'.'buy parts' --deleteold
myp active 'build cart'.'buy parts'
myp new task 'determine budget' 'find supplier' 'go to store'
```
Now you've got a few different tasks, under a couple of subprojects. To see you projects (with subprojects) you type:
```bash
myp list proj
```
To then see your subprojects tasks you type:
```bash
myp list task -pn 'build cart'.'buy parts'
myp list task -pn 'build cart'.'design'
```

The previous three command will give a little printout of the projects and then their tasks.

This little example is not exhaustive and while it would seem extreme to do all this for building a cart, hopefully this example gives a brief overview of how you can use myp to try to plan out and keep track of your project as it progresses, and make handling larger and more sophisticated projects easier.

## Why?
I like working from terminal. As my projects grew more complex and I needed to provide visuals like gantt charts, I wanted a project management/time tracking/todo list that I could use from the command line. While there are a variety of tools that do pieces of this, (see [taskwarrior](https://github.com/GothenbugBitFactory/taskwarrior), its related project [timewarrior](https://github.com/GothenburgBitFactory/timewarrior), and [taskjuggler](https://github.com/taskjuggler/taskjuggler) etc.) the options for a complete tool with all the features I needed/wanted was lacking.

## How?
The project files and config files are all stored as YAML files so that they are human readable, and easily modified in your favourite text editor. 
