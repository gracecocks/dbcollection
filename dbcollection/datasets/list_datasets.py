"""
Datasets list.

All available datasets must be added in this file.
"""


#---------------------------------------------------------
# List of image processing datasets
#---------------------------------------------------------

from . import cifar, pascal_voc, mnist, imagenet, ucf

object_classification = {
    "cifar10" : cifar.cifar10.Cifar10,
    "cifar100" : cifar.cifar100.Cifar100,
    "ilsvrc2012": imagenet.ILSVRC2012,
    'mnist': mnist.MNIST,
    "pascal_voc_2007" : pascal_voc.y2007.PascalVOC2007,
}

human_action = {
    "ucf101" : ucf.ucf101.UCF101,
    "ucfsports" : ucf.ucfsports.UCFSports
}

#---------------------------------------------------------
# MAIN list
#---------------------------------------------------------

datasets = {}
datasets.update(object_classification) # object classification
datasets.update(human_action) # human action

# list of all dataset's names
available_datasets = list(datasets.keys())