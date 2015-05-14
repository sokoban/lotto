import os

#return 7 number array



class genlottonumber(db.Model):
    seqno = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100))
    genmethod = db.Column(db.Integer)
    firstnum = db.Column(db.Integer)
    secondnum = db.Column(db.Integer)
    thirdnum = db.Column(db.Integer)
    fourthnum = db.Column(db.Integer)
    fifthnum = db.Column(db.Integer)
    sixthnum = db.Column(db.Integer)
    luckynum = db.Column(db.Integer)
    regdt = db.Column(db.DateTime)



def gennumber(name):
    lottonum = genlottonumber()
    lottonum.username = name

    lottonum = [4,7,23,24,35,37,9]
    return lottonum
