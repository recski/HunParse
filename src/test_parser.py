#!/usr/bin/python
import sys
import optfunc
import pickle
from kr2nltk import Kr2NltkConverter
import nltk
from nltk import grammar, parse

def log(x):
    sys.stderr.write(str(x)+'\n')

def splitCorp(file):
    corp=[[]]
    for line in open(file):
        if line =='\n':
            corp.append([])
        else:
            corp[-1].append(line)
    
    return corp

def getTerminals(corp):
    sys.stderr.write('generating terminal rules...')
    terminals = set()
    converter = Kr2NltkConverter()
    krSet = set([line.strip().split()[1] for sen in corp for line in sen])
    terminals = [converter.kr2termRule(kr) for kr in krSet]
    sys.stderr.write('done\n')
    return terminals

def main(grammarFile='', text='', serialize=None, uncrossing=False,
         countCrosses=False, max_maxNpTag=False, b_baseNpTag=False,
         findWrongChunks=False, useCfg=False):
    sys.stderr.write('loading nltk...')
    corp = splitCorp(text)
    cLength=len(corp)
    grammarText = [l.strip('\n') for l in file(grammarFile)]
    grammarText += getTerminals(corp)
    grammarObj = grammar.parse_fcfg(grammarText)
    parser = parse.FeatureBottomUpChartParser(grammarObj)
    sys.stderr.write('done!\nparsing...')    
    
    if serialize:
        parseOut = open(serialize, 'w')
    
    allCrosses=0.0
    allSens=0.0
    for c,sen in enumerate(corp):
        allSens+=1
        if c*100/cLength>(c-1)*100/cLength: 
            sys.stderr.write(str(c*100/cLength)+'% ')
        toks = [l.strip('\n').split()[1] for l in sen]
        words = [l.strip('\n').split()[0] for l in sen]
        chart = parser.chart_parse(toks)
        if max_maxNpTag:
            tagMaxNPs(chart, sen, useCfg)
            print
        if b_baseNpTag:
            tagBaseNPs(chart, sen)
            print
        if findWrongChunks:
            getWrongChunks(chart, sen)
        if serialize:
            serializeParse(chart, toks, words, parseOut)
        if uncrossing:
            findUncrossingNPs(chart, words, useCfg)
        if countCrosses:    
            allCrosses+=findUncrossingNPs(chart, words, useCfg, countCrosses)
    sys.stderr.write('done\n')
    if countCrosses:
        print 'No. of sentences:', str(allSens)
        print 'No. of crosses:', str(allCrosses)
        print 'Average no. of crosses per sentence:',
        print allCrosses/allSens
    

def getWrongChunks(chart, sen):
    npSpans = findNPs(chart)
    #log(npSpans)
    chunkSpans = getChunks(sen)
    #log(chunkSpans)
    for chunk in chunkSpans:
        if chunk not in npSpans:
            printChunk(chunk, sen)

def printChunk(chunk, sen):
    words=[line.split()[0] for line in sen[chunk[0]:chunk[1]]]
    krs=[line.split()[1] for line in sen[chunk[0]:chunk[1]]]
    print ' '.join(words)+'\t'+' '.join(krs)        

def getChunks(sen):
    spans=set()
    inNP=False
    currStart = 0
    for c,tok in enumerate(sen):
        tag = tok.split()[-1]
        if tag[0]=='B':
            if inNP:
                spans.add((currStart, c))
            else:
                inNP=True
                currStart = c    
        elif tag[0]=='O':
            if inNP:
                spans.add((currStart, c))
                inNP=False

    return spans


def keepUnCrossing(spans):
    newSpans=set()
    for span in spans:
        keep = True
        for span2 in spans:
            if isCrossing(span, span2):
                keep = False
        if keep:
            newSpans.add(span)
    
    return newSpans


def tagMaxNPs(chart, sen, useCfg):
    nEdges = [edge for edge in chart if isNoun(edge)]
    npSpans = [edge.span() for edge in edges if containsNoun(edge.rhs())]    
    maxNpSpans = [span for span in spans if not isContained(span, spans)]
    keepLonger = False
    
    if keepLonger:
        disjuctSpans = keepLonger(maxNpSpans)
    else:
        disjunctSpans = keepUnCrossing(maxNpSpans)
    
    printTagging(sen, disjunctSpans)


