import pandas as pd
import numpy as np

class SignalPreprocessing:

    @classmethod
    def extract_clean_signal(self, list_acc_x, list_acc_y, list_acc_z):
        values = [np.mean(list_acc_x), np.mean(list_acc_y), np.mean(list_acc_y), max(list_acc_x), \
            max(list_acc_y), max(list_acc_z), np.std(list_acc_x), np.std(list_acc_y), np.std(list_acc_z), \
                min(list_acc_x), min(list_acc_y), min(list_acc_z)]
        
        return values
