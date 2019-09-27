# -*- coding: utf-8 -*-
"""This script morphs the baseline-corrected data from 400 to 200 parcels. 
This requires a morphing operator for each subject.

Created on Fri Jun 08 11:33:29 2018

@author: hamed
"""

import os
import numpy as np
import pandas as pd
from collections import deque

os.chdir('directory where arrays are stored') ## should be the same as in 'import_data_to_python.py' and 'baseline_correction_of_data.py'

condition_arrays = ['DET_HIT_collapsed','DET_MISS_collapsed','DISC_HIT_collapsed','DISC_MISS_collapsed']
            
for condition in condition_arrays:
    array_source = condition + '_w5_BLcorrected.npy'
    array_destination = condition + '_w5_BLcorrected_morphed'    
    a = np.load(array_source)

    nbSubjects = a.shape[0]
    nbParcels=a.shape[1]
    nbTimeSamples=a.shape[2]
    
    everything = deque() #file that would have all the morphed data
    
    for i in range(nbSubjects):
        subjectNo = str(i+1).zfill(2)
        
        #morphing operator specific to each subject due to differences in anatomy
        fname = 'path to morphing operator\\Morphing_operator_400to200_S' + subjectNo + '.xlsx'
        df = pd.read_excel(fname, header = None)
        operator = df.as_matrix()
    
        storage = deque()
        for tp in range(nbTimeSamples): 
            morphed = np.dot(a[i, :, tp], operator)
            storage.append(morphed)
        storage = np.array(storage)
        storage = np.transpose(storage)
        everything.append(storage)
    
    everything = np.array(everything, dtype = float)
    np.save(array_destination, everything)