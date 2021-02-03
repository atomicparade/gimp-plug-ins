#! /usr/bin/env python
from math import cos, pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def zoom_in_and_back_out(
    img,
    original_layer,
    num_frames,
    total_y_shift,
    total_x_shift,
):
    if num_frames % 2 == 1:
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup("The number of frames must be an even number")
        message.run()
        return

    num_frames = int(num_frames)
    insert_at = img.layers.index(original_layer)
    (original_x_offset, original_y_offset) = original_layer.offsets

    # if use_existing_layers:
    #     if (insert_at + 1) < num_frames: # + 1 because the first layer counts
    #         message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
    #         message.set_markup("Not enough layers exist to animate")
    #         message.run()
    #         return

    pdb.gimp_image_undo_group_start(img)

    # Calculate offsets
    x_offset = [0] * num_frames
    y_offset = [0] * num_frames

    middle_idx = num_frames / 2

    for i in range(1, middle_idx + 1):
        # Quintic easing
        # x = i / (float(middle_idx) / 2)

        # if x < 1:
        #     pct = (pow(x, 5)) / 2
        # else:
        #     pct = (pow(x - 2, 5) + 2) / 2

        # Sinusoidal easing
        pct = float(i) / middle_idx
        pct = (1 - cos(pi * pct)) / 2

        y_offset[i] = pct * total_y_shift
        x_offset[i] = pct * total_x_shift

        if i != middle_idx:
            y_offset[num_frames - i] = y_offset[i]
            x_offset[num_frames - i] = x_offset[i]

    # Shift layers
    for i in range(1, num_frames): # Active layer counts as the first layer
        # if use_existing_layers:
        #     layer = img.layers[insert_at]
        #     insert_at -= 1
        # else:
        #     layer = pdb.gimp_layer_new_from_drawable(original_layer, img)
        #     pdb.gimp_image_insert_layer(img, layer, None, insert_at)

        layer = pdb.gimp_layer_new_from_drawable(original_layer, img)
        pdb.gimp_image_insert_layer(img, layer, None, insert_at)
        pdb.gimp_layer_set_offsets(layer, x_offset[i] + original_x_offset, y_offset[i] + original_y_offset)

        pdb.gimp_layer_resize_to_image_size(layer)

    pdb.gimp_image_undo_group_end(img)

register(
    "animate_layer_shift",
    "Animate layer shift",
    "Animate layer shift",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Image>/Filters/Animation/Animate layer shift",
    "*",
    [
        (PF_SPINNER,    "num_frames",       "Total number of frames (must be an even number)",  8,  (2, 1000, 2)        ),
        (PF_SPINNER,    "total_y_shift",    "Total Y shift",                                    0,  (-10000, 10000, 1)  ),
        (PF_SPINNER,    "total_x_shift",    "Total X shift",                                    0,  (-10000, 10000, 1)  ),
    ],
    [],
    zoom_in_and_back_out,
)

main()
