#!/usr/bin/env python
# Making Spectogram of an audio

import math
import numpy
import csv
import sys
import os
import scipy.io.wavfile as wav

from pylab import *

files = ["wav/A.wav",
         "wav/I.wav",
         "wav/O.wav",
         "wav/E.wav",
         "wav/U.wav",
         "wav/N.wav",
         "wav/Ka.wav",
         "wav/Ki.wav",
         "wav/Ko.wav",
         "wav/Ke.wav",
         "wav/Ku.wav",
         "wav/N.wav",
         "wav/Sa.wav",
         "wav/Shi.wav",
         "wav/So.wav",
         "wav/Se.wav",
         "wav/Su.wav",
         "wav/N.wav",
         "wav/Ta.wav",
         "wav/Ti.wav",
         "wav/To.wav",
         "wav/Te.wav",
         "wav/Tu.wav",
         "wav/N.wav",
         "wav/Na.wav",
         "wav/Ni.wav",
         "wav/No.wav",
         "wav/Ne.wav",
         "wav/Nu.wav",
         "wav/N.wav",
         "wav/Ha.wav",
         "wav/Hi.wav",
         "wav/Ho.wav",
         "wav/He.wav",
         "wav/Fu.wav",
         "wav/N.wav",
         "wav/Ma.wav",
         "wav/Mi.wav",
         "wav/Mo.wav",
         "wav/Me.wav",
         "wav/Mu.wav",
         "wav/N.wav",
         "wav/Ya.wav",
         "wav/I.wav",
         "wav/Yo.wav",
         "wav/E.wav",
         "wav/Yu.wav",
         "wav/N.wav",
         "wav/Ra.wav",
         "wav/Ri.wav",
         "wav/Ro.wav",
         "wav/Re.wav",
         "wav/Ru.wav",
         "wav/N.wav",
         "wav/Wa.wav",
         "wav/Wi.wav",
         "wav/Wo.wav",
         "wav/We.wav",
         "wav/U.wav",
         "wav/N.wav",
         "wav/Ga.wav",
         "wav/Gi.wav",
         "wav/Go.wav",
         "wav/Ge.wav",
         "wav/Gu.wav",
         "wav/N.wav",
         "wav/Za.wav",
         "wav/Ji.wav",
         "wav/Zo.wav",
         "wav/Ze.wav",
         "wav/Zu.wav",
         "wav/N.wav",
         "wav/Da.wav",
         "wav/Di.wav",
         "wav/Do.wav",
         "wav/De.wav",
         "wav/Du.wav",
         "wav/N.wav",
         "wav/Ba.wav",
         "wav/Bi.wav",
         "wav/Bo.wav",
         "wav/Be.wav",
         "wav/Bu.wav",
         "wav/N.wav",
         "wav/Pa.wav",
         "wav/Pi.wav",
         "wav/Po.wav",
         "wav/Pe.wav",
         "wav/Pu.wav",
         "wav/N.wav"]

#m_in = len(files)
m_in = 0

out = open('training2.csv','wb')
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

  ss = abs(Pxx[2:NFFT * max_freq / Fs])
  #ss = ss / amax(ss[:,int(len(bins)*0.4):int(len(bins)*0.6)])
  ss = ss / amax(ss)
  sl = 10 * np.log10(ss)

  nbin = 8 * int(len(ss[:,])/8.)
  sr = ss
  sr = np.mean(sr[:nbin,].reshape(-1,8,len(bins)), 1)
  fq = np.mean(freqs[2:nbin+2].reshape(-1,8),1)

  idx_cur = 0

  # skip slicence before
  while ss[7,idx_cur] < 0.001 and idx_cur < len(bins)-1:
    #print idx_cur, sr[:,idx_cur]
    idx_cur = idx_cur + 1

  idx_start = idx_cur

  idx_cur = len(bins) - 1

  # skip slicence after
  while ss[7,idx_cur] < 0.001 and idx_cur > 0:
    #print idx_cur, ss[7,idx_cur]
    idx_cur = idx_cur - 1

  idx_end = idx_cur

  if idx_start > idx_end :
    print "Parsing silence error..."
    exit(-1)

  i_start = idx_start + int(0.45 * (idx_end-idx_start))
  i_end = idx_start + int(0.85 * (idx_end-idx_start))

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
