#!/usr/bin/env python3

import subprocess
from EventDetective import EventDetective
from operator import itemgetter
from collections import Counter

class EventDetectiveChart(EventDetective):
    
    def simNoGeo(self):
        tweetList = []
        with open('corpus/5mei_all.txt', 'r') as f:
            for line in f:
                tweetList.append(line)
        
        for tweets,label in self.events:
            if '2015-05-05' in tweets[0]['localTime']:
                tweets = sorted(tweets, key=itemgetter('unixTime'))
                importantWords = self._getImportantWords(2,tweets)
                print(tweets)
                eventStart = tweets[0]['localTime']
                eventEnd = tweets[-1]['localTime']
                eventIntervalTweets = []
                # itereren we over het interval van huidige event?
                intervalIter = False
                        
                for tweet in tweetList:
                    if intervalIter:
                        wordCount = 0
                        for word,n in importantWords:
                            if word in tweet:
                                wordCount += 1
                        if wordCount > 1:
                            eventIntervalTweets.append(tweet)
                            
                    if eventStart in tweet:
                        intervalIter = True
                    elif eventEnd in tweet:
                        break
                    
                tweets.extend(eventIntervalTweets)

            # TODO woorden die door meerdere gebruikers worden genoemd (meer dan 1x voorkomen)
            
            # TODO
            # find hashtags (min 2 people)
            #for tweet in tweets:
            #    for word in tweet['tokens']:
            #        if word.startswith("#")
         
    # geeft de n hoogste tf waarden
    def _getImportantWords(self, n, tweets):
        result = Counter()
        for tweet in tweets:
            result.update(tweet['tokens'])
        #reslist = list(result.keys())
        #print(reslist)
        #for word in reslist:
        #    if word.startswith('#'):
        #        del result[word]
        return(result.most_common(n))
            
    def generateMarkers(self):
        print("Creating Google Maps markers & graphs...")
        
        js = open('vis/map/js/markers.js','w')
        js.write('var locations = [')
        
        for tweets,label in self.events:
            writableCluster = ''
            gh = []
            i = 0
            avgLon = 0
            avgLat = 0
            tweets = sorted(tweets, key=itemgetter('unixTime'))
            plotData = '['
            prevTime = 0
            tweetSimTime = []

            for tweet in tweets:
                i = i + 1
                
                tweetSimTime.append(tweet)
                # Meer dan een minuut tussen de tweets, zet de in tweetSimTime 
                # verzamelde tweets in de grafiek
                if tweet['unixTime'] - prevTime > 60 and prevTime != 0:
                    # prevTime != 0 betekent dat dit niet de eerste tweet mag zijn die
                    # gelijk al in de grafiek gezet wordt door vergelijking met 0
                    #avgTime = 0
                    tweetText = ""
                    
                    for simTimeTweet in tweetSimTime:
                        tweetText += tweet['text'].replace("'", "\\'") + "<br/>"
                        #avgTime += simTimeTweet['unixTime']
                    
                    #avgTime /= len(tweetSimTime)
                    # begin/eindtijd/middelpunt van een piek in de grafiek
                    beginTime = tweetSimTime[0]['unixTime']
                    endTime = tweetSimTime[-1]['unixTime']
                    avgTime = (beginTime + endTime)/2
                    # event tweets zelf
                    plotData += "{"
                    plotData += "x:new Date({}*1000),y:{},tweetData:'{}'".format(avgTime,len(tweetSimTime),tweetText)
                    plotData += "},"
                    # reset tweetSimTime
                    tweetSimTime = []
                
                gh.append(tweet['geoHash'])
                avgLon += float(tweet["lon"])
                avgLat += float(tweet["lat"])
                # backslashes voor multiline strings in Javascript
                writableCluster += "{} {} {} {}<br/><br/>".format(tweet['localTime'], tweet['geoHash'], tweet['user'], tweet['text']).replace("'", "\\'")
                prevTime = tweet['unixTime']
            # Bepaal het Cartesiaans (normale) gemiddelde van de coordinaten, de afwijking (door vorm
            # van de aarde) zal waarschijnlijk niet groot zijn omdat het gaat om een klein vlak op aarde...
            # Oftewel, we doen even alsof de aarde plat is ;-)
            avgLon /= i
            avgLat /= i
            plotData += ']'
            js.write("['{}', {}, {}, '{}', {}],".format(writableCluster,avgLat,avgLon,label,plotData))
        
        js.write('];')
        js.close()    
        
if __name__ == "__main__":
    detective = EventDetectiveChart()
    #detective.simNoGeo()
    detective.generateMarkers()