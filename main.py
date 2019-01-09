# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 19:43:10 2018

@author: jwkim
"""
from multiprocessing import Pool
import os

from module_simulator import Iterator_of_model_simulator
import update_function
import IOmodule

def calculate_model_with_setted_parameter(t_input):
    s_address_file_model, s_address_file_drug, s_address_file_inputnode, s_address_folder_output, i_iteration, i_length, i_count_starting, i_resolution_drug, l_s_targets= t_input
    obj_iterator = Iterator_of_model_simulator(update_function,#imported module
                                                    s_address_file_model,
                                                    s_address_file_drug,
                                                    s_address_file_inputnode,
                                                    i_iteration,
                                                    i_length,
                                                    i_count_starting,
                                                    l_s_targets,
                                                    i_resolution_drug)
    obj_iterator.calculate_model_for_each_drug_concentrations()
    IOmodule.save_output_as_txtfile(obj_iterator, s_address_folder_output)
    return s_address_file_model



def main():
    """make models by txt files in model list folder, and get drug information from drug_probability.txt
    input the number of iteration(calculation of one trajectory) and the length of trajectory.
    input the resolution of drug concentration change (if 10 is inputed, 0,0.1,0.2,,, 0.9,1 cases are calculated)
    finally, input the node names to observe.
    then this function will make text files of observed node pattern for each model in output folder"""
    
    s_address_NSC = os.path.dirname(os.path.realpath(__file__))
    l_parameters = IOmodule.set_config(s_address_NSC)
    
    IOmodule.make_forder_for_output(l_parameters[2])
    p = Pool(l_parameters[6])
    l_list_mutation_files = [os.path.join(l_parameters[0], s_filename_mutation)
                             for s_filename_mutation in os.listdir(l_parameters[0])]
    
    s_address_file_inputnode = os.path.join(s_address_NSC,"input_nodes.txt")
    l_list_inputs = [(s_address_file_model, l_parameters[3], 
                      s_address_file_inputnode, l_parameters[2], 
                      l_parameters[7], l_parameters[8], l_parameters[9], 
                      l_parameters[10], l_parameters[11])
                     for s_address_file_model in l_list_mutation_files]
    

    #print(s_address_folder_models, s_address_file_drug, i_iteration, type(i_iteration), l_s_targets)



    l_list_for_check = p.map(calculate_model_with_setted_parameter,l_list_inputs)
    if l_list_mutation_files != l_list_for_check:
        for s_mutation_file in l_list_mutation_files:
            if s_mutation_file not in l_list_for_check:
                print(s_mutation_file+ " is not calculated! by multiprocessing error!")
    
    
if __name__ == "__main__":
    main()
