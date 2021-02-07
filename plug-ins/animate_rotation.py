#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def animate_rotation(
    img,
    active_layer,
    num_frames,
    anticlockwise,
    use_existing_layers,
):
    num_frames = int(num_frames)

    idx = img.layers.index(active_layer)

    if use_existing_layers and num_frames > (idx + 1):
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup("Not enough layers exist on top of the active layer")
        message.run()
        return

    rotate_radians = (pi * 2) / num_frames

    if anticlockwise:
        rotate_radians *= -1

    pdb.gimp_image_undo_group_start(img)

    for i in range(1, num_frames): # 0 = original layer
        if use_existing_layers:
            idx -= 1
            layer = img.layers[idx]
        else:
            layer = pdb.gimp_layer_new_from_drawable(active_layer, img)
            pdb.gimp_image_insert_layer(img, layer, None, idx)

        pdb.gimp_item_transform_rotate(layer, rotate_radians * i, True, 0, 0)

    pdb.gimp_image_undo_group_end(img)

register(
    "animate_rotation",
    "Animate rotation",
    "Animate rotation",
    "atomicparade",
    "atomicparade",
    "February 2021",
    "<Image>/Filters/Animation/Animate rotation",
    "*",
    [
        (PF_SPINNER,    "num_frames",           "Number of frames",     8, (2, 1000, 1) ),
        (PF_BOOL,       "anticlockwise",        "Anticlockwise",        False           ),
        (PF_BOOL,       "use_existing_layers",  "Use existing layers",  False           ),
    ],
    [],
    animate_rotation,
)

main()
