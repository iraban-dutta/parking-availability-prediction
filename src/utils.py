import sys
import os
import numpy as np
import pandas as pd
import pickle
from src.exception import CustomException



def save_object(file_path, obj):
    try:

        # Creating a directory
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
        

    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)
    

def load_object(file_path):
    try:
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)

    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)