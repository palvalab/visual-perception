# -*- coding: utf-8 -*-
"""This script is used to import the MEG data from labVIEW to python.

Created on Fri Dec 23 14:26:06 2016

@author: hhaque
"""

from nptdms import TdmsFile
import numpy as np
from collections import deque
import os 


os.chdir('directory where arrays would be stored')

#fucntion to find the LabVIEW tdms files to import python
def list_files(dir, exact_file): 
    for root, dirs, files in os.walk(dir):
        for name in files:
            if name == exact_file:
                return os.path.join(root, name)

#Put down the conditions in a list 
conditions = [['DET_HIT', '6_DET'], ['DET_MISS', '6_DET'], ['DISC_HIT', '6_DISC'], ['DISC_MISS', '6_DISC']] # format: [condition, code]

#In later scripts, these values are taken directly from the condition array but since
#they haven't been created yet, they have to be manually put down. 
nbSubjects = 14
nbParcels = 400 
nbTimeSamples = 841

#We loop through each of the conditions, and extract the values to put into the numpy array
for condition in conditions:

    exact_file = 'VertexDM-BB_Evoked-Induced-TFR 1-1 Real+iAmplitude %s postStim_BB_%s 45-00Hz.tdms' % (condition[0], condition[1])
    
    a = deque() #a container datatype that I like to use when creating arrays from scratch 
    
    for i in range(nbSubjects): #looping through each subject
        subjectNo = str(i+1).zfill(2)
        dir = 'V:\\S%s\\BBGraphData_postStim' % subjectNo #navigate to subject-specific folder
        filepath = list_files(dir, exact_file)
        tdms_file = TdmsFile(filepath) #opens the data from the tdms file
    
        data = deque() #another deque, this time for storing subject-specific data
        for parcel in range(nbParcels): #looping through each parcel
            real_values = [] #empty list that will contain the real values of a parcel
            for sample in range(nbTimeSamples): #going through each time sample
            
                #the real value for that time point is appended to the list
                real_values.append(tdms_file.channel_data(str(sample), 'Vertex Data (CSGreim)__real')[parcel])
            data.append(real_values) #the real values for the parcel are appended to the deque object
        a.append(data) #the real values for the subject are appended
        #side note: its important that the the order in which the values are appended to the deque object
        #is correct as that will determine the dimensions of the numpy array that's created. In this
        #case we first appended from each time point, then each parcel, then each subject.
    
    a = np.array(a, dtype = float) #we convert it to a numpy array. dtype is float(64) for greater precision
    final = condition[0] + '_collapsed' #should match directory
    np.save(final, a) #the array is saved in the current working directory