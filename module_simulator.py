# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 15:03:11 2018

@author: jwkim
"""
import numpy as np
import os

class Iterator_of_model_simulator():
    def __init__(self, module_update_function, s_model_address, s_drug_address, s_inputnode_address,
                 i_num_of_iteration, i_length_of_trajectory, i_counting_discard,
                 l_targets_to_observe, i_resolution):
        self.func_update = module_update_function.update_function
        self.s_node_order= module_update_function.node_list
        self.s_model_address = s_model_address
        self.s_drug_address = s_drug_address
        self.s_inputnode_address = s_inputnode_address
        self.dic_drug_type = self.refine_drug_infor()
        self.i_length = i_length_of_trajectory
        self.i_iteration = i_num_of_iteration
        self.i_counting_discard = i_counting_discard
        self.i_resolution = i_resolution #the number of observing point in continuous drug concentratoin change. if 10 -> 0,0.1,0.2,,,1
        self.l_s_targets = l_targets_to_observe
        self.dic_drugconcentration_dic_targets_numTrue = {}

    def refine_drug_infor(self):
        dic_drug_type = {}
        with open(self.s_drug_address, 'r') as file_drug:
            for s_line in file_drug:
                if s_line == '':
                    break # in case of blanked end line
                l_drug_type = s_line.split()
                if l_drug_type[1] in ["OVER","over","Over"]:
                    dic_drug_type[l_drug_type[0]] = 1
                elif l_drug_type[1] in ["KO","Ko","ko"]:
                    dic_drug_type[l_drug_type[0]] = 0
                else:
                    raise ValueError("drug combination file has wrong form")
        return dic_drug_type

    def output_model_name(self):
        s_basename = os.path.basename(self.s_model_address)
        if s_basename[-4:] == ".txt":
            s_basename = s_basename[:-4]
        return s_basename

    def output_model_mutation(self):
        with open(self.s_model_address, 'r') as file_mutation:
            s_file = file_mutation.read()
        return s_file

    def output_drug_infor(self):
        with open(self.s_drug_address, 'r') as file_drug:
            s_file = file_drug.read()
        return s_file
        
    def output_inputnodes(self):
        with open(self.s_inputnode_address, 'r') as file_inputnodes:
            s_file = file_inputnodes.read()
        return s_file

    def output_num_of_iteration(self):
        return self.i_iteration

    def output_length_of_trajectory(self):
        return self.i_length

    def output_num_of_discarded(self):
        return self.i_counting_discard

    def output_target_activation_rate(self):
        return self.dic_drugconcentration_dic_targets_numTrue
        

    def interate_model_for_define_drug_concentration(self, dic_drug_t_type_concentration):
        dic_target_numTrue = {s_target:0 for s_target in self.l_s_targets}
        i_num_counted_state = self.i_iteration*(self.i_length-self.i_counting_discard)

        for i in range(self.i_iteration):
            obj_model = Model_simulator()
            obj_model.input_update_function(self.func_update)
            obj_model.input_node_order(self.s_node_order)
            obj_model.input_length_of_simulation(self.i_length)
            obj_model.input_initial_state()
            obj_model.input_drug_perturbation(**dic_drug_t_type_concentration)
            obj_model.input_mutation(self.s_model_address)
            obj_model.input_input_nodes(self.s_inputnode_address)
            obj_model.simulate_model()
            for s_target in dic_target_numTrue.keys():
                dic_target_numTrue[s_target]+=obj_model.count_True_target(s_target, self.i_counting_discard)


        dic_target_percentTrue = {s_target:float(i_target_numTrue)/i_num_counted_state
                                  for s_target, i_target_numTrue in dic_target_numTrue.items()}
        l_t_drug_prob = list(dic_drug_t_type_concentration.items())
        l_t_drug_prob.sort()
        t_t_drug_prob = tuple(l_t_drug_prob)
        self.dic_drugconcentration_dic_targets_numTrue[t_t_drug_prob] = dic_target_percentTrue

    def calculate_model_for_each_drug_concentrations(self):
        for i in range(self.i_resolution+1):
            f_drug_probability = float(i)/self.i_resolution
            dic_drug_t_type_concentration={s_drug:(i_type,f_drug_probability) for s_drug,i_type in self.dic_drug_type.items()}
            self.interate_model_for_define_drug_concentration(dic_drug_t_type_concentration)
        

class Model_simulator():
    def __init__(self):
        self.func_update = None
        self.dic_node_order = None
        self.array_state_trajectory = None
        self.dic_drug_updown_probability = {}
        self.dic_muation_overorsupp = {}
        self.l_input_nodes = []
        
    def input_update_function(self, func_update):
        """func_update should have array(state) as input, and return array of next state"""
        self.func_update = func_update
        
    def input_node_order(self, s_node_order):
        """s_node_order should be the string which contain node in order.
        s_node_order has the form of 
        AP_1
        APC
        ATF2
        ATM
        AXIN
        Akt
        ...
        the order of these genes has to be same with order in function"""
        l_node_order = s_node_order.split()
        self.dic_node_order = {s_node:i_order for i_order,s_node in enumerate(l_node_order)}
        
    def input_length_of_simulation(self, i_simulation):
        """before this function, input_node_order function should be done.
        i_simulation means how many times state update will be done"""
        self.array_state_trajectory = np.zeros([i_simulation, len(self.dic_node_order)], dtype=int)
        #dtype bool-> a - b == a xor b
        
    def input_initial_state(self, i_or_t_initial_state="random"):
        """before this function, input_node_order function and input_length_of_simulation should be done.
        if i_or_t_initial_state == 'random', initial state are choosen randomely.
        you can choose defined initial state by writing inital state in i_or_t_initial_state variable.
        the form should be tuple (ex: (0,1,1,0,,,,,)) or integer converted from tuple intepreted by binary.
        if tuple form is (0,1,1,0,1,1), then intepreted integer is 0*1+1*2+1*4+0*8+1*16+1*32= 54"""
        
        if i_or_t_initial_state == "random":
            i_or_t_initial_state = np.random.randint(2,size=len(self.dic_node_order))
            
        if type(i_or_t_initial_state) == int:
            i_or_t_initial_state = tuple(int(i) for i in reversed(bin(i_or_t_initial_state)[2:]))
            if len(i_or_t_initial_state) < len(self.array_state_trajectory[0]):
                i_or_t_initial_state += (0,)*(len(self.array_state_trajectory[0])-len(i_or_t_initial_state))
            
        self.array_state_trajectory[0] = i_or_t_initial_state
        
    def input_drug_perturbation(self, *args, **kwargs):
        """input the perturbation target, perturbation kind (overexpression or suppression), and probability (0.0~1.0)
        if you want to use text file, input the address of that file. the file format is
        MEK	down	1
        GAB1	up	0.4
        ....
        spaced by tab.
        if you write the perturbation condition as arguments,
        write like
        MEK=(0, 1), GAB1=(0,0.4)...."""
        if len(args) >= 1:
            if os.path.exists(args[0]):
                with open(args[0],'r') as file_drugs:
                    for s_line in file_drugs:
                        [s_drug, s_upordown, s_prob] = s_line.split() 
                        if s_upordown == 'up':
                            i_upordown = 1
                        else:
                            i_upordown = 0
                        self.dic_drug_updown_probability[s_drug] = (i_upordown, float(s_prob))
        else:
            self.dic_drug_updown_probability = kwargs
            
    def input_mutation(self, *args, **kwargs):
        """input the mutated gene, and kind of mutation (overexpression or KO)
        if you want to use text file, input the address of that file. the file format is
        MEK	KO
        GAB1	OVER
        ....
        spaced by tab.
        if you write the perturbation condition as arguments,
        write like
        MEK=0, GAB1=1...."""
        if len(args) >= 1:
            if os.path.exists(args[0]):
                with open(args[0],'r') as file_mutations:
                    self.dic_muation_overorsupp = {}
                    for s_line in file_mutations:
                        if s_line == '\n':
                            continue
                        [s_mutation, s_OVERorKO] = s_line.split() 
                        if s_OVERorKO == 'OVER':
                            i_OVERorKO = 1
                        else:
                            i_OVERorKO = 0
                        self.dic_muation_overorsupp[s_mutation] = i_OVERorKO
        else:
            self.dic_muation_overorsupp = kwargs
            
    def input_input_nodes(self, *args, **kwargs):
        """input the input nodes. 
        if you want to use text files, input the address of that file. the file format is
        EGF
        DNA_damage
        WNT
        TGF-beta
        if you write the input node names as arguments,
        write like
        'EGF', 'DNA_damage','WNT','TGF-beta'
        """
        if len(args) == 1:
            if os.path.exists(args[0]):
                with open(args[0],'r') as file_inputnodes:
                    for s_line in file_inputnodes:
                        if s_line == '\n':
                            continue
                        if s_line[-1] == '\n':
                            s_line= s_line[:-1]
                        self.l_input_nodes.append(s_line)
            else: self.l_input_nodes = list(args)
        else:
            self.l_input_nodes = list(args)
        
    
    def perturb_state(self, array_state):
        for s_drug,(i_upordown, float_proba) in self.dic_drug_updown_probability.items():
            if np.random.random() < float_proba:
                array_state[self.dic_node_order[s_drug]] = i_upordown
    
    def mutate_state(self, array_state):
        for s_mutation, i_OVERorKO in self.dic_muation_overorsupp.items():
            array_state[self.dic_node_order[s_mutation]] = i_OVERorKO
            
    def randomize_input_nodes(self, array_state):
        for s_inputnode in self.l_input_nodes:
            array_state[self.dic_node_order[s_inputnode]] = np.random.randint(2)
                   
    def simulate_model(self):
        for i in range(len(self.array_state_trajectory)-1):
            self.perturb_state(self.array_state_trajectory[i])
            self.mutate_state(self.array_state_trajectory[i])
            self.randomize_input_nodes(self.array_state_trajectory[i])
            self.array_state_trajectory[i+1] = self.func_update(self.array_state_trajectory[i])
        self.perturb_state(self.array_state_trajectory[i+1])#final state
        self.mutate_state(self.array_state_trajectory[i+1]) #final state
        self.randomize_input_nodes(self.array_state_trajectory[i]) #final state
    
    def count_True_target(self, s_target, i_count_starting=0):
        """count the True state of target node in the state trajectory.
        counting start at the i_count_starting th trajectory state to the end trajectory state.
        return the num of True of target/(len of trajectory-i_count_starting)"""
        array_target_trajectory = self.array_state_trajectory[i_count_starting:,self.dic_node_order[s_target]]
        return np.count_nonzero(array_target_trajectory)
