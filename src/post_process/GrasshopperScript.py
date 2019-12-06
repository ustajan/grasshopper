# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 19:12:32 2018

@author: Ezra
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab



############################################################
####################    Inputs   ###########################
############################################################

filename = "test.dat"
bin_num = 50

############################################################


energy = np.loadtxt(filename, usecols=0, skiprows=1)    #read in energy
particle = np.loadtxt(filename, dtype=str, usecols=2, skiprows=1)   #read in particle type
energy_alpha = energy[particle=='alpha']    #logically index energy array by particle type to take only alphas

u = np.mean(energy_alpha)   #get mean
s = np.std(energy_alpha)    #get standard deviation
print(u,s)

plt.hist(energy_alpha,bins=bin_num,edgecolor='k')   #histogram the data


x = np.linspace(2.8,3.15,100)
amp_correction = np.max(np.histogram(energy_alpha,bins=bin_num)[0])*np.sqrt(2*np.pi*s**2) #plot a normal curve of data
plt.plot(x,amp_correction*mlab.normpdf(x,u,s))



plt.xlabel('Energy (MeV)')
plt.ylabel('Counts')
plt.title('Alpha Histogram')
plt.show()