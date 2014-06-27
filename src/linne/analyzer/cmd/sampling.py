"""
Take the sampling data from input audio and save the result in 
csv format
"""

from pymir import AudioFile
from pymir import Pitch
import math
import numpy
import csv
import sys
import os

from linne.analyzer.utils import slidingWindow,frange

def writeCsv(sampling,frames,output):

    csvfile = open(output, 'wb');

    writer = csv.writer(csvfile, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_MINIMAL);

    writer.writerow(["Timestamp",
                       "ZCR",
                       "Spectrum Variance",
                       "RMS",
                       "STE",
                       "Pitch",
                       "ZCR diff.",
                       "Spec. Var. diff.",
                       "RMS diff.",
                       "STE diff."]);

    prev_zcr = 0.;
    prev_var = 0.;
    prev_rms = 0.;
    prev_ste = 0.;
    prev_ps  = 0.;

    curr_zcr = 0.;
    curr_var = 0.;
    curr_rms = 0.;
    curr_ste = 0.;
    curr_ps = 0.;

    for i  in xrange(0,len(frames)):
        windowSize = len(frames[i]) - 1
        timestamp = "%0.3f" % (sampling[i] / float(freq))
        chord, score = Pitch.getChord(frames[i].spectrum().chroma())

        curr_zcr = frames[i].zcr();
        curr_var = frames[i].spectrum().variance();
        curr_rms = frames[i].rms();
        curr_ste = frames[i].energy(windowSize)[0];
        curr_ps  = score;

#        maxFreqIdx = numpy.argmax(frames[i].spectrum());
#        maxFreq = maxFreqIdx * (frames[i].spectrum().sampleRate / 2.0) / \
#                    len(frames[i].spectrum());
#
#        if maxFreq > 750 : curr_ps = 0;
#        if maxFreq < 350 : curr_ps = 0;
        if curr_var < 0.3 : curr_zcr = 0; curr_ps = 0;

        diff_zcr = curr_zcr - prev_zcr;
        diff_var = curr_var - prev_var;
        diff_rms = curr_rms - prev_rms;
        diff_ste = curr_ste - prev_ste;

        row = [timestamp,
               curr_zcr,
               curr_var,
               curr_rms,
               curr_ste,
               curr_ps,
               diff_zcr,
               diff_var,
               diff_rms,
               diff_ste];
        writer.writerow(row);

        prev_zcr = curr_zcr;
        prev_var = curr_var;
        prev_rms = curr_rms;
        prev_ste = curr_ste;
        prev_ps  = curr_ps;


    print "The result is written on %s" % output

try:
	target = sys.argv[1]
except:
	print "Usage: %s [wav file] " % sys.argv[0]
	exit(0)

#TODO read from configuration file
#frameSize = 882 # 20ms
frameSize = 1323 # 30ms
#frameSize = 2205 # 50ms
freq = 44100

token = os.path.basename(target).split(".")
filename = ".".join(token[0:len(token)-1])

wav = AudioFile.open(target)

# Data set 2 - Using sliding Window

sampling = [s for s in frange(frameSize/4.0,len(wav),frameSize/4.0)]
frames = slidingWindow(wav,sampling,frameSize)
output = '%s-sampling.csv' % filename
writeCsv(sampling,frames,output)




