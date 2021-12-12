#! /usr/bin/env python
from gimpfu import *
import gtk

pdb = gimp.pdb

def tile_and_rotate_hue(
    img,
    original_layer,
    horizontal_copies,
    vertical_copies,
):
    horizontal_copies = int(horizontal_copies)
    vertical_copies = int(vertical_copies)

    insert_idx = img.layers.index(original_layer)
    total_copies = horizontal_copies * vertical_copies
    width = img.width
    height = img.height

    pdb.gimp_image_undo_group_start(img)

    # Resize entire canvas
    pdb.gimp_image_resize(
        img,
        width * horizontal_copies,
        height * vertical_copies,
        0,  # X offset
        0,  # Y offset
    )

    copy_number = 1
    for i in range(vertical_copies):
        for j in range(horizontal_copies):
            # No operation needed on the very first one
            if i == 0 and j == 0:
                continue

            # Create copy
            layer = pdb.gimp_layer_new_from_drawable(original_layer, img)
            pdb.gimp_image_insert_layer(
                img,
                layer,
                None, # Parent layer (i.e. group)
                insert_idx,
            )

            # Shift X and Y
            pdb.gimp_layer_translate(layer, width * j, height * i)

            # Shift hue
            hue_adjustment = ((copy_number * 1.0) / total_copies) * 360

            # gimp_drawable_hue_saturation() accepts a hue_offset between [-180, 180]
            if hue_adjustment > 180:
                hue_adjustment -= 360

            pdb.gimp_drawable_hue_saturation(
                layer,
                HUE_RANGE_ALL,
                hue_adjustment,
                0,    # Lightness adjustment
                0,    # Saturation adjustment
                0,    # Overlap other hue channels
            )

            # Merge down

            copy_number += 1

    # Merge down
    merge_layer_idx = img.layers.index(original_layer) - total_copies + 1

    for i in range(total_copies - 1):
        layer = img.layers[merge_layer_idx]
        pdb.gimp_image_merge_down(img, layer, EXPAND_AS_NECESSARY)

    pdb.gimp_image_undo_group_end(img)

register(
    "tile_and_rotate_hue",
    "Tile and rotate hue",
    "Tile and rotate hue",
    "atomicparade",
    "atomicparade",
    "December 2021",
    "<Image>/Filters/Artistic/Tile and rotate hue",
    "*",
    [
        (PF_SPINNER,    "horizontal_copies",    "Horizontal copies",    1,  (1, 25, 1)  ),
        (PF_SPINNER,    "vertical_copies",      "Vertical copies",      1,  (1, 25, 1)  ),
    ],
    [],
    tile_and_rotate_hue,
)

main()
