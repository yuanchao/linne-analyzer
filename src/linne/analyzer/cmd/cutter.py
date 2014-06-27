import os
import re
import csv
import sys
import codecs
import traceback

import numpy
from linne.analyzer.sound import Table as SoundTable
from linne.analyzer.sound import Sound
from linne.analyzer.sampling import SamplingFile
from linne.analyzer.audacity import LabelFile
from linne.analyzer.phonetic import Ipa

class Filter:
    def __init__(self):
        self._index = 0
        self._currTime = 0
        self._maxSV = 0.
        self._maxZCR = 0.
        self._maxTime = 0.

    def find_limits(self, duration = 0):
        currIdx = self._index
        endTime = self._sampling[currIdx]["Timestamp"]+duration

        if duration == 0.:
            self._maxTime = -1

        try:
            for frame in self._sampling:
                if frame["Spectrum Variance"] > self._maxSV:
                    self._maxSV = frame["Spectrum Variance"]

                if frame["ZCR"] > self._maxZCR:
                    self._maxZCR = frame["ZCR"]

                if duration == 0 and frame["Timestamp"] > self._maxTime:
                    self._maxTime = frame["Timestamp"]
        
                if duration != 0 and frame["Timestamp"] > endTime:
                    break
#            print "max time, ZCR, SV: ", self._maxTime, self._maxZCR, self._maxSV

        except IndexError:
            print "[Error] Unexpected Index."

    def find_max(self, varName, duration = 0.):
        try:
            maxVar = -9999.
            currIdx = self._index
            endTime = self._sampling[currIdx]["Timestamp"]+duration

            if duration==0. or endTime > self._maxTime:
                endTime = self._maxTime

            startIdx = self._index
            endIdx = self._sampling._data.index(self._sampling.search(endTime))

            for idx in range(currIdx, endIdx-1):
                if self._sampling[idx][varName] > maxVar:
                    maxVar = self._sampling[idx][varName]
                    self._index = idx
                    
#            print "Max ", varName, " at time, value: ", self._sampling[self._index]["Timestamp"], self._sampling[self._index][varName]

        except IndexError:
            print "[Error] Unexpected Index."

    def find_min(self, varName, duration = 0.):
        try:
            minVar = 9999.
            currIdx = self._index
            endTime = self._sampling[currIdx]["Timestamp"]+duration

            if duration==0. or endTime > self._maxTime:
                endTime = self._maxTime

            startIdx = self._index
            endIdx = self._sampling._data.index(self._sampling.search(endTime))

            for idx in range(currIdx, endIdx-1):
                if self._sampling[idx][varName] < minVar:
                    minVar = self._sampling[idx][varName]
                    self._index = idx
                    
#            print "Min ", varName, " at time, value: ", self._sampling[self._index]["Timestamp"], self._sampling[self._index][varName]

        except IndexError:
            print "[Error] Unexpected Index."

    def find_peak(self, varName, duration = 0.):
        try:
            currIdx = self._index
            endTime = self._sampling[currIdx]["Timestamp"]+duration

            if duration==0. or endTime > self._maxTime:
                endTime = self._maxTime

            startIdx = self._index
            endIdx = self._sampling._data.index(self._sampling.search(endTime))

            for idx in range(currIdx+1, endIdx-3):
                if self._sampling[idx][varName] > self._sampling[idx-1][varName] and \
                   self._sampling[idx+1][varName] < self._sampling[idx][varName] and \
                   self._sampling[idx+2][varName] < self._sampling[idx+1][varName] : #and \
#                   self._sampling[idx+3][varName] < self._sampling[idx+2][varName]:
                    self._index = idx
                    break
                    
#            print "Max ", varName, " at time, value: ", self._sampling[self._index]["Timestamp"], self._sampling[self._index][varName]

        except IndexError:
            print "[Error] Unexpected Index."

    def find_deep(self, varName, duration = 0.):
        try:
            currIdx = self._index
            endTime = self._sampling[currIdx]["Timestamp"]+duration

            if duration==0. or endTime > self._maxTime:
                endTime = self._maxTime

            startIdx = self._index
            endIdx = self._sampling._data.index(self._sampling.search(endTime))

            for idx in range(currIdx+1, endIdx-3):
                if self._sampling[idx][varName] < self._sampling[idx-1][varName] and \
                   self._sampling[idx+1][varName] > self._sampling[idx][varName] and \
                   self._sampling[idx+2][varName] > self._sampling[idx+1][varName] and \
                   self._sampling[idx+3][varName] > self._sampling[idx+2][varName]:
                    self._index = idx
                    break
                    
