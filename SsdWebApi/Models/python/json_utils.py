# -*- coding: utf-8 -*-

import json
import numpy as np

def from_json_file_to_dict(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data

def from_dict_to_json_file(adict, path):
    with open(path, 'w') as outfile:
        json.dump(adict, outfile)
        
def from_json_file_to_dict_of_numpy(path):
    dict_with_lists = from_json_file_to_dict(path)
    np_dict = {k: np.array(v) for k, v in dict_with_lists.items()}
    return np_dict

def from_dict_of_numpy_to_json_file(adict, path):
    serializable_dict = {k: v.tolist() for k, v in adict.items()}
    from_dict_to_json_file(serializable_dict, path)
    
    
def from_json_file_to_dict_of_dicts_of_numpy(path):
    dict_of_dicts_of_lists = from_json_file_to_dict(path)
    np_dict = {ok: {ik: np.array(iv) if isinstance(iv, list) else iv for ik, iv in ov.items()} for ok, ov in dict_of_dicts_of_lists.items()}  
    return np_dict

def from_dict_of_dicts_of_numpy_to_json_file(adict, path):
    serializable_dict = {ok: {ik: iv.tolist() if isinstance(iv, np.ndarray) else iv for ik, iv in ov.items()} for ok, ov in adict.items()}  
    from_dict_to_json_file(serializable_dict, path)
    return serializable_dict