# -*- coding: utf-8 -*-

"""
Test for: colors API
"""

from nose.tools import raises, eq_, ok_, assert_raises
from zenfig.api import color


def test_color_normalize_hex():
    # Valid colors
    eq_(color.normalize_hex("#fff"),   "#ffffff")
    eq_(color.normalize_hex("a1a1fd"), "#a1a1fd")
    eq_(color.normalize_hex("13d4a2"), "#13d4a2")
    eq_(color.normalize_hex("fff"),    "#ffffff")

    # Invalid colors
    eq_(color.normalize_hex("ffff"),    None)
    eq_(color.normalize_hex("affffs"),  None)
    eq_(color.normalize_hex(""),        None)
    eq_(color.normalize_hex("##ffff"),  None)
    eq_(color.normalize_hex("#rfff54"), None)

    # Invalid types
    eq_(color.normalize_hex(123),  None)
    eq_(color.normalize_hex(True), None)
    eq_(color.normalize_hex(set([1,2,3])), None)

def test_color_hex_to_rgb():
    # Valid colors
    eq_(color.hex_to_rgb("#fff"),   (255, 255, 255))
    eq_(color.hex_to_rgb("a1a1fd"), (161, 161, 253))
    eq_(color.hex_to_rgb("13d4a2"), (19, 212, 162))
    eq_(color.hex_to_rgb("fff"),    (255, 255, 255))

    # Invalid colors
    eq_(color.hex_to_rgb("ffff"),    None)
    eq_(color.hex_to_rgb("affffs"),  None)
    eq_(color.hex_to_rgb(""),        None)
    eq_(color.hex_to_rgb("##ffff"),  None)
    eq_(color.hex_to_rgb("#rfff54"), None)

    # Invalid types
    eq_(color.hex_to_rgb(123),  None)
    eq_(color.hex_to_rgb(True), None)
    eq_(color.hex_to_rgb(set([1,2,3])), None)




