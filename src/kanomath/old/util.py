# From https://stackoverflow.com/questions/4578590/python-equivalent-of-filter-getting-two-output-lists-i-e-partition-of-a-list
def partition(pred, iterable):
    trues = []
    falses = []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses

def kprint(text, level = 0):
    out = "    " * level
    out += text
    print(out)

def flatten(input):
    if isinstance(input, (list, tuple)):
        if len(input) == 1:
            return input[0]
        else:
            raise Exception("Attemption to flatten array with incorrect length") 
    else:
        return input
