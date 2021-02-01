#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def cycle_hue_in_stripes(
    img,
    active_layer,
    num_stripes,
    horizontal,
    reverse,
):
    num_stripes = int(num_stripes)

    pdb.gimp_image_undo_group_start(img)

    if horizontal:
        stripe_thickness = img.height / (num_stripes * 1.0)
    else:
        stripe_thickness = img.width / (num_stripes * 1.0)

    for i in range(1, num_stripes):
        if horizontal:
            x = 0
            y = int(stripe_thickness * i)
            width = img.width

            next_y = int(stripe_thickness * (i + 1))
            height = next_y - y
        else:
            x = int(stripe_thickness * i)
            y = 0
            height = img.height

            next_x = int(stripe_thickness * (i + 1))
            width = next_x - x

        pdb.gimp_rect_select(
            img
            , x
            , y
            , width
            , height
            , CHANNEL_OP_REPLACE # Channel operation (replace current selection)
            , False              # Whether to feather
            , 0                  # Feather radius
        )

        hue_adjustment = ((i * 1.0) / num_stripes) * 360

        # gimp_drawable_hue_saturation() accepts a hue_offset between [-180, 180]
        if hue_adjustment > 180:
            hue_adjustment -= 360

        if reverse:
            hue_adjustment *= -1

        pdb.gimp_drawable_hue_saturation(
            active_layer
            , 0                 # HUE-RANGE-ALL
            , hue_adjustment
            , 0                 # lightness adjustment
            , 0                 # saturation adjustment
            , 0                 # overlap other hue channels
        )

    pdb.gimp_selection_none(img)

    pdb.gimp_image_undo_group_end(img)

register(
    "cycle_hue_in_stripes",
    "Cycle hue in stripes",
    "Cycle hue in stripes",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Image>/Filters/Artistic/Cycle hue in stripes",
    "*",
    [
        (PF_SPINNER, "num_stripes", "Number of stripes",                    8, (2, 1000, 1) ),
        (PF_BOOL, "horizontal",     "Horizontal (set false for vertical)",  True            ),
        (PF_BOOL, "reverse",        "Reverse direction",                    False           ),
    ],
    [],
    cycle_hue_in_stripes,
)

main()
