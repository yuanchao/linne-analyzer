'''
Training an SVM classifier for identifying the vowel position
'''
#print(__doc__)

# Author: Yuan CHAO

#import csv
import numpy as np
#import scipy.io.wavfile as wav

# Standard scientific Python imports
#import pylab as pl

# Import datasets, classifiers and performance metrics
from sklearn import svm, metrics
from sklearn.cross_validation import train_test_split

from sklearn.externals import joblib

#print 'Loading CSV'

data_train = np.loadtxt( 'training2.csv', delimiter=',', skiprows=0 )

print 'Splitting training and testing samples.'

# Reading csv into NumPy arrays
# random_state used for training/validation splitting seed
Z_train, Z_valid, Y_train, Y_valid = train_test_split(
                                       data_train[:,0:-1], data_train[:,-1],
                                       test_size=0.5, random_state=42)

# Create a classifier: a support vector classifier
classifier = svm.SVC(gamma=0.00001, probability=True)

# We learn the digits on the first half of the digits
classifier.fit(Z_train, Y_train)

# Now predict the value of the digit on the second half:
expected = Y_valid
predicted = classifier.predict(Z_valid)

print("Classification report for classifier %s:\n%s\n"
      % (classifier, metrics.classification_report(expected, predicted)))
print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))

joblib.dump(classifier, 'linne2.pkl') 
#joblib.dump(classifier, 'gcin_ogg.pkl') 
