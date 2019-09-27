# -*- coding: utf-8 -*-
"""Once all condition arrays are created via 'import_data_to_python.py',
this script takes the absolute real value and performs baseline subtraction

Created on Fri Jun 08 10:58:16 2018

@author: hamed
"""

import os
import numpy as np

data_dir = 'data where arrays are stored' # should be the same as in 'import_data_to_python.py'

condition_arrays = ['DET_HIT_collapsed.npy','DET_MISS_collapsed.npy', 
                    'DISC_HIT_collapsed.npy','DISC_MISS_collapsed.npy']

t0=-0.8 #time point for first sample (in seconds)
dt=0.00332992021930646 #time period of each sample
nb_samples_average = 5 #window (in samples) of moving average

for condition in condition_arrays:
    data_file_path = data_dir + condition
    processed_file_path = data_dir + os.path.splitext(condition)[0] + '_w5_BLcorrected' #filename of processesed file
            
    data = np.load(data_file_path)
    data = abs(data) #taking the absolute value
 
    # The valid option implies that  the  convolution product is only given for 
    # points where the kernel and the signals overlap completely
    data = np.apply_along_axis(np.convolve, 2, data, np.ones((nb_samples_average,))/nb_samples_average, mode = 'valid')
    
    # Getting these info from the array shape itself; it should match 'import_data_to_python.py'
    nbSubjects = data.shape[0]
    nbParcels=data.shape[1]
    nbTimeSamples=data.shape[2]
 
    # Modify t0 to align with new t0 after moving average with valid option    
    t0 = t0 + ((nb_samples_average - 1) / 2) * dt       
    times = [t0 + x*dt for x in range(nbTimeSamples)]
    
    tStartBaseline=int((-0.5-t0)/dt)
    tStopBaseline=int((-0.1-t0)/dt)
    
    #Compute mean for each subject and parcel for timepoints between tStartBaseline
    #and tStopBaseline
    baselineData=np.mean(data[:,:,tStartBaseline:tStopBaseline], axis=2)
    
    #Transpose data so that timepoints is the first dimension
    transposedData=np.transpose(data, (2, 0, 1))
    
    #baseline correct data
    baselineCorrectedData=transposedData-baselineData
    
    #Transpose data back to initial dimensions
    transposedBaselineCorrectedData=np.transpose(baselineCorrectedData, (1, 2, 0))
    
    #saving the data
    np.save(processed_file_path, transposedBaselineCorrectedData)