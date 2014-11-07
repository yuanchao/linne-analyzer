#!/usr/bin/env python
# Making Spectogram of an audio

import math
import numpy
import csv
import sys
import os
import scipy.io.wavfile as wav

from pylab import *

files = ["voicebank/A.wav",
         "voicebank/I.wav",
         "voicebank/O.wav",
         "voicebank/E.wav",
         "voicebank/U.wav",
         "voicebank/N.wav",
         "voicebank/Ka.wav",
         "voicebank/Ki.wav",
         "voicebank/Ko.wav",
         "voicebank/Ke.wav",
         "voicebank/Ku.wav",
         "voicebank/N.wav",
         "voicebank/Sa.wav",
         "voicebank/Shi.wav",
         "voicebank/So.wav",
         "voicebank/Se.wav",
         "voicebank/Su.wav",
         "voicebank/N.wav",
         "voicebank/Ta.wav",
         "voicebank/Ti.wav",
         "voicebank/To.wav",
         "voicebank/Te.wav",
         "voicebank/Tu.wav",
         "voicebank/N.wav",
         "voicebank/Na.wav",
         "voicebank/Ni.wav",
         "voicebank/No.wav",
         "voicebank/Ne.wav",
         "voicebank/Nu.wav",
         "voicebank/N.wav",
         "voicebank/Ha.wav",
         "voicebank/Hi.wav",
         "voicebank/Ho.wav",
         "voicebank/He.wav",
         "voicebank/Fu.wav",
         "voicebank/N.wav",
         "voicebank/Ma.wav",
         "voicebank/Mi.wav",
         "voicebank/Mo.wav",
         "voicebank/Me.wav",
         "voicebank/Mu.wav",
         "voicebank/N.wav",
         "voicebank/Ya.wav",
         "voicebank/I.wav",
         "voicebank/Yo.wav",
         "voicebank/E.wav",
         "voicebank/Yu.wav",
         "voicebank/N.wav",
         "voicebank/Ra.wav",
         "voicebank/Ri.wav",
         "voicebank/Ro.wav",
         "voicebank/Re.wav",
         "voicebank/Ru.wav",
         "voicebank/N.wav",
         "voicebank/Wa.wav",
         "voicebank/Wi.wav",
         "voicebank/Wo.wav",
         "voicebank/We.wav",
         "voicebank/U.wav",
         "voicebank/N.wav",
         "voicebank/Ga.wav",
         "voicebank/Gi.wav",
         "voicebank/Go.wav",
         "voicebank/Ge.wav",
         "voicebank/Gu.wav",
         "voicebank/N.wav",
         "voicebank/Za.wav",
         "voicebank/Ji.wav",
         "voicebank/Zo.wav",
         "voicebank/Ze.wav",
         "voicebank/Zu.wav",
         "voicebank/N.wav",
         "voicebank/Da.wav",
         "voicebank/Di.wav",
         "voicebank/Do.wav",
         "voicebank/De.wav",
         "voicebank/Du.wav",
         "voicebank/N.wav",
         "voicebank/Ba.wav",
         "voicebank/Bi.wav",
         "voicebank/Bo.wav",
         "voicebank/Be.wav",
         "voicebank/Bu.wav",
         "voicebank/N.wav",
         "voicebank/Pa.wav",
         "voicebank/Pi.wav",
         "voicebank/Po.wav",
         "voicebank/Pe.wav",
         "voicebank/Pu.wav",
         "voicebank/N.wav"]

#m_in = len(files)
m_in = 0

out = open('output.csv','wb')
writer = csv.writer(out, delimiter=',')

for fin in files:

  #if (not m_in == 5) and ((m_in % 6) == 5) :
  #  continue

  try:
    Fs, sample = wav.read(fin)
  except:
    #  print "Usage: %s [wav file] " % sys.argv[0]
    print "Error opening %s " % fin
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

  #ax1 = subplot(311)
  #plot(t[:len(sample)], sample)

  #ax2 = subplot(312, sharex=ax1)
  #ax2 = subplot(312)
  Pxx, freqs, bins, im = specgram(sample, NFFT=NFFT, Fs=Fs, noverlap=900,
                                  cmap=cm.jet)
  #ax2.set_ylim([0, 6000])

  ss = abs(Pxx[2:NFFT*6000/Fs])
  #ss = ss / amax(ss[:,int(len(bins)*0.4):int(len(bins)*0.6)])
  ss = ss / amax(ss)
  sl = 10 * np.log10(ss)

  #ax3 = subplot(313, sharex=ax1)

  nbin = 8 * int(len(ss[:,])/8.)
  sr = ss
  sr = np.mean(sr[:nbin,].reshape(-1,8,len(bins)), 1)
  fq = np.mean(freqs[2:nbin+2].reshape(-1,8),1)

  #ax3.pcolormesh(bins, freqs[2:NFFT*6000/Fs], 10 * np.log10(sr), cmap=cm.jet)
  #ax3.pcolormesh(bins, fq, 10 * np.log(sr), cmap=cm.jet)
#ax3.set_ylim([0, 6000])
#ax3.pcolormesh(bins, freqs, 10 * np.log10(Pxx), cmap=cm.jet)
#ax3.pcolormesh(bins, freqs, 1000 * np.log10(Pxx), cmap=cm.jet)

  idx_cur = 0

  # skip slicence before
  while ss[7,idx_cur] < 0.0001 and idx_cur < len(bins)-1:
    #print idx_cur, sr[:,idx_cur]
    idx_cur = idx_cur + 1

  idx_start = idx_cur

  idx_cur = len(bins) - 1

  # skip slicence after
  while ss[7,idx_cur] < 0.0001 and idx_cur > 0:
    #print idx_cur, ss[7,idx_cur]
    idx_cur = idx_cur - 1

  idx_end = idx_cur

  if idx_start > idx_end :
    print "Parsing silence error..."
    exit(-1)

  i_start = idx_start + int(0.5 * (idx_end-idx_start))
  i_end = idx_start + int(0.9 * (idx_end-idx_start))

  row = []

  for idx in range(100, idx_start-100, 2) :
    for ifq in range(0, len(fq)) :
      row.append(10*log(sr[ifq, idx]/max(sr[:,idx])))
#      row.append(sl[fq, idx]/amax(sl[:,idx]))

    row.append(-1)     # the class id

    writer.writerow(row)
    row = []
  
  for idx in range(i_start, i_end) :
    for ifq in range(0, len(fq)) :
      row.append(10*log(sr[ifq, idx]/max(sr[:,idx])))
#      row.append(sl[fq, idx]/amax(sl[:,idx]))

    row.append(m_in % 6)     # the class id

    writer.writerow(row)
    row = []

#  for idx in range(idx_end+10, len(bins)-10) :
#    for ifq in range(0, len(fq)) :
#      row.append(sr[ifq, idx])
##      row.append(sl[fq, idx]/amax(sl[:,idx]))
#
#    row.append(-1)     # the class id
#
#    writer.writerow(row)
#    row = []
  m_in = m_in + 1

#  savefig(fin+".jpg")
#  clf()

  #show()
