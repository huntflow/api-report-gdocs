def get_nested(data, key: str) -> str:
    ret = data
    for x in key.split("."):
        if x.isdigit():
            x = int(x)
        ret = ret[x]
    return ret
