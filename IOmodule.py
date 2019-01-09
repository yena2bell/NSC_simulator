# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 10:08:00 2019

@author: jwKim
"""

import os, sys, time
import update_function
import measure_calculation

if sys.version_info[0] == 2:
    input = raw_input
    #check!
    

def find_info_in_config(l_lines, s_line):
    for line_config in l_lines:
        if s_line in line_config:
            s_parameter = line_config[line_config.index("=")+1:]
            s_parameter = s_parameter.strip()
            return s_parameter
                
    
def set_config(s_address_NSC_folder):
    with open(os.path.join(s_address_NSC_folder, "config.txt")) as file_config:
        l_s_lines = file_config.readlines()
        
    s_address_folder_mutations = find_info_in_config(l_s_lines, "folder containing models mutation information")
    s_address_folder_model = find_info_in_config(l_s_lines, "folder containing network model")
    s_address_folder_results = find_info_in_config(l_s_lines, "folder that will save the result")
    s_address_file_drug = find_info_in_config(l_s_lines, "file about drug perturbation")
    s_address_file_nodes = find_info_in_config(l_s_lines, "file about node information")
    s_address_file_logics = find_info_in_config(l_s_lines, "file about logic information")
    
    i_num_processes = int(find_info_in_config(l_s_lines,"the number of processes for multiprocessing"))
    i_iteration = int(find_info_in_config(l_s_lines,"the number of iteration(trajectories for each cell lines)"))
    i_length = int(find_info_in_config(l_s_lines,"the time step of each trajectory"))
    i_count_starting = int(find_info_in_config(l_s_lines, "the number of states discarded in result calculation"))
    i_resolution_drug = int(find_info_in_config(l_s_lines,"how many drug perturbation probabilities will be calculated except 0"))
    l_s_targets = find_info_in_config(l_s_lines,"target nodes to observe the results").split()
    
    if s_address_folder_results == '':
        now = time.localtime()
        s_address_folder_results = "{0}_{1:0>2d}_{2:0>2d}_{3:0>2d}h{4:0>2d}m{5:0>2d}s".format(now.tm_year,now.tm_mon,now.tm_mday,now.tm_hour,now.tm_min,now.tm_sec)
    

    
    print("the number of processes to use is ", i_num_processes)
    print("path of folder having model mutation is ",s_address_folder_mutations)
    print("drug target information is recorded in ",s_address_file_drug)
    print("nodes are recored in ", s_address_file_nodes," file in the ", s_address_folder_model, " folder")
    print("logic information is in ",s_address_file_logics, " file in the ", s_address_folder_model, " folder")
    print(i_iteration," times of trajectories will be calculated")
    print("each trajectories will have length of ", i_length)
    print("for ",i_length, "state transitions, only ", i_length-i_count_starting, " states near end will be used for calculation of results")
    print("models will be simulated for perturbation probabilities of ",[i/i_resolution_drug for i in range(i_resolution_drug+1)] )
    print("results will be saved in ",s_address_folder_results)
    if not l_s_targets:
        print("all nodes will be observed for the result")
        l_s_targets = (update_function.node_list).split()
    else:
        print(l_s_targets, " nodes will be obserbed for the results")
    
    
    
    s_address_folder_mutations= os.path.join(s_address_NSC_folder,s_address_folder_mutations)
    s_address_folder_model= os.path.join(s_address_NSC_folder,s_address_folder_model)
    s_address_folder_results=os.path.join(s_address_NSC_folder,s_address_folder_results)
    s_address_file_drug = os.path.join(s_address_NSC_folder,s_address_file_drug)
    s_address_file_nodes= os.path.join(s_address_folder_model,s_address_file_nodes)
    s_address_file_logics=os.path.join(s_address_folder_model,s_address_file_logics)
    
    l_parameters = [s_address_folder_mutations,
                    s_address_folder_model,
                    s_address_folder_results,
                    s_address_file_drug,
                    s_address_file_nodes,
                    s_address_file_logics,
                    i_num_processes,
                    i_iteration,
                    i_length,
                    i_count_starting,
                    i_resolution_drug,
                    l_s_targets]
    
    return l_parameters

def get_list_mutation_files(s_address_folder_models):
    l_list_mutation_files = []
    return l_list_mutation_files

#output functions
def make_forder_for_output(s_address_result):
    """make folder for output text files. 
    new folder is maden in s_path. if not assined, basic folder address if current working directory.
    new folder name is (year)_(month)_(day)_(hour)h(minint)m(second)s
    example is 2018_09_08_09h05m12s"""
    os.mkdir(s_address_result)

def save_output_as_txtfile(obj_iterator, s_address_folder_output):
    s_name_output = "output_of_"+obj_iterator.output_model_name()+".txt"
    with open(os.path.join(s_address_folder_output, s_name_output), 'w') as file_output:
        file_output.write("mutation states of this model are\n")
        file_output.write(obj_iterator.output_model_mutation()+'\n')
        file_output.write("input nodes of this models are\n")
        file_output.write(obj_iterator.output_inputnodes()+'\n')
        file_output.write("treated drugs are\n")
        file_output.write(obj_iterator.output_drug_infor()+'\n')
        file_output.write("for each drug concentration, {0} trajectories are calculated,the length of trajectory is {1}, only {2} states are concerned from behind\n".format(obj_iterator.output_num_of_iteration(),obj_iterator.output_length_of_trajectory(),
                                     obj_iterator.output_length_of_trajectory()-obj_iterator.output_num_of_discarded()))
        dic_drug_prob_target_activation_rate = obj_iterator.output_target_activation_rate()
        l_order_keys = list(dic_drug_prob_target_activation_rate.keys())
        l_order_keys.sort()#l_order_keys = [(('MEK', (0, 0.0)),('Raf',(1,0.0))), (('MEK', (0, 0.1)),('Raf',(1,0.1))),,,,(('MEK', (0, 1.0)),('Raf',(1,1.0)))]
        l_drugs = [t_drug_prob[0] for t_drug_prob in l_order_keys[0]]#l_drugs = ['MEK','Ras']
        for s_drug in l_drugs:
            file_output.write(s_drug+'\t')
            for t_t_drug_prob in l_order_keys:
                for t_drug_prob in t_t_drug_prob:
                    if t_drug_prob[0] == s_drug:
                        file_output.write(str(t_drug_prob[1][1])+'\t')
                        break
            file_output.write('\n')
        l_targets = list(list(dic_drug_prob_target_activation_rate.values())[0].keys())
        for s_target in l_targets:
            file_output.write(s_target+'\t')
            for l_key in l_order_keys:
                file_output.write(str(dic_drug_prob_target_activation_rate[l_key][s_target])+'\t')
            file_output.write('\n')
        
        file_output.write('\n')
        l_f_CASP3 = [dic_drug_prob_target_activation_rate[l_key]["CASP3"] for l_key in l_order_keys]
        l_viabilities = [1.0- f_value for f_value in l_f_CASP3]
        dic_measures = measure_calculation.get_drug_response_measure(l_viabilities)
        
        for s_measure in dic_measures.keys():
            file_output.write(s_measure)
            file_output.write(": "+str(dic_measures[s_measure]))
            file_output.write("\n")

#not used
def read_nodes_data(s_address_nodes):
    l_s_nodes = []
    l_s_inputs = []
    with open(s_address_nodes) as file_nodes:
        file_nodes.readline()#first line is "Node list\n" so delete it
        for s_line in file_nodes:
            l_line = s_line.split()
            if not l_line:#l-line == []
                continue
            if len(l_line) == 2 and l_line[1] == "input_node":
                l_s_inputs.append(l_line[0])
            l_s_nodes.append(l_line[0])
        
    return l_s_nodes, l_s_inputs


def read_logic_data(s_address_logic):
    l_s_lines = []
    with open(s_address_logic, 'rt', encoding="UTF8") as file_logic:
        file_logic.readline()#first line is "logic list\n" so delete it
        for s_line in file_logic:
            if '#' in s_line:
                s_line = s_line[:s_line.index('#')+1]
            if s_line.isspace():
                continue
            if ';' in s_line:
                s_line = s_line[:s_line.index(';')]
                s_line = s_line.strip()
                l_s_lines.append(s_line)
    return l_s_lines
                         
            
            
    
"""
NSC = os.path.dirname(os.path.realpath(__file__))
l_parameter = set_config(NSC)
x,y = read_nodes_data(l_parameter[4])
print(y)
z = read_logic_data(l_parameter[5])

"""