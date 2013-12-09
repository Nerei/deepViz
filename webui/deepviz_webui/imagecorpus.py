import cPickle
import os
from math import sqrt
import numpy as np
from PIL import Image


class CIFAR10ImageCorpus(object):
    """
    Class for loading images from the Python version of the CIFAR-10
    corpus: http://www.cs.toronto.edu/~kriz/cifar-10-py-colmajor.tar.gz
    """
    def __init__(self, root_folder):
        with open(os.path.join(root_folder, "batches.meta")) as metafile:
            meta = cPickle.load(metafile)
            self.label_names = meta['label_names']
        batches = sorted(os.listdir(root_folder))[1:]  # Skip batches.meta.
        self._image_data = None
        self._image_labels = None
        self.filenames = {}
        for batch in batches:
            with open(os.path.join(root_folder, batch)) as batchfile:
                data = cPickle.load(batchfile)
                # data.keys() == ['batch_label', 'labels', 'data', 'filenames']
                if self._image_data is None:
                    offset = 0
                    self._image_data = data['data'].T  # colmajor version
                    self._image_labels = data['labels']
                else:
                    offset = self._image_data.shape[0]
                    self._image_data = np.concatenate((self._image_data, data['data'].T))
                    self._image_labels.extend(data['labels'])
                for (counter, filename) in enumerate(data['filenames']):
                    self.filenames[filename] = offset + counter

    def find_images(self, query):
        """
        Return the names of images that match a query
        """
        for image_name in self.filenames.keys():
            if query in image_name:
                yield image_name

    def get_image(self, filename):
        data = self._image_data[self.filenames[filename]]
        ksize = sqrt(len(data) / 3)
        rgb_data = np.rot90(np.reshape(data, (ksize, ksize, 3), 'F'), 3)
        return Image.fromarray(rgb_data)

    def get_all_images_data(self):
        ksize = sqrt(len(self._image_data[0]) / 3)
        return np.reshape(self._image_data, (self._image_data.shape[0], ksize, ksize, 3), 'F')

    def get_class(self, filename):
        return self.label_names[self._image_labels[self.filenames[filename]]]