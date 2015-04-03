#!/usr/bin/env python
# Making Spectogram of an audio

import math
import numpy
import csv
import sys
import os
import scipy.io.wavfile as wav

from pylab import *

from sklearn import svm, metrics
from sklearn.externals import joblib

files = ["a a",
         "c o",
         "2 er",
         "3 e",
         "I i",
         "U u",
         "Y v",
         "N n"]

#m_in = len(files)
m_in = 0

try:
  Fs, sample = wav.read(sys.argv[1])
except:
  #  print "Usage: %s [wav file] " % sys.argv[0]
  print "Error opening %s " % sys.argv[1]
  exit(-1)

dt = 1.0 / Fs
t = arange(0.0, len(sample)*dt, dt)

NFFT = 1024       # the length of the windowing segments
Fs = int(1.0/dt)  # the sampling frequency

# Pxx is the segments x freqs array of instantaneous power, freqs is
# the frequency vector, bins are the centers of the time bins in which
# the power is computed, and im is the matplotlib.image.AxesImage
# instance

max_freq = 6000

ax1 = subplot(311)
plot(t[:len(sample)], sample)

ax2 = subplot(312, sharex=ax1)
  #ax2 = subplot(312)
Pxx, freqs, bins, im = specgram(sample, NFFT=NFFT, Fs=Fs, noverlap=900,
                                cmap=cm.jet)
ax2.set_ylim([200, 5500])

ss = abs(Pxx[2:NFFT*max_freq/Fs])
#ss = ss / amax(ss[:,int(len(bins)*0.4):int(len(bins)*0.6)])
ss = ss / amax(ss)
sl = 10 * np.log10(ss)

nbin = 8 * int(len(ss[:,])/8.)
sr = ss
sr = np.mean(sr[:nbin,].reshape(-1,8,len(bins)), 1)
fq = np.mean(freqs[2:nbin+2].reshape(-1,8),1)

ax2.pcolormesh(bins, fq, 10 * np.log(sr/amax(sr)), cmap=cm.jet)

classifier = joblib.load("linne_zh.pkl")

sk = []
sk0 = []
sk1 = []
skn = [[] for x in xrange(9)]
row = []

for idx in range(0, len(bins)) :
  for ifq in range(0, len(fq)) :
    row.append(10*log(sr[ifq, idx]/max(sr[:,idx])))
    
  sk.append(classifier.predict(row))     # the class id
  #sk.append(classifier.predict_proba(row)[:,1])     # the class id
  #sk.append(classifier.predict_proba(row))     # the class id
  #sk0.append(classifier.predict_proba(row)[:,1]*5)
  #sk1.append(classifier.predict_proba(row)[:,2]*5)

  for ii in range(0, 9) :
    skn[ii].append(classifier.predict_proba(row)[:,ii]*7)

  
  row = []
    
ax3 = subplot(313, sharex=ax1)
#plot(bins, sk[:,0])
#plot(bins, sk[1,:])
#plot(bins, sk[:,2])
#plot(bins, sk[:,3])
#plot(bins, sk[:,4])
#plot(bins, sk, lw=3)
#plot(bins, sk0)
#plot(bins, sk1)

for ii in range(8, 0, -1) :
  plot(bins, skn[ii], label=files[ii-1].split('/')[-1].split('.wav')[0])

plot(bins, sk, lw=3, color = '0.25')

#legend()
legend(bbox_to_anchor=(0.83, 0.02), loc=3, borderaxespad=0.)

#ax3.set_ylim([0, 1])
ax3.set_ylim([-1.5, 7.5])

savefig(sys.argv[1].split(".wav")[0]+".png")
#  clf()

#show()
