# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 15:35:09 2019

@author: jwKim
"""
import numpy

def get_drug_response_measure(l_viabilities):
    l_viablities_adjusted = adjust_viabilities(l_viabilities)
    f_IC50 = get_IC50(l_viablities_adjusted)
    f_EC50 = get_EC50(l_viablities_adjusted)
    f_AUC = get_AUC(l_viablities_adjusted)
    f_efficacy = get_efficacy(l_viablities_adjusted)
    
    dic_measures = {"IC50": f_IC50, "EC50": f_EC50, "AUC": f_AUC, "efficacy": f_efficacy}
    return dic_measures

def adjust_viabilities(l_viabilities):
    f_factor = 1.0/l_viabilities[0]
    l_viabilities_adjusted = [f_value*f_factor for f_value in l_viabilities]
    return l_viabilities_adjusted

def get_IC50(l_viabilities):#assume monotonic decrease of l_vialbilities
    f_threshold = 0.5
    
    if l_viabilities[-1] >= f_threshold:
        return 1
    
    i_num_points = len(l_viabilities)#contains drug concentration 0
    f_interval_drug_concen = 1.0/(i_num_points-1)
    for i in range(i_num_points-1):
        if l_viabilities[i] >= f_threshold and l_viabilities[i+1] < f_threshold:
            return ((l_viabilities[i]-f_threshold)/(l_viabilities[i]-l_viabilities[i+1])+i)*f_interval_drug_concen#linear approximation
        if l_viabilities[i] == l_viabilities[i+1] and l_viabilities[i] == f_threshold:
            return (i+0.5)*f_interval_drug_concen


def get_EC50(l_viabilities):
    """assume l_viabilities are monotonic pattern."""
    f_threshold = (1 - l_viabilities[-1])/2.0 + l_viabilities[-1]
    
    i_num_points = len(l_viabilities)#contains drug concentration 0
    f_interval_drug_concen = 1.0/(i_num_points-1)
    
    if l_viabilities[-1] >= f_threshold:
        return 1
    
    for i in range(i_num_points,0,-1):
        if l_viabilities[i-1] >= f_threshold and l_viabilities[i] < f_threshold:
            return ((l_viabilities[i-1]-f_threshold)/(l_viabilities[i-1]-l_viabilities[i])+i-1)*f_interval_drug_concen#linear approximation
        if l_viabilities[i-1] == l_viabilities[i] and l_viabilities[i] == f_threshold:
            return (i-0.5)*f_interval_drug_concen
    
    return 1

def get_AUC(l_concentrations):#average
    return numpy.mean(numpy.array(l_concentrations))
    

def get_efficacy(l_viabilities):
    return 1.0 - l_viabilities[-1]