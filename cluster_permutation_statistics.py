# -*- coding: utf-8 -*-
"""Uses the 'permutation_cluster_1samp_test' function from the mne package
compute the cluster-based permutation statistics for each contrast.

Created on Mon Nov 14 10:34:21 2016

@author: hhaque
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from mne.stats import permutation_cluster_1samp_test

## Each key in the dictionary is a specific contrast. The value in the dict is 
## has a list that contains the numpy files used (created in previous steps) to 
## compute the contrast
Contrasts_AllInfo = {'Det_Hit-Miss_collapsed_w5': [['DET_HIT_collapsed_w5_BLcorrected_morphed.npy', 'DET_MISS_collapsed_w5_BLcorrected_morphed.npy'],[2]], 
                    'Det_Hit_collapsed_w5': [['DET_HIT_collapsed_w5_BLcorrected_morphed.npy'],[2]],
                    'Det_Miss_collapsed_w5': [['DET_MISS_collapsed_w5_BLcorrected_morphed.npy'],[2]],
                    'Disc_Hit-Miss_collapsed_w5': [['DISC_HIT_collapsed_w5_BLcorrected_morphed.npy', 'DISC_MISS_collapsed_w5_BLcorrected_morphed.npy'],[2]], 
                    'Disc_Hit_collapsed_w5': [['DISC_HIT_collapsed_w5_BLcorrected_morphed.npy'],[2]],
                    'Disc_Miss_collapsed_w5': [['DISC_MISS_collapsed_w5_BLcorrected_morphed.npy'],[2]],
                    }
n_permutations=1000
nb_samples_average = 5

# Take into account effect of moving average on t0
dt=0.00332992021930646
t0 = -0.8 + ((nb_samples_average - 1) / 2) * dt  
tLimit=int(1.8/0.00332992021930646)

#This is done for each contrast
for contrast in Contrasts_AllInfo.keys():
    
    os.chdir('data where arrays are stored') #change dir to location where data is
    plt.close('all') #closing any open figures   
    
    Condition_arrays = Contrasts_AllInfo.get(contrast)[0]
    SubjectsToExclude = Contrasts_AllInfo.get(contrast)[1] #indices of subjects to exclude. S03 is excluded due to problems in the neural data
    
    #Contrasts treated differently if one or two arrays are involved
    if len(Condition_arrays) == 2:
        a = np.load(Condition_arrays[0])
        b = np.load(Condition_arrays[1])
        data = a - b
    elif len(Condition_arrays) == 1:
        data = np.load(Condition_arrays[0]) 
    else:
        raise ValueError('Condition arrays has more than two conditions')

    data=np.delete(data, SubjectsToExclude, 0) #removing S03 from data

    data=data[:,:,0:tLimit] #restricting analysis to 1.8 s after stimulus
    
    nbSubjects = data.shape[0]
    nbParcels=data.shape[1]
    nbTimeSamples=data.shape[2]
    times = [t0 + x*dt for x in range(nbTimeSamples)]
    
    folda = 'path where cluster permutation results would be stored' + contrast
    if not os.path.exists(folda):
        os.makedirs(folda)
        
    os.chdir(folda)
    
    ## creating empty arrays and lists where the output from the cluster permutation stats would be stored
    T_ObsAllParcels=np.empty([nbParcels, nbTimeSamples])
    clustersAllParcels=[]
    cluster_pvParcels=[]
    H0_allParcels = np.empty([nbParcels, n_permutations])

    for parcel in range(nbParcels):
        
        T_obs, clusters, cluster_pv, H0 = permutation_cluster_1samp_test(data[:,parcel,:], threshold=None,
                                                n_permutations=n_permutations, seed=542,
                                                tail=0, connectivity=None, verbose=None, n_jobs=1, buffer_size=None)
        
        H0_allParcels[parcel,:]=H0 #max cluster level stats observed for permutation
        T_ObsAllParcels[parcel,:]=T_obs #t-statistic observed for each sample
        clustersAllParcels.append(clusters) #start and stop sample of each cluster
        cluster_pvParcels.append(cluster_pv) # p-value of each cluster
    
    
    nama = ['T_ObsAllParcels', 'clustersAllParcels', 'cluster_pvParcels', 'H0_allParcels']
    for n in nama:
        np.save(n, eval(n))  
    
    isSignificantTimepoint=np.zeros_like(T_ObsAllParcels) # has shape (parcel x samples)
    
    ## if a time sample in a parcel belongs to a significant cluster, its value in
    ## 'isSignificantTimepoint' is changed from 0 to 1.
    for iParcel in range(len(clustersAllParcels)):
        for iCluster in range(len(clustersAllParcels[iParcel])):
            if cluster_pvParcels[iParcel][iCluster]<0.01:
                for iTimePoint in range(clustersAllParcels[iParcel][iCluster][0].start, clustersAllParcels[iParcel][iCluster][0].stop):
                    isSignificantTimepoint[iParcel][iTimePoint]=1

    # Save thresholded t-values (only sig at the cluster level) for further visualizations
    np.save('thresholded_TObs_all_parcels.npy',isSignificantTimepoint*T_ObsAllParcels)  
    
    # Plot heatmap of significant clusters
    plt.close('all')
    plt.figure()        
    plt.pcolor(isSignificantTimepoint)
    plt.xlabel('Time samples')
    plt.ylabel('Parcel')
    plt.title(contrast)
    plt.savefig('Heatmap')
            
    fractionSignificant = np.mean(isSignificantTimepoint, axis=0)
    
    
    T_ObsAllParcelsLeft = T_ObsAllParcels[::2]   
    T_ObsAllParcelsRight = T_ObsAllParcels[1::2]  
         
    # Plot significant fraction of parcels at each time-point
    plt.close('all')
    plt.figure()
    plt.plot(times, fractionSignificant)
    plt.grid(True)    
    plt.xlabel('Time (s)')
    plt.ylabel('Fraction of significant')
    a_title = contrast + ' - Fraction of signitificant'
    plt.title(a_title, y = 1.04)
    plt.savefig('Fraction of signitificant using clustering at the parcel level.png')
    


    summary = 'The condition was %s and the file(s) used were %s \
    The index of subjects removed (if any) were %s' % (contrast, (' '.join(Condition_arrays)), (' '.join(str(e) for e in SubjectsToExclude)))
    
    log_file = open('summary.txt', 'w')
    log_file.write(summary)
    log_file.close()