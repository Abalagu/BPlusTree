# Created by Luming on 11/11/2020 1:39 PM
import numpy as np


def gen_record(key_range, num_record):
    samples: np.ndarray = np.random.choice(key_range, num_record, False)
    return samples.tolist()
