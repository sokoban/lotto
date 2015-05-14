import nltk,re, pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Text, Column, Integer, String, DateTime
from BeautifulSoup import BeautifulSoup
from nltk.corpus import conll2000

Base = declarative_base()

engine = create_engine('mysql://root:tnwlEkfkdgo^7@221.143.42.85:19999/netscan_server')

class Newsfeeds(Base):
    __tablename__ = "newsfeeds"

    seqno = Column(Integer, primary_key=True)
    newstitle = Column(String(500))
    uriaddr = Column(String(500))
    sitename = Column(String(300))
    description = Column(Text)
    regdt = Column(DateTime)
    publisheddate = Column(DateTime)
    titlecategory = Column(String(100))
    alertflag = Column(Integer)

    def __init__(self, newstitle=None,uriaddr=None, sitename=None, description=None, regdt=None, publisheddate=None, titlecategory=None, alertflag=None):
        self.newstitle = newstitle
        self.sitename = sitename
        self.description = description
        self.regdt = regdt
        self.publisheddate = publisheddate
        self.titlecategory = titlecategory
        self.alertflag = alertflag


def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

string = "this is a test"
ie_preprocess(string)

print engine.execute("select 1").scalar()

session = sessionmaker(bind=engine)
sess = session()
ret = sess.query(Newsfeeds).filter(Newsfeeds.newstitle.like('cve%')).limit(1)

def stripAllTags(context):
    if context is None:
        return None
    return ''.join(BeautifulSoup(context).findAll(text=True))

#grammar = r"""
#NP: {<DT|PP\$>?<JJ>*<NN>}
#    {<NNP>+}
#"""

grammar = r"""
NP: {<DT|JJ|NN.*>+} # Chunk sequences of DT, JJ, NN
PP: {<IN><NP>} # Chunk prepositions followed by NP 
VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments 
CLAUSE: {<NP><VP>} # Chunk NP, VP
"""
cp = nltk.RegexpParser(grammar)

for a in ret:
    print a.newstitle 
    text = stripAllTags(a.description)
    ret1 = ie_preprocess(text)
    for b in ret1:
        #print b
        text2 = b
        result = cp.parse(b)
        print result
        #test_sents = conll2000.chunked_sents(text,chunk_types=['NP'])
        #print cp.evaluate(test_sents)

#cp2 = nltk.RegexpParser('CHUNK: {<V.*> <TO> <V.*>}')
#brown = nltk.corpus.brown
#for sent in brown.tagged_sents():
#    tree = cp2.parse(text2)
#    for subtree in tree.subtrees():
#        #print subtree
#        if subtree.node == 'CHUNK': print subtree

