import re



def parseFilter(_filter):
    normal = list()
    wildcards = list()

    for i in _filter:
        i = i.replace("*", "", (i.count("*") - 1)) # remove multiple wildcards
        if i.endswith("*"):
            wildcards.append(i.replace("*", ".+"))
        else:
            normal.append(i)
    
    return re.compile(r"|".join([*normal, *wildcards]))