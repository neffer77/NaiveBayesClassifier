
import requests
import logging
import base64
import time
import random
import binascii
from pandas import DataFrame as DF
import pandas as pd
import numpy
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer


logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Server(object):
    url = 'https://mlb.praetorian.com'
    log = logging.getLogger(__name__)

    def __init__(self):
        self.session = requests.session()
        self.binary  = None
        self.hash    = None
        self.wins    = 0
        self.targets = []

    def _request(self, route, method='get', data=None):
        while True:
            try:
                if method == 'get':
                    r = self.session.get(self.url + route)
                else:
                    r = self.session.post(self.url + route, data=data)
                if r.status_code == 429:
                    raise Exception('Rate Limit Exception')
                if r.status_code == 500:
                    raise Exception('Unknown Server Exception')

                return r.json()
            except Exception as e:
                self.log.error(e)
                self.log.info('Waiting 60 seconds before next request')
                time.sleep(60)

    def get(self):
        r = self._request("/challenge")
        self.targets = r.get('target', [])
        self.binary  = base64.b64decode(r.get('binary', ''))
        return r

    def post(self, target):
        r = self._request("/solve", method="post", data={"target": target})
        self.wins = r.get('correct', 0)
        self.hash = r.get('hash', self.hash)
        self.ans  = r.get('target', 'unknown')
        return r

if __name__ == "__main__":
    import random

    # create the server object
    s = Server()


    #create dataset for machine learning classifier
    #bin,targets = addData(1000)

    #create dataframe
    #df = DF ({'binary': bin, 'targets': targets})
    df = DF
    #read in data frame from csv
    df = df.from_csv("C:\Users\conno_000\Desktop\machLearningChallengeData.csv")
    #df = df.dropna(how='any')  
    

    #binaries = df['binary']

    #turn binary into hexadecimal
    #for i in range(len(binaries)):
     #   binaries[i] = binascii.hexlify(binaries[i])
    

    #df['binary'] = binaries

    #combine dataframes
    #frames = [df,df2]

    #df = pd.concat(frames)


    from sklearn.feature_extraction.text import CountVectorizer

    vec_opts = {
        "ngram_range": (1, 4),  # allow n-grams of 1-4 words in length (32-bits)
        "analyzer": "word",     # analyze hex words
        "token_pattern": "..",  # treat two characters as a word (e.g. 4b)
        "min_df": 0.0005,          # for demo purposes, be very selective about features
    }

    #create count vectorizor
    vectorizer = CountVectorizer(**vec_opts)
    
    #fit to model
    X = vectorizer.fit_transform(df['binary'].values, df['targets'].values)

    idf_opts = {"use_idf": True}
    idf = TfidfTransformer(**idf_opts)

    # perform the idf transform
    X = idf.fit_transform(X)


    #create naive bayes classifier
    classifier = MultinomialNB()
    classifier.fit(X, df['targets'].values)


    df2 = DF
    
    #status updates
    wins = 0
    testWins = s.wins
    maxWins = 0

        
    for _ in range(600):
        #get binary
        s.get()

        #convert to hexadecimal
        hex =  binascii.hexlify(s.binary)
    
        #predict ISA
        a = vectorizer.transform([hex])
        p = classifier.predict(a)
        target = p[0]
        s.post(target)

        #count consecutive wins in a row
        if s.wins == testWins:
            if wins > maxWins:
                maxWins = wins
            wins = 0
        else:
            wins = wins + 1
        testWins = s.wins
        
        
        print wins

        s.log.info("Guess:[{: >9}]   Answer:[{: >9}]   Wins:[{: >3}]".format(target, s.ans, s.wins))

        # 500 consecutive correct answers are required to win
        # very very unlikely with current code
        if s.hash:
            s.log.info("You win! {}".format(s.hash))
            f = s._request("/hash" , method="post", data={"email": "connor.neff77@gmail.com"})
            print f
            quit()
