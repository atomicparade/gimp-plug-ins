#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def zoom_in_and_back_out(
    img,
    original_layer,
    num_frames,
    repeat_first_frame,
    ease_in,
    use_existing_layers,
):
    (selection_is_empty, x1, y1, x2, y2) = pdb.gimp_selection_bounds(img)

    if num_frames % 2 == 1:
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup("The number of frames must be an even number")
        message.run()
        return

    if selection_is_empty == 0:
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup("Please select a part of the image to zoom in on")
        message.run()
        return

    num_frames = int(num_frames)
    insert_at = img.layers.index(original_layer)

    if use_existing_layers:
        if (insert_at + 1) < num_frames: # + 1 because the first layer counts
            message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
            message.set_markup("Not enough layers exist to zoom in on")
            message.run()
            return

    pdb.gimp_image_undo_group_start(img)

    # Calculate widths, heights, and offsets
    width = [0] * num_frames
    height = [0] * num_frames
    x_offset = [0] * num_frames
    y_offset = [0] * num_frames

    middle_idx = num_frames / 2
    num_zooms = num_frames / 2

    for i in range(1, middle_idx + 1):
        if ease_in:
            # Cubic easing
            pct = 1 - pow(float(middle_idx - i) / num_zooms, 3)
        else:
            pct = float(i) / num_zooms

        left = pct * x1
        top = pct * y1
        right = img.width - (img.width - x2) * pct
        bottom = img.height - (img.height - y2) * pct

        width[i] = right - left
        height[i] = bottom - top
        x_offset[i] = -left
        y_offset[i] = -top

        if i != middle_idx:
            width[num_frames - i] = right - left
            height[num_frames - i] = bottom - top
            x_offset[num_frames - i] = -left
            y_offset[num_frames - i] = -top

    for i in range(1, num_frames): # Active layer counts as the first layer
        if use_existing_layers:
            layer = img.layers[insert_at]
            insert_at -= 1
        else:
            layer = pdb.gimp_layer_new_from_drawable(original_layer, img)
            pdb.gimp_image_insert_layer(img, layer, None, insert_at)

        # Crop
        pdb.gimp_layer_resize(layer, width[i], height[i], x_offset[i], y_offset[i])

        # Scale up
        pdb.gimp_layer_scale(
            layer,
            img.width,
            img.height,
            True, # Scale from origin of layer, not image
        )

        # Move to center
        pdb.gimp_layer_set_offsets(layer, 0, 0)

    if repeat_first_frame:
        layer = pdb.gimp_layer_new_from_drawable(original_layer, img)
        pdb.gimp_image_insert_layer(img, layer, None, insert_at)

    pdb.gimp_image_undo_group_end(img)

register(
    "zoom_in_and_back_out",
    "Zoom in and back out",
    "Zoom in and back out",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Image>/Filters/Animation/Zoom in and back out",
    "*",
    [
        (PF_SPINNER,    "num_frames",           "Total number of frames (must be an even number)",  8,      (2, 1000, 1)    ),
        (PF_TOGGLE,     "repeat_first_frame",   "Repeat first frame at the end",                    False                   ),
        (PF_TOGGLE,     "ease_in",              "Ease in",                                          True                    ),
        (PF_TOGGLE,     "use_existing_layers",  "Use existing layers",                              False                   ),
    ],
    [],
    zoom_in_and_back_out,
)

main()
