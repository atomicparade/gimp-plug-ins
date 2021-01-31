#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def cycle_hue(
    img,
    active_layer,
    num_frames,
    use_existing_layers,
):

    if use_existing_layers:
        num_frames = len(img.layers)

        if num_frames < 2:
            message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
            message.set_markup("There must be at least two layers")
            message.run()
            return

        insert_at = len(img.layers) - 2
    else:
        num_frames = int(num_frames)
        insert_at = img.layers.index(active_layer)

    pdb.gimp_image_undo_group_start(img)

    for i in range(1, num_frames): # original layer is iteration #0
        if use_existing_layers:
            layer = img.layers[insert_at]
            insert_at -= 1
        else:
            layer = pdb.gimp_layer_new_from_drawable(active_layer, img)
            pdb.gimp_image_insert_layer(img, layer, None, insert_at)

        hue_adjustment = ((i * 1.0) / num_frames) * 360

        # gimp_drawable_hue_saturation() accepts a hue_offset between [-180, 180]
        if hue_adjustment > 180:
            hue_adjustment -= 360

        pdb.gimp_drawable_hue_saturation(
            layer
            , 0                 # HUE-RANGE-ALL
            , hue_adjustment
            , 0                 # lightness adjustment
            , 0                 # saturation adjustment
            , 0                 # overlap other hue channels
        )

    pdb.gimp_image_undo_group_end(img)

register(
    "cycle_hue",
    "Cycle hue",
    "Cycle hue",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Image>/Filters/Animation/Cycle hue",
    "*",
    [
        (PF_SPINNER,    "num_frames",           "Total number of frames",                                                           8,      (2, 1000, 1)    ),
        (PF_TOGGLE,     "use_existing_layers",  "Use existing layers (enabling this causes total number of frames to be ignored)",  False                   ),
    ],
    [],
    cycle_hue,
)

main()
