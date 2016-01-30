# -*- coding: utf-8 -*-

"""
Test for: colors API
"""

from nose.tools import raises, eq_, ok_, assert_raises
from zenfig.api import color


def test_color_hex_normalize():
    # Valid colors
    eq_(color.hex_normalize("#fff"),   "#ffffff")
    eq_(color.hex_normalize("a1a1fd"), "#a1a1fd")
    eq_(color.hex_normalize("13d4a2"), "#13d4a2")
    eq_(color.hex_normalize("fff"),    "#ffffff")

    # Invalid colors
    eq_(color.hex_normalize("ffff"),    None)
    eq_(color.hex_normalize("affffs"),    None)
    eq_(color.hex_normalize(""),    None)
    eq_(color.hex_normalize("##ffff"),  None)
    eq_(color.hex_normalize("#rfff54"), None)

    # Invalid types
    eq_(color.hex_normalize(123), None)
    eq_(color.hex_normalize(True), None)
    eq_(color.hex_normalize(set([1,2,3])), None)

def test_color_hex_to_rgb():
    # Valid colors
    eq_(color.hex_to_rgb("#fff"),   (255, 255, 255))
    eq_(color.hex_to_rgb("a1a1fd"), (161, 161, 253))
    eq_(color.hex_to_rgb("13d4a2"), (19, 212, 162))
    eq_(color.hex_to_rgb("fff"),    (255, 255, 255))

    # Invalid colors
    eq_(color.hex_to_rgb("ffff"),    None)
    eq_(color.hex_to_rgb("affffs"),    None)
    eq_(color.hex_to_rgb(""),    None)
    eq_(color.hex_to_rgb("##ffff"),  None)
    eq_(color.hex_to_rgb("#rfff54"), None)

    # Invalid types
    eq_(color.hex_to_rgb(123), None)
    eq_(color.hex_to_rgb(True), None)
    eq_(color.hex_to_rgb(set([1,2,3])), None)




