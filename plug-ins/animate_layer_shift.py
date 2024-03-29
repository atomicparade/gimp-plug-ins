#! /usr/bin/env python
from math import cos, pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def animate_layer_shift(
    img,
    original_layer,
    num_frames,
    total_y_shift,
    total_x_shift,
    shift_back,
    use_easing,
    use_existing_layers,
):
    if num_frames % 2 == 1:
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup("The number of frames must be an even number")
        message.run()
        return

    num_frames = int(num_frames)
    starting_layer = img.layers.index(original_layer)

    if use_existing_layers and ((starting_layer + 1) - num_frames) < 0:
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup("Use existing layers was selected, but there are not enough layers")
        message.run()
        return

    (original_x_offset, original_y_offset) = original_layer.offsets

    pdb.gimp_image_undo_group_start(img)

    # Calculate offsets
    x_offset = [0] * num_frames
    y_offset = [0] * num_frames

    if shift_back:
        middle_idx = num_frames / 2

        for i in range(1, middle_idx + 1):
            pct = float(i) / middle_idx

            if use_easing:
                pct = (1 - cos(pi * pct)) / 2 # Sinusoidal easing

            y_offset[i] = pct * total_y_shift
            x_offset[i] = pct * total_x_shift

            if i != middle_idx:
                y_offset[num_frames - i] = y_offset[i]
                x_offset[num_frames - i] = x_offset[i]
    else:
        for i in range(1, num_frames):
            pct = float(i) / num_frames

            if use_easing:
                pct = (1 - cos(pi * pct)) / 2 # Sinusoidal easing

            y_offset[i] = pct * total_y_shift
            x_offset[i] = pct * total_x_shift

    curr_layer = starting_layer

    # Shift layers
    if use_existing_layers:
        curr_layer = starting_layer - 1

        for i in range(1, num_frames): # Active layer counts as the first layer
            layer = img.layers[curr_layer]
            curr_layer -= 1

            pdb.gimp_layer_set_offsets(layer, x_offset[i] + original_x_offset, y_offset[i] + original_y_offset)
            pdb.gimp_layer_resize_to_image_size(layer)
    else:
        for i in range(1, num_frames): # Active layer counts as the first layer
            layer = pdb.gimp_layer_new_from_drawable(original_layer, img)
            pdb.gimp_image_insert_layer(img, layer, None, starting_layer)

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
        (PF_SPINNER,    "num_frames",           "Total number of frames (must be an even number)",  8,      (2, 1000, 2)        ),
        (PF_SPINNER,    "total_y_shift",        "Total Y shift",                                    0,      (-10000, 10000, 1)  ),
        (PF_SPINNER,    "total_x_shift",        "Total X shift",                                    0,      (-10000, 10000, 1)  ),
        (PF_TOGGLE,     "shift_back",           "Shift back to original position",                  False                       ),
        (PF_TOGGLE,     "use_easing",           "Use easing",                                       False                       ),
        (PF_TOGGLE,     "use_existing_layers",  "Use existing layers",                              False                       ),
    ],
    [],
    animate_layer_shift,
)

main()
