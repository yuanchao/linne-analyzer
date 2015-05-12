# -*- coding: utf-8 -*-

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
                   self._sampling[idx+2][varName] < self._sampling[idx+1][varName] :

                    self._index = idx
                    break
                    
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

            #print threshold, startIdx, endIdx
            idx = startIdx + 1
            while idx < (endIdx - 1) and (self._sampling[idx][varName] < threshold):
                idx = idx + 1

            self._index = idx
            #print idx, self._sampling[idx][varName]

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

        except IndexError:
            print "[Error] Unexpected Index."

    def find_vowel_id(self, target, duration = 0.):
        VOWEL = {'a': 0,
                 'o': 1,
                 'e': 2,
                 'r': 2,
                 'ei': 3,
                 'i': 4,
                 'u': 5,
                 'v': 6,
                 'n': 7,
                 'ng': 7}

        try:
            currIdx = self._index
            endTime = self._sampling[currIdx]["Timestamp"]+duration

            if duration==0. or endTime > self._maxTime:
                endTime = self._maxTime

            startIdx = self._index
            endIdx = self._sampling._data.index(self._sampling.search(endTime))

            #print startIdx, currIdx, endIdx

            vow_start = -1
            vow_end = -1

            for idx in range(currIdx+1, endIdx-5):
                #print idx, self._sampling[idx]["Vowel ID"]
                if vow_start == -1 :
                   if self._sampling[idx]["Vowel ID"] == VOWEL[target] and \
                      self._sampling[idx+1]["Vowel ID"] == VOWEL[target] and \
                      self._sampling[idx+2]["Vowel ID"] == VOWEL[target]:
                    vow_start = idx
                    idx += 3

                else : #vow_start != -1 and \
                   if self._sampling[idx]["Vowel ID"] != VOWEL[target] and \
                      self._sampling[idx+2]["Vowel ID"] != VOWEL[target] and \
                      self._sampling[idx+5]["Vowel ID"] != VOWEL[target] :
                       vow_end = idx
                       break

            if vow_start == -1:
                vow_start = startIdx
            if vow_end == -1:
                vow_end = endIdx - 3

            # use SV as vowel part ending
            sv_max = -1
            lowIdx = endIdx
            for idx in range(vow_start, endIdx-3):
                if self._sampling[idx]["Spectrum Variance"] > sv_max:
                    sv_max = self._sampling[idx]["Spectrum Variance"]

                if self._sampling[idx]["Spectrum Variance"] < 0.35 * sv_max:
                    lowIdx = idx
                    break

            if lowIdx < vow_end and not target == 'u':
                vow_end = lowIdx

            # add some buffer area
            vow_len = vow_end - vow_start

            if vow_start == currIdx+1:  # first vowel
                vow_start = int(vow_start + 0.15 * vow_len)
            else:
                vow_start = int(vow_start + 0.10 * vow_len)

            vow_end = int(vow_end - 0.05 * vow_len)

            #print vow_start, vow_end

            start_time = int(self._sampling[vow_start]["Timestamp"] * 1000)
            end_time = int(self._sampling[vow_end]["Timestamp"] * 1000)

            return start_time, end_time

        except IndexError:
            print "[Error] Unexpected Index."


    def find_vowel(self, target, duration = 0.):

        # 
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

        #print target
        #for phon in target.split('-'):
        #    print phon
        f_name = target+".wav"
        target = target.split('-')[0]

        try:
            self.find_limits();

            #self.skip_empty();
            #m_offset = int( self._sampling[self._index]["Timestamp"] * 1000)
            m_offset = 0

            # find const.
            self._index = 0
            #p_zcr = self.find_peak("ZCR diff.", 0.1)
            if target.lower().find('d') == 0 :
                self._index = 2
                #self.find_max("ZCR diff.", 0.05)
            elif target.lower().find('fang') == 0 :
                self.find_max("ZCR diff.", 0.15)
            elif target.lower().find('fu') == 0 :
                self._index = 10
                self.find_max("ZCR diff.", 0.15)
            elif target.lower().find('fan') == 0 :
                self.find_min("ZCR diff.", 0.15)
                self.find_max("ZCR diff.", 0.05)
            elif target.lower().find('liao') == 0 :
                self.find_min("ZCR diff.", 0.1)
                self.find_max("ZCR diff.", 0.05)
            elif target.lower().find('p') == 0 :
                self.find_min("ZCR diff.", 0.1)
                self.find_max("ZCR diff.", 0.05)
            elif target.lower().find('shui') == 0 :
                self.find_min("ZCR diff.", 0.15)
            elif target.lower().find('shi') == 0 :
                self.find_min("ZCR diff.", 0.15)
            elif target.lower().find('shu') == 0 :
                self.find_min("ZCR diff.", 0.15)
            elif target.lower().find('q') == 0 :
                self.find_min("ZCR diff.", 0.15)
                self.find_max("ZCR diff.", 0.05)
            elif target.lower().find('x') == 0 :
                self._index = 10
                self.find_min("ZCR diff.", 0.1)
                self.find_max("ZCR diff.", 0.1)
            else :
                self.find_max("ZCR diff.", 0.1)

            #self._index = 0
            p_zcr = self._index

            #self._index = 0
            if target.lower().find('ch') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.35*self._maxSV, 0.2)
            elif target.lower().find('ci') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.5*self._maxSV, 0.2)
            elif target.lower().find('d') == 0 :
                self._index = 0
                self.find_rise("Spectrum Variance", 0.3*self._maxSV, 0.2)
            elif target.lower().find('fang') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.3*self._maxSV, 0.2)
            elif target.lower().find('fan') == 0 :
                self._index = 5
                self.find_min("Spec. Var. diff.", 0.15)
                self.find_max("Spec. Var. diff.", 0.05)
            elif target.lower().find('f') == 0 or \
                 target.lower().find('g') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.3*self._maxSV, 0.2)
            elif target.lower().find('h') == 0 :
                self._index = 0
                self.find_rise("Spectrum Variance", 0.35*self._maxSV, 0.2)
            elif target.lower().find('ji') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.35*self._maxSV, 0.2)
            elif target.lower().find('k') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.45*self._maxSV, 0.2)
            elif target.lower().find('l') == 0 or \
                 target.lower().find('m') == 0 or \
                 target.lower().find('n') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.3*self._maxSV, 0.2)
            elif target.lower().find('o') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.5*self._maxSV, 0.2)
            elif target.lower().find('pi') == 0 :
                self._index = 5
                self.find_min("Spec. Var. diff.", 0.1)
                self.find_max("Spec. Var. diff.", 0.1)
            elif target.lower().find('po') == 0 :
                self._index = 5
                self.find_min("Spec. Var. diff.", 0.1)
                self.find_max("Spec. Var. diff.", 0.05)
            elif target.lower().find('p') == 0 :
                self._index = 7
                self.find_rise("Spectrum Variance", 0.5*self._maxSV, 0.2)
            elif target.lower().find('q') == 0 :
                self._index = 2
                self.find_min("Spec. Var. diff.", 0.1)
                self.find_max("Spec. Var. diff.", 0.05)
            elif target.lower().find('shu') == 0 :
                self._index = 5
                self.find_rise("Spectrum Variance", 0.5*self._maxSV, 0.2)
            elif target.lower().find('shi') == 0 :
                self._index = 2
                self.find_min("Spec. Var. diff.", 0.15)
                self.find_max("Spec. Var. diff.", 0.1)
            elif target.lower().find('te') == 0 :
                self._index = 2
                self.find_rise("Spectrum Variance", 0.5*self._maxSV, 0.2)
            elif target.lower().find('r') == 0 or \
                 target.lower().find('s') == 0 or \
                 target.lower().find('t') == 0 or \
                 target.lower().find('w') == 0 or \
                 target.lower().find('y') == 0 or \
                 target.lower().find('z') == 0 :
                self._index = 2
                self.find_rise("Spectrum Variance", 0.3*self._maxSV, 0.2)
            elif target.lower().find('x') == 0 :
                self._index = 2
                self.find_rise("Spectrum Variance", 0.55*self._maxSV, 0.2)
            else :
                self._index = 5
                self.find_max("Spec. Var. diff.", 0.1);

            #self._index = 0
            p_sv = self._index

            if p_sv > p_zcr:
                # pre-utterance
                m_prevoice = int(self._sampling[p_sv]["Timestamp"] * 1000 - m_offset)
            else:
                m_prevoice = int(self._sampling[p_zcr]["Timestamp"] * 1000 - m_offset)

            if target.lower().find('pe') == 0 :
               m_prevoice = int(self._sampling[p_zcr]["Timestamp"] * 1000 - m_offset)
            elif target.lower().find('xia') == 0 or \
               target.lower().find('xio') == 0 or \
               target.lower().find('xiu') == 0 or \
               target.lower().find('xua') == 0 :
                m_prevoice = int(self._sampling[p_sv]["Timestamp"] * 1000 - m_offset)
            #print "p_sv, p_zcr", p_sv, p_zcr
            #print p_sv, p_zcr, self._index

            self._index = max(p_sv, p_zcr) + 5
            #self.find_max("ZCR", 0.15);
            #self.find_min("ZCR", 0.15);
            #print p_sv, p_zcr, self._index

            #self.find_rise("Spectrum Variance", 0.7*self._maxSV, 0.5);

            m_pho = target.split('-')[0]
            if m_pho[-1].isdigit():
                m_pho = m_pho[:-1]

            if target.lower().find('ng') > 0 :
                m_cons, m_vowel = self.find_vowel_id('n')
            elif target.lower().find('ei') > 0 :
                m_cons, m_vowel = self.find_vowel_id('ei')
            elif target.lower().find('ie') > 0 :
                m_cons, m_vowel = self.find_vowel_id('ei')
            elif target.lower().find('iu') > 0 :
                m_cons, m_vowel = self.find_vowel_id('o')
            elif target.lower().find('er') > 0 :
                m_cons, m_vowel = self.find_vowel_id('e')
            elif target.lower().find('ai') > 0 :
                m_cons, m_vowel = self.find_vowel_id('ei')
            elif target.lower().find('ao') > 0 :
                m_cons, m_vowel = self.find_vowel_id('o')
            elif target.lower().find('ou') > 0 :
                m_cons, m_vowel = self.find_vowel_id('u')
            elif target.lower().find('ui') > 0 :
                m_cons, m_vowel = self.find_vowel_id('ei')
            elif target.lower().find('uo') > 0 :
                m_cons, m_vowel = self.find_vowel_id('o')
            elif target.lower().find('ve') > 0 :
                m_cons, m_vowel = self.find_vowel_id('ei')
            elif target.lower().find('ci') > 0 :
                m_cons, m_vowel = self.find_vowel_id('e')
            else :
                m_cons, m_vowel = self.find_vowel_id(m_pho[-1].lower())
                #print m_pho
            #m_cons, m_vowel = self.find_vowel_id(target[-1].lower())

            #print m_cons, m_vowel

            m_cons = m_cons - m_offset
            m_vowel = - int(m_vowel - m_offset)

            pho_file = open("pinying.csv")
            pho_tab = csv.DictReader(pho_file)

            #print target
            print f_name+"="+m_pho.lower()+"," + \
                  ("%d,%d,%d,%d,%d" %  \
                   (m_offset, m_cons, m_vowel, \
                        m_prevoice, m_overlap))

            m_target = m_pho.replace("lv", "lü")
            m_target = m_pho.replace("nv", "nü")

            #for row in pho_tab:
            #    if row['漢語拼音方案'].lower() == m_target:
            #        print target+".wav"+"="+row['國語注音符號第一式']+"," + \
            #              ("%d,%d,%d,%d,%d" %  \
            #              (m_offset, m_cons, m_vowel, m_prevoice, m_overlap))

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

