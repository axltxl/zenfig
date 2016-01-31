# -*- coding: utf-8 -*-

"""
zenfig.api.color
~~~~~~~~

Utilities for color string manipulation

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import re
import webcolors

from . import _register
from . import api_entry


def _hex_check(hex_func):
    """Hexadecimal color sanity check routine"""
    def _wrapper(color):
        if re.match("^[0-9a-fA-F]*$", color):
            color = "#{}".format(color)
        return hex_func(color)
    return _wrapper

@api_entry
@_hex_check
def normalize_hex(hex_value):
    """
    Normalize a hexadecimal color value to a string
    followed by six lowercase hexadecimal digits (what
    HTML5 terms a “valid lowercase simple color”)

    :param hex_value: The hexadecimal color value to normalize.
    :returns: A normalized 6-digit hexadecimal color prepended with a #
    """

    return webcolors.normalize_hex(hex_value)

@api_entry
def normalize_rgb(rgb_triplet):
    """
    Normalize an integer rgb() triplet so that
    all values are within the range 0..255.

    :param rgb_triplet: rgb_triplet (3-tuple of int) – The integer rgb() triplet to normalize.
    :returns: 3-tuple of int
    """
    return webcolors.normalize_triplet(rgb_triplet)


@api_entry
@_hex_check
def hex_to_rgb(hex_value):
    """
    Convert a hexadecimal color value to a
    3-tuple of integers suitable for use in
    an rgb() triplet specifying that color.

    :param hex_value: The hexadecimal color to convert
    :returns: 3-tuple of int
    """
    return webcolors.hex_to_rgb(hex_value)


@api_entry
def rgb_to_hex(rgb_triplet):
    """
    Convert a 3-tuple of integers,
    suitable for use in an rgb() color triplet,
    to a normalized hexadecimal value for that color.

    :param rgb_triplet: rgb_triplet (3-tuple of int) – The integer rgb() triplet to normalize.
    :returns: Hexadecimal color
    """
    return webcolors.rgb_to_hex(hex_color)


###################################
# Register all functions on the API
###################################
_register('color_normalize_hex', normalize_hex)
_register('color_normalize_rgb', normalize_rgb)
_register('color_hex_to_rgb', hex_to_rgb)
_register('color_rgb_to_hex', rgb_to_hex)

