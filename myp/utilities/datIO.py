from ruamel.yaml import YAML

def yamlWrite(dat, location):                                # the write file function
    yaml=YAML()
    with open(location, 'w') as fp:
        yaml.dump(dat, fp)


def yamlRead(location):                                 # the read file function
    yaml=YAML()
    try:
        with open(location, 'r') as fp:
            dat = yaml.load(fp)             # if it is found, read it

        return dat
    except:
        return
