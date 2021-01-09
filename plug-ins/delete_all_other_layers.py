#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def delete_all_other_layers(
    img,
    active_layer,
):
    pdb.gimp_image_undo_group_start(img)

    for layer in img.layers:
        if layer != active_layer:
            pdb.gimp_image_remove_layer(img, layer)

    pdb.gimp_image_undo_group_end(img)

register(
    "delete_all_other_layers",
    "Delete all other layers",
    "Delete all other layers",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Image>/Filters/Animation/Delete all other layers",
    "*",
    [],
    [],
    delete_all_other_layers,
)

main()
