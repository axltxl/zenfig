# -*- coding: utf-8 -*-

"""
Test for: template renderer
"""

from nose.tools import raises, eq_, ok_, assert_raises
from zenfig import renderer


def test_renderer_render_dict():
    var_dict_simple = {
        "message": "{{ @{hello} }} {{ @{world} }}",
        "hello": "Hello",
        "world": "world!"
    }

    #
    r = renderer.render_dict(var_dict_simple)
    eq_(r['message'], "Hello world!")

    var_dict_second_degree = {
        "message": "{{ @{marco} }}",
        "marco": "{{ @{polo} }}",
        "polo": "Polo!"
    }

    #
    r = renderer.render_dict(var_dict_second_degree)
    eq_("Polo!", r['marco'])
    eq_("Polo!", r['message'])

    var_dict_with_filters_simple = {
        "color_hex": "{{ @{color}|norm_hex }}",
        "color": "1a1a1a"
    }

    #
    r = renderer.render_dict(var_dict_with_filters_simple)
    eq_("#1a1a1a", r['color_hex'])

    var_dict_with_filters_second_degree = {
        "message": "{{ @{another_color} }}",
        "another_color": "{{ @{color}|norm_hex }}",
        "color": "1a1a1a"
    }

    r = renderer.render_dict(var_dict_with_filters_second_degree)
    eq_("#1a1a1a", r['message'])

    # Variable resolution through filters
    # FIXME: this is the bug!
    var_dict_with_filters_third_degree = {
        "message": "{{ @{another_color} }}",
        "another_color": "{{ @{color}|norm_hex }}",
        "base_color": "1a1a1a",
        "color": "{{ @{base_color} }}"
    }

    r = renderer.render_dict(var_dict_with_filters_third_degree)
    eq_("#1a1a1a", r['message'])
