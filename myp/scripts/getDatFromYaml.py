from ruamel.yaml import YAML

def writeProj(self):
    yaml = YAML()
    with open(self.projFile, 'w') as fp:
        yaml.dump(self.projDat, fp)

def readProj(self):
    yaml = YAML()
    if not self.projExists():
        raise click.ClickException(\
                'No project/subproject by that name')
    else:
        with open(self.projFile, 'r') as fp:
            self.projDat = yaml.load(fp)
