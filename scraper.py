import requests
from collections import deque
from pprint import pformat
from lxml import html
import trie
from os.path import isfile
from urllib.parse import urlparse
import json


def as_words(link):
    scheme, netloc, path, params, query, fragment = urlparse(link)
    _, *result = path.split('/')
    return result

def processTree(tree, xpathString):
    try:
        elements = tree.xpath(xpathString)
        content = list(map(lambda x: x.text_content(), elements))
        cat = '\n'.join(content)
        return cat
    except UnicodeDecodeError:
        return ''

def writeout(outdir, fname, string):
    fname = fname.replace("/", '_')
    path = outdir + "/" + fname
    try:
        with open(path, "w+") as ofp:
            ofp.write(string)
    except OSError:
        maxlen = 30
        path = path[:30]
        with open(path, "w+") as ofp:
            ofp.write(string)
 

def maybe_resume(website):
    queue = trie.id()
    processed = set()
    scheme, netloc, *_ = urlparse(website)
    backup_fn = "." + '_'.join(list(reversed(netloc.split(".")))) + ".backup"
    try:
        with open(backup_fn, "r") as backup_fp:
            backup = json.load(backup_fp)
            queue = backup["queue"]
            processed = set(backup["processed"])
            return (queue, processed)

    except:
        trie.add(queue, [])
        processed.add(website)
        return (queue, processed)

def save_checkpoint(website, processed, queue):
    scheme, netloc, *_ = urlparse(website)
    backup_fn = "." + '_'.join(list(reversed(netloc.split(".")))) + ".backup"
    with open(backup_fn, "w+") as backup_fp:
        backup = {"processed": list(processed), "queue": queue}
        json.dump(backup, backup_fp)

def crawl(website, xpathString, passes_rules, outdir, logfile):
    queue, processed = maybe_resume(website)
    logfp = open(logfile, "a+")

    counter = 0
    save_frequency = 100

    with requests.Session() as session:
        while not trie.empty(queue):
            #print(pformat(queue))
            #@print(trie.next(queue))
            counter += 1
            if (counter % save_frequency == 0):
                save_checkpoint(website, processed, queue)
            target_path = trie.next(queue)
            target = website + target_path
            page = session.get(target)
            try:
                tree = html.fromstring(page.content)
                content = processTree(tree, xpathString)
                if content:
                    writeout(outdir, target_path, content)
                score = len(content)
                trie.update_recieved(queue, as_words(target_path), score)

                print("-\t%s\t%d"%(target, score), file=logfp)
                print("- %s %d"%(target, score))
                for (elem, attrib, link, pos) in tree.iterlinks():
                    path = as_words(link)
                    pathStr = '/'.join(path)
                    if pathStr not in processed and passes_rules(path):
                        processed.add(pathStr)
                        print("+\t%s"%('/'.join(path)), file=logfp)
                        trie.add(queue, path)
            except lxml.etree.XMLSyntaxError:
                pass

def rules(words):
    if not words:
        return False
    if words[0] == 'en-news':
        return False
    white_ext = ['.html']
    last = words[-1]
    for ext in white_ext:
        if(len(last) < len(ext)):
            return False
        return last[-(len(ext)):].lower() == ext

        



