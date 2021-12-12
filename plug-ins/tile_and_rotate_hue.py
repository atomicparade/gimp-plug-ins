#! /usr/bin/env python
from math import ceil, log
from gimpfu import *
import gtk

pdb = gimp.pdb

def copy_and_paste_layer(img, layer, destination_x, destination_y):
    pdb.gimp_image_select_rectangle(
        img,
        CHANNEL_OP_REPLACE,
        0,          # X
        0,          # Y
        img.width,  # Width
        img.height, # Height
    )

    pdb.gimp_edit_copy(layer)

    floating_sel = pdb.gimp_edit_paste(layer, True)

    floating_sel = pdb.gimp_item_transform_2d(
        floating_sel,
        0,              # Source X
        0,              # Source Y
        1,              # Scale X
        1,              # Scale Y
        0,              # Rotation angle
        destination_x,  # Destination X
        destination_y,  # Detination Y
    )

    pdb.gimp_floating_sel_anchor(floating_sel)

def shift_hue(img, layer, x, y, width, height, hue_offset):
    pdb.gimp_image_select_rectangle(
        img,
        CHANNEL_OP_REPLACE,
        x,
        y,
        width,
        height,
    )

    # gimp_drawable_hue_saturation() accepts a hue_offset between [-180, 180]
    if hue_offset > 180:
        hue_offset -= 360

    pdb.gimp_drawable_hue_saturation(
        layer,
        HUE_RANGE_ALL,
        hue_offset,
        0,    # Lightness adjustment
        0,    # Saturation adjustment
        0,    # Overlap other hue channels
    )

def tile_and_rotate_hue(
    img,
    active_layer,
    horizontal_copies,
    vertical_copies,
):
    horizontal_copies = int(horizontal_copies)
    vertical_copies = int(vertical_copies)

    original_width = img.width
    original_height = img.height

    pdb.gimp_image_undo_group_start(img)

    # Resize entire canvas
    pdb.gimp_image_resize(
        img,
        original_width * horizontal_copies,
        original_height * vertical_copies,
        0,  # X offset
        0,  # Y offset
    )

    pdb.gimp_layer_resize_to_image_size(active_layer)

    horizontal_doublings = int(ceil(log(horizontal_copies, 2)))
    vertical_doublings = int(ceil(log(vertical_copies, 2)))

    # Double horizontally
    for i in range(horizontal_doublings):
        copy_and_paste_layer(img, active_layer, original_width * pow(2, i), 0)

    # Double vertically
    for i in range(vertical_doublings):
        copy_and_paste_layer(img, active_layer, 0, original_height * pow(2, i))

    shift_increment = 360.0 / (horizontal_copies * vertical_copies)

    # Shift hue in vertical stripes
    for i in range(1, horizontal_copies):
        shift_hue(
            img,
            active_layer,
            original_width * i,
            0,
            original_width,
            img.height,
            shift_increment * i,
        )

    # Shift hue in horizontal stripes
    for i in range(1, vertical_copies):
        shift_hue(
            img,
            active_layer,
            0,
            original_height * i,
            img.width,
            original_height,
            shift_increment * i * horizontal_copies,
        )

    pdb.gimp_layer_resize_to_image_size(active_layer)

    # Clear selection
    pdb.gimp_image_select_rectangle(
        img,
        CHANNEL_OP_REPLACE,
        0,
        0,
        0,
        0,
    )

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
        (PF_SPINNER,    "horizontal_copies",    "Horizontal copies",    1,  (1, 100, 1) ),
        (PF_SPINNER,    "vertical_copies",      "Vertical copies",      1,  (1, 100, 1) ),
    ],
    [],
    tile_and_rotate_hue,
)

main()
