#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def cycle_hue_radially(
    img,
    active_layer,
    num_stripes,
    reverse,
):
    num_stripes = int(num_stripes)

    pdb.gimp_image_undo_group_start(img)

    center_x = img.width / 2
    center_y = img.height / 2

    incremental_hue_adjustment = -360 / num_stripes

    if reverse:
        incremental_hue_adjustment *= -1

    for i in range(0, num_stripes):
        width = img.width * ((num_stripes - i) / (num_stripes * 1.0))
        height = img.height * ((num_stripes - i) / (num_stripes * 1.0))

        x = center_x - (width / 2)
        y = center_y - (height / 2)

        pdb.gimp_ellipse_select(
            img,
            x,
            y,
            width,
            height,
            CHANNEL_OP_REPLACE,
            True,   # Anti-aliasing
            False,  # Feathering
            0,      # Feather radius
        )

        pdb.gimp_drawable_hue_saturation(
            active_layer
            , 0                 # HUE-RANGE-ALL
            , incremental_hue_adjustment
            , 0                 # lightness adjustment
            , 0                 # saturation adjustment
            , 0                 # overlap other hue channels
        )

    pdb.gimp_selection_none(img)

    pdb.gimp_image_undo_group_end(img)

register(
    "cycle_hue_radially",
    "Cycle hue radially",
    "Cycle hue radially",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Image>/Filters/Artistic/Cycle hue radially",
    "*",
    [
        (PF_SPINNER, "num_stripes", "Number of stripes", 8, (2, 1000, 1)),
        (PF_BOOL, "reverse",        "Reverse direction", False          ),
    ],
    [],
    cycle_hue_radially,
)

main()
