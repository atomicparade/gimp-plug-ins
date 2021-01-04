#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def create_slide_spin(
    base_img_path,
    background_img_path,
    mask_img_path,
    output_img_path,
    base_img_overlap,
    final_img_size,
    num_slide_frames,
    num_frames,
    frame_length_ms,
    generate_xcf,
):
    if base_img_path == "" or background_img_path == "" or mask_img_path == "" or output_img_path == "":
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup("Base image, background image, mask image, and output are required")
        message.run()
        return

    final_img_size = int(final_img_size)
    num_frames = int(num_frames)
    frame_length_ms = int(frame_length_ms)

    rotate_rad = 360 / num_frames * pi / 180

    # Load base image
    img = pdb.gimp_file_load(base_img_path, base_img_path)

    background_img = pdb.gimp_file_load(background_img_path, background_img_path)
    mask_img = pdb.gimp_file_load(mask_img_path, mask_img_path)

    base_img_width = img.width
    base_img_height = img.height

    # Overlap the image 5 times
    slide_size = int((img.width - base_img_overlap) * 4 + img.width)
    slide_center = int(slide_size / 2)

    pdb.gimp_image_resize(
        img,
        slide_size,                                # Width
        slide_size,                                # Height
        slide_size - base_img_width,               # X offset
        int((slide_size - base_img_height) / 2)    # Y offset
    )

    pdb.gimp_edit_copy_visible(img)

    for i in range(1, 5):
        paste_layer = img.new_layer('paste')
        selection = pdb.gimp_edit_paste(paste_layer, False)
        pdb.gimp_layer_translate(selection, (-base_img_width + base_img_overlap) * i, 0)
        pdb.gimp_image_merge_visible_layers(img, NORMAL_MODE)

    # Copy the background
    bg = pdb.gimp_layer_new_from_visible(background_img, img, "bg")
    pdb.gimp_image_insert_layer(img, bg, None, len(img.layers))
    pdb.gimp_layer_resize(bg, slide_size, slide_size, 0, 0)
    pdb.gimp_image_merge_visible_layers(img, NORMAL_MODE)

    # Create the frames
    for i in range(1, num_frames): # Initial layer counts as 1st layer
        frame_layer = pdb.gimp_layer_new_from_drawable(img.layers[-1], img)
        pdb.gimp_image_insert_layer(img, frame_layer, None, 0)

        # Slide
        slide_by = (i % num_slide_frames) * base_img_width / num_slide_frames
        pdb.gimp_layer_translate(frame_layer, slide_by, 0)

        # Spin
        pdb.gimp_item_transform_rotate(frame_layer, rotate_rad * i, False, slide_center, slide_center)

        pdb.gimp_layer_resize_to_image_size(frame_layer)

    # Crop the image
    offset = int((slide_size - final_img_size) / 2)
    pdb.gimp_image_resize(img, final_img_size, final_img_size, -offset, -offset)

    # Prepare the mask - put it at the bottom
    pdb.gimp_image_scale(mask_img, img.width, img.height)
    mask_layer = pdb.gimp_layer_new_from_drawable(mask_img.layers[0], img)
    pdb.gimp_image_insert_layer(img, mask_layer, None, len(img.layers))

    # Convoluted workaround to duplicate the bottom layer because GIMP doesn't
    # seem to like pasting the working mask onto the layer mask for the
    # original background
    new_bottom_layer = pdb.gimp_layer_new_from_drawable(img.layers[0], img)
    pdb.gimp_image_insert_layer(img, new_bottom_layer, None, len(img.layers) - 2)
    pdb.gimp_edit_copy(img.layers[-2])
    pasted_layer = pdb.gimp_edit_paste(img.layers[-3], False)
    pdb.gimp_floating_sel_anchor(pasted_layer)

    pdb.gimp_image_remove_layer(img, img.layers[-2]) # Remove the original bottom layer

    # Apply the mask to each frame
    num_layers = len(img.layers)
    starting_layer = num_layers - num_frames # Don't operate on mask_layer
    for i in range(starting_layer, num_layers):
        layer_idx = (num_layers - 1) - i
        layer = img.layers[layer_idx]

        # 1) Resize the layer to the image size
        pdb.gimp_layer_resize_to_image_size(layer)

        # 2) Duplicate the mask_layer to working_mask_copy
        working_mask_copy = pdb.gimp_layer_new_from_drawable(mask_layer, img)
        pdb.gimp_image_insert_layer(img, working_mask_copy, None, 0)

        # 3) Rotate working_mask_copy
        pdb.gimp_item_transform_rotate(
            working_mask_copy,
            rotate_rad * (i - starting_layer),
            True, # Auto center
            img.width / 2,
            img.height / 2
        )

        # 4) Copy working_mask_copy to the frame's layer mask
        mask = pdb.gimp_layer_create_mask(layer, ADD_MASK_BLACK)
        pdb.gimp_layer_add_mask(layer, mask)
        pdb.gimp_edit_copy(working_mask_copy)
        pasted_mask = pdb.gimp_edit_paste(mask, False)
        pdb.gimp_floating_sel_anchor(pasted_mask)

        # 5) Delete working_mask_copy
        pdb.gimp_image_remove_layer(img, img.layers[0])

    pdb.gimp_image_remove_layer(img, mask_layer)

    if generate_xcf:
        img.layers[-1].name = "Background (%ims)" % (frame_length_ms)

        for i in range(1, num_frames):
            img.layers[-(i + 1)].name = "Frame %i (%ims) (replace)" % (i + 1, frame_length_ms)

        pdb.gimp_file_save(
            img,
            img.layers[0],
            output_img_path + ".xcf",
            output_img_path + ".xcf"
        )

    for i in range(0, num_frames):
        # 6) Apply the layer mask so that the exported GIF has it
        pdb.gimp_layer_remove_mask(img.layers[-(i + 1)], MASK_APPLY)

    # Prepare image for export as GIF
    pdb.gimp_image_convert_indexed(
        img,
        NO_DITHER,
        MAKE_PALETTE,
        255,    # Number of colours
        False,  # Alpha dither
        True,   # Remove unused
        ""      # Palette
    )

    pdb.file_gif_save(
        img,
        None,               # Layer
        output_img_path,
        output_img_path,
        0,                  # Non-interlaced
        1,                  # Loop animation
        frame_length_ms,    # Default frame length
        2,                  # Default frame disposal (2 = dispose)
    )

    pdb.gimp_image_delete(img)
    pdb.gimp_image_delete(background_img)
    pdb.gimp_image_delete(mask_img)

register(
    "slide_spin",
    "Create slide-spin",
    "Create slide-spin",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Toolbox>/Plugins/Create slide-spin",
    "",
    [
        (PF_FILENAME,   "base_img_path",        "Base image",                   ""                  ),
        (PF_FILENAME,   "background_img_path",  "Background image",             ""                  ),
        (PF_FILENAME,   "mask_img_path",        "Mask image",                   ""                  ),
        (PF_FILENAME,   "output_img_path",      "Output (GIF)",                 ""                  ),
        (PF_SPINNER,    "base_img_overlap",     "Base image overlap",           20,   (1, 1000, 1)  ),
        (PF_SPINNER,    "final_img_size",       "Final image width/height",     200,  (1, 1000, 1)  ),
        (PF_SPINNER,    "num_slide_frames",     "Number of frames for slide",   8,    (8, 1000, 1)  ),
        (PF_SPINNER,    "num_frames",           "Total number of frames",       32,   (8, 1000, 1)  ),
        (PF_SPINNER,    "frame_length_ms",      "Frame length (ms)",            40,   (1, 1000, 1)  ),
        (PF_TOGGLE,     "generate_xcf",         "Generate XCF file",            False               ),
    ],
    [],
    create_slide_spin,
)

main()
