import os
import json
import re
import enum

class TagType(enum.Enum):
    miscellaneous = 0
    character = 1
    series = 2

images = {}
tags = {
    "No Tags" : []
}

# Improvement Feature
tag_categories = {
    "No Tags" : 0
}

rules = {}

def index():
    hotlist = []
    for root, dirs, files in os.walk("./Repo-Chan"):
        for i in files:
            if i.endswith(".jpg") or i.endswith(".png") or i.endswith(".gif"):
                if i not in images:
                    images[i] = [0, "No Tags"]
                    tags["No Tags"].append(i)
                hotlist.append(i)

    if len(hotlist) != len(images):
        coldlist = []
        for i in images:
            if i not in hotlist:
                coldlist.append(i)
        for i in coldlist:
            delImg(i)
    saveIndex()
    
def saveIndex():
    json_obj = json.dumps({ "tags" : tags, "images" : images }, indent=1)
    with open(".index.json", "w") as out:
        out.write(json_obj)

def saveRule():
    json_obj = json.dumps({ "rules" : rules }, indent=1)
    with open(".rules", "w") as out:
        out.write(json_obj)

def readJsonRules():
    global rules
    if not os.path.exists(".rules") or os.path.getsize(".rules") == 0:
        with open(".rules", 'w') as file:
            return
    with open(".rules", "r") as rulesFile:
        rulebook = json.load(rulesFile)
        rules = rulebook["rules"]

def readJsonIndex():
    global images, tags
    if not os.path.exists(".index.json") or os.path.getsize(".index.json") == 0:
        with open(".index.json", 'w') as file:
            return
    with open(".index.json", "r") as indexFile:
        index = json.load(indexFile)
        images = index["images"]
        tags = index["tags"]

def addTag(tag, tp = TagType.miscellaneous):
    tags[tag] = []
    tag_categories[tag] = tp


def addImgTag(image, tag = "No Tags", tp = TagType.miscellaneous):
    images[image][0] += 1
    if tag not in images[image]:
        images[image].append(tag)
    if tag not in tags:
        addTag(tag, tp)
    if image not in tags[tag]:
        tags[tag].append(image)
    if images[image][0] == 1:
        tags["No Tags"].remove(image)
        images[image].remove("No Tags")

def delImgTag(image, tag):
    tags[tag].remove(image)
    images[image][0] -= 1
    images[image].remove(tag)
    if images[image][0] == 0:
        tags["No Tags"].append(image)
        images[image].append("No Tags")

def delImg(image): # Not actually delete image file, but to clean up deleted images from the index
    for t in tags:
        if image in tags[t]:
            delImgTag(image, t)
    images.pop(image)

def delTag(tag):
    for i in tags[tag]:
        delImgTag(i, tag)
    tags.pop(tag)
    if tag in tag_categories:
        tag_categories.pop(tag)

def addRule(string, tag):
    if string not in rules:
        rules[string] = []
    rules[string] = tag
    saveRule()

def removeRule(string):
    if string in rules:
        rules.pop(string)
    saveRule()

def editRuleString(oldString, newString):
    if oldString in rules:
        rules[newString] = rules[oldString]
        rules.pop(oldString)
    saveRule()

def editRuleTags(string, tags):
    rules[string] = tags
    saveRule()



def removeTaginRule(string, tag):
    if string in rules and tag in rules[string]:
        rules[string].pop(tag)

def applyRule(rule):
    for i in images:
        if rule in i:
            for t in rules[rule]:
                addImgTag(i, t)
    saveIndex()

def unapplyRule(rule):
    for i in images:
        if rule in i:
            for t in rules[rule]:
                delImgTag(i, t)
    saveIndex()

def indexByRule():
    for r in rules:
        applyRule(r)

def undoIndexByRule():
    for r in rules:
        unapplyRule(r)

def searchByName(string):
    index()
    results = []
    for i in images: 
        if string in i:
        #Regex search is broken
        #if re.search(string, i):
            results.append(i)
    return results

def searchByTags(searchTags, strong = True, space = None):
    index()
    if space == None:
        results = list(images.keys())
    else:
        results = space
    for i in images:
        for t in searchTags:
            if i in tags[t] and not strong:
                break
            if i not in tags[t] and strong:
                if i in results:
                    results.remove(i)
    return results

def searchByNameAndTags(string, searchTags, strong = True):
    return searchByTags(searchTags, strong, searchByName(string))
