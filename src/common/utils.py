import os
import re

import numpy as np


def get_filenames_from_folder(mypath):
    return [file for file in os.listdir(mypath)
            if os.path.isfile(os.path.join(mypath, file)) and
            os.path.splitext(file)[0] not in {".DS_Store", "_DS_Store"}]


def get_filename(file_path, with_ext=True):
    if with_ext:
        return os.path.basename(file_path)
    else:
        return os.path.splitext(os.path.basename(file_path))[0]


def standardize_filename(filename):
    return re.sub("[^a-z0-9-_]", "", filename.lower())


def feature_reshape(feature, multi=False):
    """
    reshape mfccBands feature into n_sample * n_row * n_col
    :param feature:
    :return:
    """

    n_sample = feature.shape[0]
    n_row = 80
    n_col = 15

    feature_reshaped = np.zeros((n_sample, n_row, n_col), dtype='float16')
    if multi:
        feature_reshaped = np.zeros((n_sample, n_row, n_col, feature.shape[-1]), dtype='float16')
    # print("reshaping feature...")
    for ii in range(n_sample):
        # print ii
        feature_frame = np.zeros((n_row, n_col), dtype='float16')
        if multi:
            feature_frame = np.zeros((n_row, n_col, feature.shape[-1]), dtype='float16')
        for jj in range(n_col):
            feature_frame[:, jj] = feature[ii][n_row * jj:n_row * (jj + 1)]
        feature_reshaped[ii, :, :] = feature_frame
    return feature_reshaped


def get_features_mean_std(features):
    return [np.nanmean(np.nanmean(features, axis=1), axis=0, dtype="float32"),
            np.nanmean(np.nanstd(features, axis=1), axis=0, dtype="float32")]


def get_scalers(features, multi):
    """
    Gather scalers along the frequency axis
    :param features: nparray - audio feature frames reshaped into time and frequency axises
    :param multi: bool - True if using multiple channels
    :return scalers: list - mean and std for each frequency band for each channel
    """
    # TODO: Add better check for non formatted features
    if {80 * 15 * 3, 80 * 15} in features.shape[1:]:
        raise ValueError('Need to reshape features before getting scalers')

    scalers = []
    if multi:
        import multiprocessing
        import psutil
        with multiprocessing.Pool(psutil.cpu_count(logical=False)) as pool:
            for result in pool.imap(get_features_mean_std, (features[:, :, i, :] for i in range(15))):
                scalers.append(result)
        return np.array(scalers).T
    else:
        return get_features_mean_std(features)
