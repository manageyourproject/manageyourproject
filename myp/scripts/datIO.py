# Manage Your Project! A Complete Commandline Project Manager
# Copyright 2018 Aaron English
# Released under the GNU GPL-3


from ruamel.yaml import YAML

def yamlWriteConf(self, fileName, datDump):                                # the write file function
    yaml=YAML()
    with open(fileName, 'w') as fp:
        yaml.dump(datDump, fp)

def yamlReadConf(self, fileName):                                 # the read file function
    yaml=YAML()
    with open(fileName, 'r') as fp:
        loadedDat = yaml.load(fp)             # if it is found, read it

    return loadedDat

