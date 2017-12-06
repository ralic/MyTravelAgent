# This module implements the calculation of the semantic similarity 
# between two words

from nltk.corpus import wordnet as wn
import nltk

SIMILARITY_THRESHOLD = 0.5

def findIntersection(list1, list2):
    common = None
    deepest = 0
    for i1 in list1:
        for i2 in list2:
            if i1 == i2:
                depth = list1.index(i1)
                if depth > deepest:
                    deepest = depth
                    common = i1
    return common, deepest

def getLso(synsets1, synsets2):
    pathList1, pathList2 = [], []
    for s1 in synsets1:
        for path in s1.hypernym_paths():
            pathList1.append(path)
    for s2 in synsets2:
        for path in s2.hypernym_paths():
            pathList2.append(path)
    deepest = 0
    lso = None
    for p1 in pathList1:
        for p2 in pathList2:
            subsumer, depth = findIntersection(p1, p2)
            if subsumer is not None:
                if depth > deepest:
                    lso = subsumer
                    deepest = depth
    return lso, deepest

def getShortestPath(synsets1, synsets2):
    minShortest = float("inf")
    for s1 in synsets1:
        for s2 in synsets2:
            shortest = s1.shortest_path_distance(s2)
            if shortest is not None:
                minShortest = min(shortest, minShortest)
    return minShortest

def semSim(word1, word2):
    synsets1 = wn.synsets(word1.lower())
    synsets2 = wn.synsets(word2.lower())
    if (len(synsets1) == 0) or (len(synsets2) == 0):
        return -1
    lso, lsoDepth = getLso(synsets1, synsets2)
    minLen = getShortestPath(synsets1, synsets2)
    sim = float(2 * lsoDepth) / float(minLen + 2 * lsoDepth)
    return sim

def getSetsSim(refSet, targetSet):
    if len(refSet) == 0:
        return 0.0
    hitRatioSum = 0
    for targetWord in targetSet:
        targetWord = targetWord.lower()
        targetWord = targetWord.strip("#")
        hit = 0
        for refWord in refSet:
            refWord = refWord.strip("#")
            refWord = refWord.lower()
            if (refWord == targetWord) or (refWord in targetWord) or (targetWord in refWord):
                hit += 2
            else:
                if semSim(refWord, targetWord) > SIMILARITY_THRESHOLD:
                    hit += 1
        hitRatio = float(hit) / float(len(refSet))
        hitRatioSum += hitRatio
    simScore = hitRatioSum / len(targetSet)
    return simScore


if  __name__ == "__main__":
    print(semSim("happy", "excited"))
    print(semSim("policman", "fireman"))
    print(semSim("tree", "flower"))
    #synsets2 = wn.synsets("ice")
    #print getShortestPath(synsets1, synsets2)
    #print synsets1[0].hypernym_paths()[3]
    #print getLso(synsets1, synsets2)