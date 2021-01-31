#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def duplicate_all_layers(
    img,
    active_layer,
    num_copies,
):
    n = len(img.layers)

    pdb.gimp_image_undo_group_start(img)

    for i in range(int(n * num_copies)):
        layer = pdb.gimp_layer_new_from_drawable(img.layers[n - 1], img)
        pdb.gimp_image_insert_layer(img, layer, None, 0)

    pdb.gimp_image_undo_group_end(img)

register(
    "duplicate_all_layers",
    "Duplicate all layers",
    "Duplicate all layers",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Image>/Filters/Animation/Duplicate all layers",
    "*",
    [
        (PF_SPINNER, "num_copies", "Number of copies", 1, (1, 1000, 1)),
    ],
    [],
    duplicate_all_layers,
)

main()
