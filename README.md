# Manage Your Project! A Complete Commandline Project Manager

## A Commandline Project Manage With Bells
------------------------------------------
myp aims to provide a free and open source commandline project management experience that can serve to organize your projects, teams, and provide 

## ...And Whistles
------------------
Many project management tools lack many features or have their features hidden behind a paywall. This tool aims to rectify that. 

## Installation
myp requires python 3 to run, and manages dependancies using pip. In the future, myp will be installable via pip, but as of right now it is only installable using the following commands. 

NOTE: Make sure to use your system's python 3 installation, not 2.x. myp has not been tested using python <3.x and likely will not work.

```bash
git clone https://github.com/manageyourproject/manageyourproject
cd manageyourproject
pip3 install --user --editable ./
```

## Usage

## Why?
-------
I like working from terminal. As my projects grew more complex, and I needed to provide visuals like gantt charts, I wanted a project management/time tracking/todo list that i could use from the command line. While there are projects that do pieces of this, (see [taskwarrior](https://github.com/GothenbugBitFactory/taskwarrior), its related project [timewarrior](https://github.com/GothenburgBitFactory/timewarrior) and [taskjuggler](https://github.com/taskjuggler/taskjuggler) etc.) the options for a complete tool with all the features I needed/wanted was lacking.

## How?
-------
The project files are all done using json so that they are human readable, and easily modified in your favourite text editor. 
