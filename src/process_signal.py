import pandas as pd
import numpy as np

class Signal_preprocessing:
    def __init__(self, list_acc_x, list_acc_y, list_acc_z):

        self.list_acc_x = list_acc_x
        self.list_acc_y = list_acc_y
        self.list_acc_z = list_acc_z

    def extract_clean_signal(self):
        values = [np.mean(self.list_acc_x), np.mean(self.list_acc_y), np.mean(self.list_acc_y), max(self.list_acc_x), \
            max(self.list_acc_y), max(self.list_acc_z), np.std(self.list_acc_x), np.std(self.list_acc_y), np.std(self.list_acc_z), \
                min(self.list_acc_x), min(self.list_acc_y), min(self.list_acc_z)]
        
        return values