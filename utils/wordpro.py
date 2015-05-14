import nltk,re, pprint
from BeautifulSoup import BeautifulSoup
from nltk.corpus import conll2000


def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def stripAllTags(context):
    if context is None:
        return None
    return ''.join(BeautifulSoup(context).findAll(text=True))

#grammar = r"""
#NP: {<DT|PP\$>?<JJ>*<NN>}
#    {<NNP>+}
#"""

def chunkingword(content):
    grammar = r"""
    NP: {<DT|JJ|NN.*>+} # Chunk sequences of DT, JJ, NN
    PP: {<IN><NP>} # Chunk prepositions followed by NP 
    VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments 
    CLAUSE: {<NP><VP>} # Chunk NP, VP
    """
    result = ""
    cp = nltk.RegexpParser(grammar)

    text = stripAllTags(content)
    ret1 = ie_preprocess(text)
    print "======================"
    print "======================"
    print "======================"
    print ret1
    for b in ret1:
        text2 = b
        result = cp.parse(b)
        print text2
        print "----------------------------------------------"
        print result
        print "----------------------------------------------"
    return result 

