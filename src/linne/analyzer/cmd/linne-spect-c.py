#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Making Spectogram of an audio

import math
import numpy
import csv
import sys
import os
import scipy.io.wavfile as wav

from pylab import *

# ㄚ ㄛ ㄜ ㄝ ㄧ ㄨ ㄩ
# a  o 2  e i u v
 
# ㄞ ㄟ ㄠ ㄡ
# ai ei ao ou
# ㄢ ㄣ ㄤ ㄥ
# an en ang eng

files = ["a-a-ai-a-an.wav",
         "o-e-sen.wav",
         "e-chi.wav",
         "E.wav",
         "yi-ha.wav",
         "wu-ang.wav",
         "yu-ba.wav",
         "an-ai-ao-a-fa.wav",
#
         "ba-bei-bei-bi-bia.wav",
         "bo-chou.wav",
         "er-ang.wav",
         "Be.wav",
         "bi-bang-chun.wav",
         "bu-bie-ba-bang-a.wav",
         "lv-a-kuang-gong-ka.wav",
         "en-tou-bia-ben-ting.wav",
#
         "ta-che-mi-lao-pen.wav",
         "fo-chuan.wav",
         "e-hang.wav",
         "Te.wav",
         "ti-bai-ta.wav",
         "tu-niao-ma-nen-cou.wav",
         "nv-an-mie-fou-guai.wav",
         "ang-zi-fei-pan-tai.wav",
#
         "ha-jin-zhi-yi-lun.wav",
         "hou-xi.wav",
         "er-ju.wav",
         "He.wav",
         "ni-bo-bie-mie-mian.wav",
         "hu-nang-diu-nao-mo.wav",
         "lv-bai-shuo-song.wav",
         "heng-zuan-quan-qin-qing.wav",
#
         "la-ceng-han-zhua-cou.wav",
         "zhou-pang-qun-xiang-que.wav",
         "ne-chuai.wav",
         "Ge.wav",
         "qi-ban.wav",
         "cu-heng.wav",
         "nv-bei-shun.wav",
         "N.wav",
#
         "pa-chui-qian.wav",
         "po-che-da.wav",
         "pe-chuang.wav",
         "Pe.wav",
         "pi-bao-suo-bian.wav",
         "pu-cheng.wav",
         "lv-da.wav",
         "rong-duo-mian-ha-beng.wav"]
#
 
#m_in = len(files)
m_in = 0

out = open('output_zh.csv','wb')
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
  while ss[7,idx_cur] < 0.0001 and idx_cur < len(bins)-1:
    #print idx_cur, sr[:,idx_cur]
    idx_cur = idx_cur + 1

  idx_start = idx_cur

  #idx_cur = len(bins) - 1

  # skip slicence after, at most ~0.7 sec
  #while ss[7,idx_cur] < 0.0001 and idx_cur > 0:
  idx_cur += 50
  while ss[6,idx_cur] > 0.0001 and (idx_cur - idx_start) < 350:
    #print idx_cur, ss[6,idx_cur]
    idx_cur = idx_cur + 1

  # skip slicence from tail
  #while ss[6,idx_cur] < 0.0001 and idx_cur > 0:
  #  #print idx_cur, ss[7,idx_cur]
  #  idx_cur = idx_cur - 1

  print fin, len(bins), idx_start, idx_cur-idx_start
  idx_end = idx_cur

  if idx_start > idx_end :
    print "Parsing silence error..."
    exit(-1)

  i_start = idx_start + int(0.5 * (idx_end-idx_start))
  i_end = idx_start + int(0.9 * (idx_end-idx_start))

  # Nasal consonant
  if (m_in % 8) == 7:
    i_start = idx_start + int(0.75 * (idx_end-idx_start))
    i_end = idx_start + int(0.95 * (idx_end-idx_start))

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

    row.append(m_in % 8)     # the class id

    writer.writerow(row)
    row = []

  m_in = m_in + 1

  #show()
