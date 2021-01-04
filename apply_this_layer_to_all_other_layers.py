#! /usr/bin/env python
from math import pi
from gimpfu import *
import gtk

pdb = gimp.pdb

def apply_this_layer_to_all_other_layers(img, layer_to_apply, apply_above, apply_as_mask):
    for i in range(0, len(img.layers)):
        layer = img.layers[i]

        if layer == layer_to_apply:
            pass
        else:
            if apply_as_mask:
                mask = pdb.gimp_layer_get_mask(layer)

                if mask is None:
                    mask = pdb.gimp_layer_create_mask(layer, ADD_MASK_BLACK)
                    pdb.gimp_layer_add_mask(layer, mask)

                pdb.gimp_edit_copy(layer_to_apply)
                pasted_mask = pdb.gimp_edit_paste(mask, False)
                pdb.gimp_floating_sel_anchor(pasted_mask)
            else:
                applied_layer = pdb.gimp_layer_new_from_drawable(layer_to_apply, img)

                if apply_above:
                    pdb.gimp_image_insert_layer(img, applied_layer, None, i)
                    pdb.gimp_image_merge_down(img, applied_layer, CLIP_TO_IMAGE)
                else:
                    pdb.gimp_image_insert_layer(img, applied_layer, None, i + 1)
                    pdb.gimp_image_merge_down(img, layer, CLIP_TO_IMAGE)

register(
    "apply_this_layer_to_all_other_layers",
    "Apply this layer to all other layers",
    "Apply this layer to all other layers",
    "atomicparade",
    "atomicparade",
    "January 2021",
    "<Image>/Filters/Animation/Apply this layer to all other layers",
    "*",
    [
        (PF_TOGGLE, "apply_above",      "Apply above",                                      True    ),
        (PF_TOGGLE, "apply_as_mask",    "Apply as mask (will replace any existing masks)",  False   ),
    ],
    [],
    apply_this_layer_to_all_other_layers,
)

main()
