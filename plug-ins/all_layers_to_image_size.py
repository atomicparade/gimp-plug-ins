#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def all_layers_to_image_size(
    img,
    active_layer,
):
    pdb.gimp_image_undo_group_start(img)

    for layer in img.layers:
        pdb.gimp_layer_resize_to_image_size(layer)

    pdb.gimp_image_undo_group_end(img)

register(
    "all_layers_to_image_size",
    "All layers to image size",
    "All layers to image size",
    "atomicparade",
    "atomicparade",
    "February 2021",
    "<Image>/Filters/Animation/All layers to image size",
    "*",
    [
    ],
    [],
    all_layers_to_image_size,
)

main()
