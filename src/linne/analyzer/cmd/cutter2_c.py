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
        startTime = self._sampling[currIdx]["Timestamp"]
        endTime = self._sampling[-1]["Timestamp"]

        self._maxSV = 0.
        self._maxZCR = 0.
        self._maxTime = startTime + duration

        if duration == 0.:
            self._maxTime = self._sampling[-1]["Timestamp"]

        try:
            for frame in self._sampling:
                if frame["Spectrum Variance"] > self._maxSV:
                    self._maxSV = frame["Spectrum Variance"]

                if frame["ZCR"] > self._maxZCR:
                    self._maxZCR = frame["ZCR"]

                #if duration == 0 and frame["Timestamp"] > self._maxTime:
                #    self._maxTime = frame["Timestamp"]
        
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
        VOWEL = {'-': -1,
                 'a': 0,
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

            #if target == 'u':
            #print target
            #print startIdx, currIdx, endIdx

            vow_start = -1
            vow_end = -1

            for idx in range(currIdx+1, endIdx-3):
                #print idx, self._sampling[idx]["Vowel ID"]
                if vow_start == -1 :
                   if self._sampling[idx]["Vowel ID"] == VOWEL[target] and \
                      self._sampling[idx+2]["Vowel ID"] == VOWEL[target] and \
                      self._sampling[idx+3]["Vowel ID"] == VOWEL[target]:
                    vow_start = idx
                    idx += 2

                else : #vow_start != -1 and \
                   if self._sampling[idx]["Vowel ID"] != VOWEL[target] and \
                      self._sampling[idx+2]["Vowel ID"] != VOWEL[target] and \
                      self._sampling[idx+3]["Vowel ID"] != VOWEL[target] :
                       vow_end = idx
                       break

            if vow_start == -1:
                vow_start = startIdx + 2
            if vow_end == -1:
                vow_end = endIdx - 3

            # use SV as vowel part ending
            sv_max = -1
            lowIdx = endIdx
            for idx in range(vow_start, endIdx-3):
                if self._sampling[idx]["Spectrum Variance"] > sv_max:
                    sv_max = self._sampling[idx]["Spectrum Variance"]

                if self._sampling[idx]["Spectrum Variance"] < 0.5 * sv_max:
                    lowIdx = idx
                    break

            if lowIdx < vow_end : #and not target == 'u':
                vow_end = lowIdx

            # add some buffer area
            vow_len = vow_end - vow_start

            if vow_start == currIdx+1:  # first vowel
                vow_start = int(vow_start + 0.15 * vow_len)
            else:
                vow_start = int(vow_start + 0.10 * vow_len)

            vow_end = int(vow_end - 0.15 * vow_len)

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
            if startTime >= 0. :
                if startTime != 0.:
                    self._index = self._sampling._data.index(self._sampling.search(startTime))

                #self._index = 0
                #print self._maxSV, self._maxZCR
                while self._sampling[self._index]["Spectrum Variance"] < self._maxSV/100 and self._sampling[self._index]["ZCR"] < self._maxZCR/100:
                    self._index = self._index+1
            else :
                self._index = len(self._sampling) - 1
                while self._sampling[self._index]["Spectrum Variance"] < self._maxSV/100 and self._sampling[self._index]["ZCR"] < self._maxZCR/100:
                    self._index = self._index-1

        except IndexError:
            print "[Error] Unexpected Index."


    def process(self,soundTable,sampling,targets):
        self._index = 0
        self._soundTable = soundTable
        self._sampling = sampling

        m_offset = 0
        m_cons = 0
        m_vowel = 0
        m_prevoice = 0
        m_overlap = 0
        m_length = 0
        m_len_idx = 0
        m_end_idx = 0
        m_end = 0

        #print target
        #for phon in target.split('-'):
        #    print phon
        f_name = targets+".wav"
        target = targets.split('-')[0]
        n_target = len(targets.split('-'))

        try:
            # frame size is 30 ms / 4, typical blank: ~800 ms
            self._index = 50

            self.find_limits();

            self.skip_empty(-1); # get the ending point
            m_end_idx = self._index
            m_end = int(self._sampling[self._index]["Timestamp"] * 1000)

            self._index = 50
            #self._index = 100
            self.skip_empty(0.5);
            #m_offset = int(self._sampling[self._index]["Timestamp"] * 1000)

            #self.find_limits(0.27); # typical sound length is ~256 ms
            #self._index -= 5

#            if target.lower().find('bei') == 0 :
#                self._index -= 20
#                self.find_max("ZCR diff.", 0.05);
#                self._index -= 20

            m_offset = int(self._sampling[self._index]["Timestamp"] * 1000) - 10

            #print "offset, end: ", m_offset, m_end
            #print m_offset
            #print self._index
            #self.find_rise("ZCR", 0.05, 0.5);
            self.find_max("Spec. Var. diff.", 0.1);
            #self.find_rise("Spectrum Variance", 0.2*self._maxSV, 0.5);

            # set a reference point on pre-utterance
            tmp_index = self._index

            if target.lower().find('cuan') == 0 :
                self._index += 2
            m_prevoice = int(self._sampling[self._index]["Timestamp"] * 1000 - m_offset)
            self.find_max("Spec. Var. diff.", 0.2);
            if self._index - tmp_index < 10 :
                m_prevoice = int(self._sampling[self._index]["Timestamp"] * 1000 - m_offset)
            if m_prevoice > 60 :
                #m_overlap = int(m_prevoice/2)
                m_overlap = 30

            m_length = int((m_end - m_offset - m_prevoice)/n_target)
            m_len_idx = int((m_end_idx - tmp_index)/n_target)

            #print "Pre-utterance, Note length: ", m_prevoice, m_length
            self._index += 2

            # find consanent and vowel

            for m_i in range(n_target) :

                #self.find_rise("Spectrum Variance", 0.7*self._maxSV, 0.5);
                target_pre = ""
                target = targets.split('-')[m_i]

                if m_i > 0 :
                    target_pre = targets.split('-')[m_i-1]
                    m_offset = m_offset + m_prevoice + m_length - 150
                    self.find_min("Spec. Var. diff.", 0.2);
                    m_overlap = int(self._sampling[self._index]["Timestamp"] * 1000 - m_offset)
                    if m_overlap < 30 : m_overlap = 35
                    #m_overlap
                    self._index = tmp_index + m_len_idx * m_i - 10
                    self.find_max("Spec. Var. diff.", 0.2);
                    m_prevoice = 150
                    if abs(self._index - (tmp_index + m_len_idx * m_i)) < 10 :
                        m_prevoice = int(self._sampling[self._index]["Timestamp"] * 1000 - m_offset)
                
                if target.lower().find('gong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('jong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('kong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('jiong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('hong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('long') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('rong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('song') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('tong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('zhong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('zong') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('ong') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')

                elif target.lower().find('chuang') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('guang') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('a')
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('guan') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('a')
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('huan') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('a')
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('mang') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('-')
                elif target.lower().find('yang') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('geng') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')
                elif target.lower().find('deng') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('-')
                elif target.lower().find('qing') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('-')
                elif target.lower().find('qiang') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('-')
                elif target.lower().find('bing') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('jing') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('bin') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('lin') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('yin') == 0 : # both yin & ying
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('lang') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('leng') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('reng') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                    self._index += 50
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('ng') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')

                elif target.lower().find('han') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('bin') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('hun') == 0 : # also chun
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('pin') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('jin') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('gun') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('jun') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('lun') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('men') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                    
                #elif target.lower().find('bou') == 0 :
                #    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('moa') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')
                    
                elif target.lower().find('bei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('dei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('fei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('gei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('lei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('rei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('mei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('nei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('ei') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('ei')
                    
                elif target.lower().find('ie') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('ei')
                elif target.lower().find('jiu') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('liu') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('miu') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                    
                elif target.lower().find('ju') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('v')
                #elif target.lower().find('nu') == 0 :
                #    m_cons, m_vowel = self.find_vowel_id('v')
                elif target.lower().find('xu') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('v')
                elif target.lower().find('lvn') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('v')
                elif target.lower().find('qu') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('v')
                elif target.lower().find('yu') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('v')
                    
                elif target.lower().find('miu') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                elif target.lower().find('iu') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')
                    
                elif target.lower().find('er') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                    
                elif target.lower().find('bai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('chai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('chuai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('chuo') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('kai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('dai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('gai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('tai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('wai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('yai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('shei') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('shuai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('mai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('pai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('sai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('shai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('wai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('guai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('kuai') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('kou') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')
                elif target.lower().find('mou') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')
                elif target.lower().find('you') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')
                    
                elif target.lower().find('ai') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('ei')
                    
                elif target.lower().find('qiao') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('a')
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('ao') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                    
                elif target.lower().find('ou') > 0 :
                    #m_cons, m_vowel = self.find_vowel_id('o')!!!
                    m_cons, m_vowel = self.find_vowel_id('u')

                elif target.lower().find('gui') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('hui') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('kui') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('sui') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('shui') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('zui') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('i')
                elif target.lower().find('si') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('ui') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('ei')
                    
                elif target.lower().find('chuo') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('ruo') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('tuo') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('uo') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')
                    
                elif target.lower().find('oa') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('o')
                    
                elif target.lower().find('ren') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('re') == 0 :
                    self._index +=10
                    m_cons, m_vowel = self.find_vowel_id('i')
                    m_cons, m_vowel = self.find_vowel_id('o')
                    
                elif target.lower().find('she') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('u')
                    m_cons, m_vowel = self.find_vowel_id('e')
                elif target.lower().find('ve') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('ei')
                elif target.lower().find('ye') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('ei')
                elif target.lower().find('uan') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('n')
                elif target.lower().find('ue') > 0 :
                    m_cons, m_vowel = self.find_vowel_id('ei')
                    
                elif target.lower().find('ci') == 0 :
                    m_cons, m_vowel = self.find_vowel_id('-')
                else :
                    m_cons, m_vowel = self.find_vowel_id(target[-1].lower())
                #print target
                #m_cons, m_vowel = self.find_vowel_id(target[-1].lower())
                    
                #print "Consenant, Vowel: ", m_cons, m_vowel
                m_cons = m_cons - m_offset
                    
                if (m_vowel - m_offset - m_prevoice) > m_length :
                    m_vowel = m_offset + m_prevoice + m_length * 0.95
                    
                m_vowel = - int(m_vowel - m_offset)
                
                pho_file = open("pinying.csv")
                pho_tab = csv.DictReader(pho_file)

                #print target
                if m_i > 0 :
                    target = target_pre[-1]+'_'+target
                print f_name+"="+target.lower()+"," + \
                    ("%d,%d,%d,%d,%d" %  \
                         (m_offset, m_cons, m_vowel, \
                              m_prevoice, m_overlap))

                m_target = target.replace("lv", "lü")
                m_target = target.replace("nv", "nü")

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

