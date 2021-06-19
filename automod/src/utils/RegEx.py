import re


def getPattern(pattern, join=False):
    if join is False:
        return re.compile(pattern, flags=re.IGNORECASE)
    else:
        return re.compile(r"|".join(pattern), flags=re.IGNORECASE)


def Match(string, pattern, option="search", _return=False):
    options = {
        "search": pattern.search,
        "findall": pattern.findall
    }
    if option not in options:
        return False

    try:
        func = options[option]
        res = func(string)
        if res:
            if _return:
                return res
            else:
                return True
        else:
            return False
    except Exception:
        return False
