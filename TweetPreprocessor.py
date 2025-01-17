#!/usr/bin/python3

"""
#################
TWEETPREPROCESSOR
#################
Maakt op dit moment een lijst van tweet dictionaries, gegeven een
.txt-bestand met tweets in het formaat:

tekst<TAB>lengtegraad breedtegraad<TAB>gebruikersnaam<TAB>tijd

Een tweet-dictionary bevat de volgende (keys) gegevens voor elke tweet:
* text      : de tekst
* tokens    : lijst van woorden (getokeniseerde tekst)
* lon       : de lengtegraad
* lat       : de breedtegraad
* user      : de gebruikersnaam
* unixTime  : lokale tijd, geconverteerd naar Unix Time
* localTime : lokale tijd, zoals weergegeven in de tweet
* geoHash   : de geoHash waarin deze tweet is gepost
"""

import re, math, time, datetime
from modules import geohash
from collections import defaultdict

class TweetPreprocessor:
    
    def __init__(self, tweetFile):
        # SETTINGS
        self.HASH_ACCURACY = 7 # precisie van geoHash
        
        # regex pattern voor simpele tokenisatie: alles behalve letters, cijfers en 
        # underscores wordt vervangen door een spatie
        #self.pat = re.compile('[\W]+')
        # alternatief pattern waarbij #'s en @'s worden behouden
        self.pat = re.compile(r"[^a-zA-Z0-9#@]+")
        # maak een lijst met Nederlandse stopwoorden
        self.stoplist = []
        with open("corpus/stopwords.txt") as stopwords:
            # stopwords.txt: stopwoorden van NLTK + handmatig toegevoegde stopwoorden
            for stopword in stopwords:
                self.stoplist.append(stopword.strip())
        # maak een lijst van tweet dictionaries
        self.tweetDicts = []
        self._createTweetDicts(tweetFile)
        
    def _tokenize(self, text):
        tokens = text.split()
     
        # filter links
        for word in tokens[:]:
            if "http" in word:
                tokens.remove(word)
        filterLinkText = ' '.join(tokens)
        # vervang alles behalve letters/cijfers door een spatie
        tokens = self.pat.sub(' ', filterLinkText).lower().split()
        # filter stopwoorden, cijfers en losse karakters
        for word in tokens[:]:
            if word in self.stoplist or word.isdigit() or len(word) < 2:
                tokens.remove(word)

        return tokens
       
    # Maak de lijst van tweet dictionaries
    def _createTweetDicts(self, tweetFile):
        tweetDicts = []
        
        # is tweetFile een file (string) of een andere iterable?
        if type(tweetFile) == str:
            f = open(tweetFile)
            print("Creating tweet dictionaries for ", tweetFile, "...", sep = "")
        else:
            f = tweetFile

        for line in f:
            tweetElements = line.strip().split('\t')
            text = tweetElements[0]
            tokens = self._tokenize(text)
            
            if len(tweetElements) == 4:
                # tweets MET coordinaten
                coords = tweetElements[1].split()
                lat, lon = float(coords[1]), float(coords[0])
                # maak een geoHash met precisie HASH_ACCURACY
                geoHash = geohash.encode(lat, lon, self.HASH_ACCURACY)
                # converteer de tijd van de tweet naar Unix Time
                tweetTime = ' '.join(tweetElements[3].split()[:2])
                unixTime = int(time.mktime(datetime.datetime.strptime(tweetTime, "%Y-%m-%d %H:%M:%S").timetuple()))
                # zet alle waarden in een tweet dictionary
                self.tweetDicts.append({"text"      : text,
                                        "tokens"    : tokens,
                                        "lon"       : lon,
                                        "lat"       : lat,
                                        "user"      : tweetElements[2],
                                        "unixTime"  : unixTime,
                                        "localTime" : tweetTime,
                                        "geoHash"   : geoHash})
            elif len(tweetElements) == 3:
                # tweets ZONDER coordinaten
                tweetTime = ' '.join(tweetElements[2].split()[:2])
                unixTime = int(time.mktime(datetime.datetime.strptime(tweetTime, "%Y-%m-%d %H:%M:%S").timetuple()))
                self.tweetDicts.append({"text"      : text,
                                        "tokens"    : tokens,
                                        "user"      : tweetElements[1],
                                        "unixTime"  : unixTime,
                                        "localTime" : tweetTime})
            
        if type(tweetFile) == str:
            f.close()
            
    def getTweetDicts(self):
        return self.tweetDicts
