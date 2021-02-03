#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def duplicate_layer(
    img,
    active_layer,
    num_dupes,
):
    num_dupes = int(num_dupes)

    pdb.gimp_image_undo_group_start(img)

    insert_pos = img.layers.index(active_layer)

    for i in range(num_dupes):
        layer = pdb.gimp_layer_new_from_drawable(active_layer, img)
        pdb.gimp_image_insert_layer(img, layer, None, insert_pos)

    pdb.gimp_image_undo_group_end(img)

register(
    "duplicate_layer",
    "Duplicate layer",
    "Duplicate layer",
    "atomicparade",
    "atomicparade",
    "February 2021",
    "<Image>/Filters/Animation/Duplicate layer",
    "*",
    [
        (PF_SPINNER, "num_dupes", "Number of duplicates", 1, (1, 1000, 1)),
    ],
    [],
    duplicate_layer,
)

main()
