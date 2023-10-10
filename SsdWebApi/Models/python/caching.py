# -*- coding: utf-8 -*-

from functools import lru_cache, wraps
import shelve
import numpy as np





def enable_nparray_cache(*args, **kwargs):
    """
    Decorator to apply to any function taking any number of arguments with 
    an array as first argument that enables in-memory caching if the remaining 
    arguments are serializable.
    """
    def decorator(function):
        @wraps(function)
        def wrapper(np_array, *args, **kwargs):
            hashable_array = array_to_tuple(np_array)
            return cached_wrapper(hashable_array, *args, **kwargs)

        @lru_cache(*args, **kwargs)
        def cached_wrapper(hashable_array, *args, **kwargs):
            array = np.array(hashable_array)
            return function(array, *args, **kwargs)

        def array_to_tuple(np_array):
            try:
                return tuple(array_to_tuple(_) for _ in np_array)
            except TypeError:
                return np_array

        wrapper.cache_info = cached_wrapper.cache_info
        wrapper.cache_clear = cached_wrapper.cache_clear
        return wrapper
    return decorator



def enable_shelve_cache(file_name):
    """
    Decorator to apply to any class method taking 1 array argument (other than 
    self) that enables disk/memory caching improving performances when the 
    function takes too long to be computed.
    """
    d = shelve.open(file_name)

    def decorator(func):
        def new_func(s, candidate):
            hashable_candidate = str(candidate.tolist()) #tuple(candidate)
            if hashable_candidate not in d:
                d[hashable_candidate] = func(s, candidate)
            return d[hashable_candidate]

        return new_func

    return decorator