"""
Cifar10 download/process functions.
"""


import os
import numpy as np
from ... import utils, storage

str2ascii = utils.convert_str_to_ascii


class Cifar10:
    """ Cifar10 preprocessing/downloading functions """

    # download url
    url = 'https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz'
    md5_checksum = 'c58f30108f718f92721af3b95e74349a'

    # extracted file names
    data_files = [
        "batches.meta",
        "data_batch_1",
        "data_batch_2",
        "data_batch_3",
        "data_batch_4",
        "data_batch_5",
        "test_batch"
    ]

    # some keywords. These are used to classify datasets for easier
    # categorization.
    keywords = ['image_processing', 'classification']


    def __init__(self, data_path, cache_path, verbose=True):
        """
        Initialize class.
        """
        self.cache_path = cache_path
        self.data_path = data_path
        self.verbose = verbose


    def download(self, is_download=True):
        """
        Download and extract files to disk.
        """
        # download + extract data and remove temporary files
        if is_download:
            utils.download_extract_all(self.url, self.md5_checksum, self.data_path, False, self.verbose)

        return self.keywords


    def get_object_list(self, data, labels):
        """
        Groups the data + labels info in a 'list' of indexes.
        """
        #object_id = np.ndarray((data.shape[0], 2), dtype=np.uint16)
        object_id = np.ndarray((data.shape[0], 2), dtype=int)
        for i in range(data.shape[0]):
            object_id[i][0] = i
            object_id[i][1] = labels[i]
        return object_id


    def load_data(self):
        """
        Load the data from the files.
        """
        # merge the path with the extracted folder name
        data_path_ = os.path.join(self.data_path, 'cifar-10-batches-py')

        # load classes name file
        class_names = utils.load_pickle(os.path.join(data_path_, self.data_files[0]))

        # load train data files
        train_batch1 = utils.load_pickle(os.path.join(data_path_, self.data_files[1]))
        train_batch2 = utils.load_pickle(os.path.join(data_path_, self.data_files[2]))
        train_batch3 = utils.load_pickle(os.path.join(data_path_, self.data_files[3]))
        train_batch4 = utils.load_pickle(os.path.join(data_path_, self.data_files[4]))
        train_batch5 = utils.load_pickle(os.path.join(data_path_, self.data_files[5]))

        # concatenate data
        train_data = np.concatenate((
            train_batch1['data'],
            train_batch2['data'],
            train_batch3['data'],
            train_batch4['data'],
            train_batch5['data']),
            axis=0)

        train_labels = np.concatenate((
            train_batch1['labels'],
            train_batch2['labels'],
            train_batch3['labels'],
            train_batch4['labels'],
            train_batch5['labels']),
            axis=0)

        train_data = train_data.reshape((50000, 3, 32, 32))
        train_data = np.transpose(train_data, (0,2,3,1)) # NxHxWxC
        train_object_list = self.get_object_list(train_data, train_labels)

        # load test data file
        test_batch = utils.load_pickle(os.path.join(data_path_, self.data_files[6]))

        test_data = test_batch['data'].reshape(10000, 3, 32, 32)
        test_data = np.transpose(test_data, (0,2,3,1)) # NxHxWxC
        test_labels = np.array(test_batch['labels'], dtype=np.uint8)
        test_object_list = self.get_object_list(test_data, test_labels)

        #return a dictionary
        return {
            "object_fields": ['data', 'class_name'],
            "class_name": class_names['label_names'],
            "train_data": train_data,
            "train_labels": train_labels,
            "train_object_id_list": train_object_list,
            "test_data": test_data,
            "test_labels": test_labels,
            "test_object_id_list": test_object_list
        }


    def classification_metadata_process(self):
        """
        Process metadata and store it in a hdf5 file.
        """

        # load data to memory
        data = self.load_data()

        # create/open hdf5 file with subgroups for train/val/test
        file_name = os.path.join(self.cache_path, 'classification.h5')
        fileh5 = storage.StorageHDF5(file_name, 'w')

        # add data to the **default** group
        fileh5.add_data('train/source', 'class_name', str2ascii(data["class_name"]), np.uint8)
        fileh5.add_data('train/source', 'data', data["train_data"], np.uint8)
        fileh5.add_data('train/source', 'labels', data["train_labels"], np.uint8)

        fileh5.add_data('test/source', 'class_name', str2ascii(data["class_name"]), np.uint8)
        fileh5.add_data('test/source', 'data', data["test_data"], np.uint8)
        fileh5.add_data('test/source', 'labels', data["test_labels"], np.uint8)

        # add data to the **list** group
        # write data to the metadata file
        fileh5.add_data('train/default', 'class_name', str2ascii(data["class_name"]), np.uint8)
        fileh5.add_data('train/default', 'data', data["train_data"], np.uint8)
        fileh5.add_data('train/default', 'object_id', data["train_object_id_list"], np.int32)
        # object fields is necessary to identify which fields compose 'object_id'
        fileh5.add_data('train/default', 'object_fields', str2ascii(data['object_fields']), np.uint8)

        fileh5.add_data('test/default', 'class_name', str2ascii(data["class_name"]), np.uint8)
        fileh5.add_data('test/default', 'data', data["test_data"], np.uint8)
        fileh5.add_data('test/default', 'object_id', data["test_object_id_list"], np.int32)
        # object fields is necessary to identify which fields compose 'object_id'
        fileh5.add_data('test/default', 'object_fields', str2ascii(data['object_fields']), np.uint8)

        # close file
        fileh5.close()

        # return information of the task + cache file
        return file_name


    def process(self):
        """
        Process metadata for all tasks
        """
        classification_filename = self.classification_metadata_process()

        info_output = {
            "default" : classification_filename,
            "classification" : classification_filename,
        }

        return info_output, self.keywords