#            print "Max ", varName, " at time, value: ", self._sampling[self._index]["Timestamp"], self._sampling[self._index][varName]

        except IndexError:
            print "[Error] Unexpected Index."

    def find_rise(self, varName, threshold, duration = 0.):
        try:
            currIdx = self._index
            endTime = self._sampling[currIdx]["Timestamp"]+duration

            if duration==0. or endTime > self._maxTime:
                endTime = self._maxTime

            startIdx = self._index
            endIdx = self._sampling._data.index(self._sampling.search(endTime))

            idx = startIdx + 1
            while idx < (endIdx - 1) and self._sampling[idx][varName] < threshold:
                idx = idx + 1

            self._index = idx

#            print "Rise cut ", varName, " at time, value: ", self._sampling[self._index]["Timestamp"], self._sampling[self._index][varName]

        except IndexError:
            print "[Error] Unexpected Index."

    def find_fall(self, varName, threshold, duration = 0.):
        try:
            currIdx = self._index
            endTime = self._sampling[currIdx]["Timestamp"]+duration

            if duration==0. or endTime > self._maxTime:
                endTime = self._maxTime

            startIdx = self._index
            endIdx = self._sampling._data.index(self._sampling.search(endTime))

            idx = startIdx + 1
            while idx < (endIdx - 1) and self._sampling[idx][varName] > threshold:
                idx = idx + 1

            self._index = idx

#            print "Fall cut ", varName, " at time, value: ", self._sampling[self._index]["Timestamp"], self._sampling[self._index][varName]

        except IndexError:
            print "[Error] Unexpected Index."

    def find_vowel(self, target, duration = 0.):

        if target.find('b') >=0 or \
           target.find('d') >=0 or \
           target.find('f') >=0 or \
           target.find('c') ==0 or \
           target.find('j') ==0 or \
           target.find('s') ==0 or \
           target.find('w') ==0 or \
           target.find('y') ==0 or \
           target.find('x') ==0 or \
           target.find('z') ==0 or \
           target.find('p') >=0 :
            self.find_max("Spectrum Variance", 0.15);

        if target.find('m') >=0 or \
           target.find('n') >=0 or \
           target.find('g') >=0 or \
           target.find('k') >=0 or \
           target.find('h') >=0 :
            self.find_max("ZCR", 0.2);

        if target.find('c') == 0 or \
           target.find('w') == 0 or \
           target.find('z') == 0 :
            self.find_min("ZCR", 0.1);

        if target.find('b') >=0 or \
           target.find('d') >=0 or \
           target.find('f') >=0 or \
           target.find('j') >=0 or \
           target.find('y') >=0 or \
           target.find('p') >=0 :
            self.find_min("Spectrum Variance", 0.15);

        if target.find('g') >=0 or \
           target.find('b') >=0 or \
           target.find('k') >=0 or \
           target.find('t') >=0 :            
            self.find_max("ZCR diff.", 0.15);
      
        if target.find('f') ==0 :            
            self.find_min("ZCR", 0.1);
      
        if target.find('d') >=0 or \
           target.find('m') >=0 or \
           target.find('n') >=0 or \
           target.find('j') >=0 or \
           target.find('s') >=0 or \
           target.find('x') >=0 or \
           target.find('p') >=0 :
            self.find_max("Spec. Var. diff.", 0.15);

        m_cons = int(self._sampling[self._index]["Timestamp"] * 1000)

        self.find_max("Spectrum Variance", 0.2);
        m_max = self._sampling[self._index]["Spectrum Variance"]

        self.find_fall("Spectrum Variance", 0.8*m_max, 0.5);
        m_vowel = int(self._sampling[self._index]["Timestamp"] * 1000)

        return m_cons, m_vowel


    def skip_empty(self, startTime=0.):
        try:
            if startTime != 0.:
                self._index = self._sampling._data.index(self._sampling.search(startTime))

            while self._sampling[self._index]["Spectrum Variance"] < self._maxSV/200:
                self._index = self._index+1

        except IndexError:
            print "[Error] Unexpected Index."


    def process(self,soundTable,sampling,target):
        self._index = 0
        self._soundTable = soundTable
        self._sampling = sampling

        m_offset = 0
        m_cons = 0
        m_vowel = 0
        m_prevoice = 0
        m_overlap = 0

        try:
            self.find_limits();

            self.skip_empty();
            m_offset = int( self._sampling[self._index]["Timestamp"] * 1000)

            if target.find('w') ==0 and m_offset < 400 :
                self._index = self._index + 50
                self.find_rise("Spectrum Variance", 0.5, 0.5);
                m_offset = int( self._sampling[self._index]["Timestamp"] * 1000)

            if target.find('x') ==0:
                self._index = 50
                self.find_rise("ZCR", 0.05, 0.5);
                m_offset = int( self._sampling[self._index]["Timestamp"] * 1000) - 20.

            if target.find('c') ==0 or \
               target.find('h') ==0 or \
               target.find('s') ==0 or \
               target.find('j') ==0 or \
               target.find('f') ==0 :