def tagBaseNPs(chart, sen):
    nEdges = [edge for edge in chart if isNoun(edge)]
    #melyik edge ir ujra Noun-t?
    #print 'nEdges', nEdges
    npSpans = [edge.span() for edge in nEdges if containsNoun(edge.rhs())==1]
    #print 'npSpans', npSpans
    #melyik span tartalmaz pontosan 1 Nount legalabb 1 edge szerint
    baseNpSpans = set([span for span in npSpans if span[0]!=span[1]])
    #print 'baseNpSpans', baseNpSpans
    for edge in chart:
        if edge.is_complete() and containsNoun(edge.rhs())>1 and edge.span() in baseNpSpans:
            baseNpSpans.remove(edge.span())
    #melyik span nem irodik ujra tobb noun-kent (semelyik edge szerint)
    uncrossingSpans = keepUnCrossing(baseNpSpans)
    #print 'uncrossingSpans', uncrossingSpans
    longestSpans = keepLongestSpans(uncrossingSpans)
    printTagging(sen, longestSpans)

def keepLongestSpans(spans):
    spansToKeep = spans.copy()
    for span1 in spans:
        for span2 in spans:
            if span1!=span2 and contains(span2, span1):
                spansToKeep.discard(span1)
    return spansToKeep

def contains(span1, span2):
    return ( span1[0]<=span2[0] and span1[1]>=span2[1] )


def isNoun(edge):
    if edge.is_complete():
         leftS = edge.lhs()
         if type(leftS)==str:
            if leftS == 'NOUN':
                return True
            return False
         
         for key in leftS.keys():
             if type(key)!=str and leftS[key]=='NOUN':
                 return True
    return False

def containsNoun(edgeSide):
    #if type(edgeSide.lhs()) == str:
    #    return 0
    #print str(edgeSide)
    c = 0
    for symbol in edgeSide:
        if type(symbol)==str:
            if symbol == 'NOUN':
                c+=1
            continue
        for key in symbol.keys():
            if type(key)!=str and symbol[key]=='NOUN':
                c+=1
    
    return c

def isContained(span, spans):        
    for span2 in spans:
        if span2 == span: continue
        a=span[0]
        b=span[1]
        c=span2[0]
        d=span2[1]    
        if not (a<c or b>d):        
            #if span == (1,4):sys.stderr.write(str(span2))
            return True
    return False

def findUncrossingNPs(chart, words, useCfg, countCrosses=False):    
    crosses=0
    cross=[]
    spans = findNPs(chart, useCfg)
    if not countCrosses:
        for i in range(len(words)):
            sys.stdout.write('_')
            print
    keptSpans=set()
    for span in spans:
        #displaySpan(span)
        if not isContained(span, spans):
            keptSpans.add(span)
    
    
    for span in keptSpans:    
        if not countCrosses:
            displaySpan(span, len(words))
        for span2 in keptSpans:
            if isCrossing(span, span2):
                cross.append((span, span2))
                crosses+=1
        
    if not countCrosses:
        print ' '.join(words)
        for cr in cross:
            print '\t'.join([' '.join(words[sp[0]:sp[1]]) for sp in cr])
    else:
        return crosses
    
def isCrossing(span1, span2):        
    a=span1[0]
    b=span1[1]
    c=span2[0]
    d=span2[1]
    if a<c and c<b and b<d:
        return True
    return False


def printTagging(sen, spans):
    posStart=set()
    posInt=set()
    for span in spans:
        posStart.add(span[0])
        for i in range(span[0]+1, span[1]):
            posInt.add(i)
        
    for c, line in enumerate(sen):
        if c in posInt:
            tag = 'I-NP'
        elif c in posStart:
            tag = 'B-NP'
        else:
            tag = 'O'
    
        print '\t'.join((line.strip('\n'),tag))

def serializeParse(chart, toks, words, out):    
    out.write(' '.join(toks)+'\n'+' '.join(words)+'\n')
    for edge in chart.edges():
        if edge.is_complete():
            out.write(repr(edge)+'\n')
    print    
    

def displaySpan(span, senLength):
    for i in range(senLength):
        if i<span[0] or i>=span[1]:
            sys.stdout.write('.')
        else:
            sys.stdout.write('_')
    print
    

def x():
#if __name__=='__main__':
    optfunc.run(main)

profile = False

if __name__=='__main__':    
    if profile:    
        import cProfile
        cProfile.run('x()')
    else:
        x()
