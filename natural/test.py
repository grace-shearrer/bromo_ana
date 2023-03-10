#!/home/gshearre/miniconda3/bin/python

import os
import glob
import numpy as np
import pandas as pd
from nltools.stats import isc, isfc, isps, fdr, threshold, phase_randomize, circle_shift, _butter_bandpass_filter, _phase_mean_angle, _phase_vector_length
from sklearn.metrics import pairwise_distances
from sklearn.utils import check_random_state
import argparse
import pickle
from datetime import datetime
from time import time

# inpu is the input it should be a dataframe with the column as subjects and rows as time


def adillyofapickle(basepath,dic, name):
    datefmt='%m-%d-%Y_%I-%M-%S'
    st = datetime.fromtimestamp(time()).strftime(datefmt)
    if os.path.exists(os.path.join(basepath,'tmp')):
        print('already have tmp')
    else:
        os.makedirs(os.path.join(basepath,'tmp'))
    pickle.dump(dic, open(os.path.join(basepath,'tmp','%s_%s.pkl'%(name,st)), 'wb'), protocol=4)


def onetoughjar(p):
    list_of_files = glob.glob(p) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getmtime)
    with open(latest_file, 'rb') as pickle_file:
        try:
            while True:
                output = pickle.load(pickle_file)
        except EOFError:
            pass
    return(output)


def get_subject_roi(data_dict, roi_num):
    sub_rois = {}
    for sub, value in data_dict.items():
        sub_rois[sub] = value[ROIS.iloc[roi_num]]
    return (pd.DataFrame(sub_rois))
 
def fcisc(inpu,outpu):
	try:
		stats = isc(inpu, n_bootstraps=500, metric='median', method='bootstrap')
	except ValueError:
		test = inpu.dropna(axis=1)
		print(test)
		stats = isc(test, n_bootstraps=500, metric='median', method='bootstrap')


	return(stats)


if __name__ == '__main__':
	outpath = '/projects/niblab/data/BRO/timeseries'
	atlaspath = '/projects/niblab/parcellations/Harvard_Oxford'
	ROIS = pd.read_csv(os.path.join(atlaspath,'tmp','ROIS.csv'))
	ROIS = ROIS['0']

	cortical_dict = onetoughjar(os.path.join(atlaspath,'tmp','cortical*'))
	subcortical_dict = onetoughjar(os.path.join(atlaspath,'tmp','subcortical*'))
	data_dict = onetoughjar(os.path.join(outpath,'tmp','timeseries_parc*'))


# Create the parser
	pars = argparse.ArgumentParser()
# Add an argument
	pars.add_argument('--condition', type=str, required=True)
	pars.add_argument('--ROI', type=int, required=True)
# Parse
	parser = pars.parse_args()
	print(parser)
# get data
	df = pd.concat([get_subject_roi(data_dict[parser.condition]['run-1'], parser.ROI), get_subject_roi(data_dict[parser.condition]['run-2'], parser.ROI)]) 
# make dicts and run code
	stats = fcisc(df, os.path.join(outpath,'isc_ROI-%s_%s'%(parser.ROI, parser.condition)))
# save pickle
	packit = {'%s'%parser.condition:{'%s_ROI'%parser.ROI:{'stats':stats, 'df':df}}}
	adillyofapickle(outpath,packit, '%s_%s'%(parser.condition,parser.ROI))