#                target.find('f') >=0 or \
#                target.find('c') >=0 :
                m_offset = m_offset - 20.

            if target.find('d') ==0 or \
               target.find('j') ==0 :
                m_offset = m_offset - 5.

            if target.find('f') ==0 :
                self._index = self._index + 5

            #self.find_min("Spec. Var. diff.", 0.2);
            #self.find_peak("Spec. Var. diff.", 0.2);
            self.find_max("Spec. Var. diff.", 0.2);
            #self.find_max("ZCR diff.", 0.15);
            m_prevoice = int(self._sampling[self._index]["Timestamp"] * 1000 - m_offset)

            ##self.find_max("Spectrum Variance", 0.1);
            ##self.find_min("Spectrum Variance", 0.1);
            #self.find_max("ZCR", 0.15);
            #self.find_min("ZCR", 0.15);

            #self.find_rise("Spectrum Variance", 0.7*self._maxSV, 0.5);
            #m_cons = int(self._sampling[self._index]["Timestamp"] * 1000 - m_offset)

            #self.find_max("Spectrum Variance", 0.2);
            #m_max = self._sampling[self._index]["Spectrum Variance"]
            #self.find_fall("Spectrum Variance", 0.8*m_max, 0.5);
            #m_vowel = - int(self._sampling[self._index]["Timestamp"] * 1000 - m_offset)

            m_cons, m_vowel = self.find_vowel(target)

            m_cons = m_cons - m_offset
            m_vowel = - int(m_vowel - m_offset)

            print target+".wav"+"="+target+"," + \
                  ("%d,%d,%d,%d,%d" %  \
                   (m_offset, m_cons, m_vowel, \
                        m_prevoice, m_overlap))


#            for phonetic in phonetics:
#                points = [] 
#                cv = phonetic.breakdown()
#                for p in cv:
#                    try:
#                        res = self.search(p)["Timestamp"]
#                        points.append(res)
#                    except KeyError:
#                        print "[Error] %s is not existed in sound table(sound.csv)" %  p
#                    
#                points.append(self.highPass()["Timestamp"])
#                phonetic.points = points
        except IndexError:
            print "[Error] Unexpected termination. Not all phonetic is found."
            
            # When this exception happen , it means that analyzer can not 
            # found all the phonetic listed in the input file (.txt).
            
            # It should adjust the sound.csv according to the output
                        
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
		

    def search(self,symbol):
        print "Searching %s..." % symbol
        s = self._soundTable[symbol]
        while not s.passThreshold(self._sampling[self._index]):
            self._index = self._index+1
        frame = self._sampling[self._index]
        self._index = self._index + 1
        return frame
        
    def highPass(self):
        # A high pass filter on RMS. A dirty hack for right-endpoint searching
        while self._sampling[self._index]["RMS"] > 0.03:
            self._index = self._index+1
        frame = self._sampling[self._index]
        self._index = self._index + 1
        return frame

try:
	target = sys.argv[1]
except:
	print "Usage: %s name_of_sample " % sys.argv[0]
	exit(0)

table = SoundTable()
#print "Reading sound.csv..."
table.open("sound.csv")

samplingFile = SamplingFile()

filename = target + "-sampling.csv"
#print "Reading %s..." % filename
samplingFile.open(filename)

#filename = target + ".txt"
#print "Reading %s..." % filename
#
#f = codecs.open(filename,"r","utf-8")
#line = f.readline()
#phonetics = [ Ipa(item.strip()) for item in line.split(" ") ]

filter = Filter()
filter.process(table,samplingFile,target)

#labelFile = LabelFile()
#

#for p in phonetics:
#    try:
#        labels = p.toLabel()
#        for row in labels:
#            labelFile.append(row)
#    except IndexError:
#        print u"[Error] The detection of %s is incomplete. The rest of phonentic will be skipped in output" % p
#        break
#        
#filename = target + "-label.txt"
#print "Writing to %s..." % filename
#    
#labelFile.save(filename)

