
# Node is assumed to be a dict.
# keys = ["hit", "count", "children"]

def id():
    keys = ["hit", "left", "recieved",  "children"]
    values = [0, 0, 0, {}]
    return dict(zip(keys, values))

def add(node, words):
    while words:
        head, *tail = words
        node["hit"] += 1
        node["left"] += 1
        if head in node["children"]:
            node = node["children"][head] 
        else:
            newNode = id()
            node["children"][head] = newNode
            node = newNode
        words = tail
    node["hit"] += 1
    node["left"] += 1

def update_recieved(node, words, recieved):
    node["recieved"] += recieved
    if words:
        head, *tail = words
        if head in node["children"]:
            update_recieved(node["children"][head], tail, recieved)



def weight(node):
    visited = node["hit"] - node["left"]
    if visited == 0:
        return 1.0
    return (float(node["recieved"])+0.5)/visited

def next(node):
    node["left"] -= 1
    return next_acc(node, '')

def next_acc(node, acc):
    if not node["children"]:
        return acc
    else:
        children = node["children"]
        mChild, nChild = max(children.items(), key=lambda x: weight(x[1]))
        result = next_acc(nChild, acc + "/" + mChild)
        nChild["left"] -= 1
        if nChild["left"] == 0:
            del children[mChild]
        return result

def empty(node):
    return node["left"] <= 0

        









