#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def merge_layers_from_another_image(
    img,
    active_layer,
    img_path,
    merge_above,
):
    if img_path == "":
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup("Please specify the image to merge")
        message.run()
        return

    # Load base image
    img_to_merge = pdb.gimp_file_load(img_path, img_path)

    num_layers_to_merge = min(len(img.layers), len(img_to_merge.layers))

    pdb.gimp_image_undo_group_start(img)

    for i in range(num_layers_to_merge):
        if i >= len(img_to_merge.layers):
            break

        idx_img = len(img.layers) - i - 1
        idx_merge = len(img_to_merge.layers) - i - 1

        layer = pdb.gimp_layer_new_from_drawable(img_to_merge.layers[idx_merge], img)

        pdb.gimp_image_insert_layer(img, layer, None, idx_img if merge_above else idx_img + 1)
        pdb.gimp_image_merge_down(img, img.layers[idx_img], EXPAND_AS_NECESSARY)

    pdb.gimp_image_delete(img_to_merge)

    pdb.gimp_image_undo_group_end(img)

register(
    "merge_layers_from_another_image",
    "Merge layers from another image",
    "Merge layers from another image",
    "atomicparade",
    "atomicparade",
    "February 2021",
    "<Image>/Filters/Animation/Merge layers from another image",
    "",
    [
        (PF_FILENAME,   "img_path",     "Image",        ""),
        (PF_BOOL,       "merge_above",  "Merge on top", True),
    ],
    [],
    merge_layers_from_another_image,
)

main()
