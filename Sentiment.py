import re, math, collections, itertools, os
import nltk, nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

SENTIMENT_THRESHOLD = 0.7

def initPath():
    global POLARITY_DATA_DIR
    global RT_POLARITY_POS_FILE
    global RT_POLARITY_NEG_FILE
    POLARITY_DATA_DIR = os.path.join('polarityData', 'rt-polaritydata')
    RT_POLARITY_POS_FILE = os.path.join(POLARITY_DATA_DIR, 'rt-polarity-pos.txt')
    RT_POLARITY_NEG_FILE = os.path.join(POLARITY_DATA_DIR, 'rt-polarity-neg.txt')

def getSentiment(featureSelect, sentenceText):
    posFeatures = []
    negFeatures = []
    with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
        for i in posSentences:
            posWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            posWords = [featureSelect(posWords), 'pos']
            posFeatures.append(posWords)
    with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
        for i in negSentences:
            negWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            negWords = [featureSelect(negWords), 'neg']
            negFeatures.append(negWords)

    trainFeatures = posFeatures + negFeatures
    classifier = NaiveBayesClassifier.train(trainFeatures)  

    sentenceWords = re.findall(r"[\w']+|[.,!?;]", sentenceText.rstrip())
    sentenceWords = dict([(word, True) for word in sentenceWords])
    predicted = classifier.classify(sentenceWords)

    return predicted

def judgeSetSentiment(sentenceList):
    if len(sentenceList) == 0:
        return False
    posCount = 0
    for sentence in sentenceList:
        if 'pos' == getSentiment(makeFullDict, sentence):
            posCount += 1
    ratio = float(posCount) / float(len(sentenceList))
    if ratio > SENTIMENT_THRESHOLD:
        return True
    else:
        return False



def evaluateFeatures(featureSelect):
    posFeatures = []
    negFeatures = []
   
    with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
        for i in posSentences:
            posWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            posWords = [featureSelect(posWords), 'pos']
            posFeatures.append(posWords)
    with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
        for i in negSentences:
            negWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            negWords = [featureSelect(negWords), 'neg']
            negFeatures.append(negWords)

    
    posCutoff = int(math.floor(len(posFeatures)*3/4))
    negCutoff = int(math.floor(len(negFeatures)*3/4))
    #trainFeatures = posFeatures[:posCutoff] + negFeatures[:negCutoff]
    testFeatures = posFeatures[posCutoff:] + negFeatures[negCutoff:]
    trainFeatures = posFeatures + negFeatures
    print testFeatures[0]
    classifier = NaiveBayesClassifier.train(trainFeatures)  

    referenceSets = collections.defaultdict(set)
    testSets = collections.defaultdict(set) 

    for i, (features, label) in enumerate(testFeatures):
        referenceSets[label].add(i)
        predicted = classifier.classify(features)
        #print features
        #print predicted
        testSets[predicted].add(i)  

    # print 'train on %d instances, test on %d instances' % (len(trainFeatures), len(testFeatures))
    # print 'accuracy:', nltk.classify.util.accuracy(classifier, testFeatures)
    # print 'pos precision:', nltk.metrics.precision(referenceSets['pos'], testSets['pos'])
    # print 'pos recall:', nltk.metrics.recall(referenceSets['pos'], testSets['pos'])
    # print 'neg precision:', nltk.metrics.precision(referenceSets['neg'], testSets['neg'])
    # print 'neg recall:', nltk.metrics.recall(referenceSets['neg'], testSets['neg'])
    # classifier.show_most_informative_features(10)

def makeFullDict(words):
    return dict([(word, True) for word in words])


#evaluateFeatures(makeFullDict)


def getWordScores():
    posWords = []
    negWords = []
    with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
        for i in posSentences:
            posWord = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            posWords.append(posWord)
    with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
        for i in negSentences:
            negWord = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            negWords.append(negWord)
    posWords = list(itertools.chain(*posWords))
    negWords = list(itertools.chain(*negWords))

    word_fd = FreqDist()
    cond_word_fd = ConditionalFreqDist()
    for word in posWords:
        word_fd[word.lower()] += 1
        cond_word_fd['pos'][word.lower()] += 1
    for word in negWords:
        word_fd[word.lower()] += 1
        cond_word_fd['neg'][word.lower()] += 1

    pos_word_count = cond_word_fd['pos'].N()
    neg_word_count = cond_word_fd['neg'].N()
    total_word_count = pos_word_count + neg_word_count

    word_scores = {}
    for word, freq in word_fd.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word], (freq, pos_word_count), total_word_count)
        neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word], (freq, neg_word_count), total_word_count)
        word_scores[word] = pos_score + neg_score

    return word_scores


def getBestWords(word_scores, number):
    best_vals = sorted(word_scores.iteritems(), key=lambda (w, s): s, reverse=True)[:number]
    best_words = set([w for w, s in best_vals])
    return best_words

def bestWordFeatures(words):
    return dict([(word, True) for word in words if word in best_words])


initPath()


if __name__ == "__main__":

    print "pos" == getSentiment(makeFullDict, "What a wonderful place to eat!")

    #finds word scores
    #word_scores = getWordScores()
    #print word_scores['fun'], word_scores['wonderful'], word_scores['chill']
        
    #numbers of features to select
    #numbers_to_test = [10, 100, 1000, 10000, 15000]
    #tries the bestWordFeatures mechanism with each of the numbers_to_test of features
    #for num in numbers_to_test:
    #    print 'evaluating best %d word features' % (num)
    #    best_words = getBestWords(word_scores, num)
    #    #evaluateFeatures(bestWordFeatures)
