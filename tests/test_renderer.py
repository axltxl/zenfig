# -*- coding: utf-8 -*-

"""
Test for: template renderer
"""

from nose.tools import raises, eq_, ok_, assert_raises
from zenfig import renderer
from zenfig.depgraph import DepGraphException


def test_renderer_render_dict():
    ############################
    # Simple variable resolution
    ############################
    var_dict_simple = {
        "message": "{{ @hello }} {{ @world }}",
        "hello": "Hello",
        "world": "world!"
    }
    r = renderer.render_dict(**var_dict_simple)
    eq_(r['message'], "Hello world!")

    var_dict_second_degree = {
        "message": "{{ @marco }}",
        "marco": "{{ @polo }}",
        "polo": "Polo!"
    }
    r = renderer.render_dict(**var_dict_second_degree)
    eq_("Polo!", r['marco'])
    eq_("Polo!", r['message'])

    #####################################
    # Variable resolution through filters
    #####################################
    var_dict_with_filters_simple = {
        "color_hex": "{{ @color|norm_hex }}",
        "color": "1a1a1a",
        "somenum": 1
    }
    r = renderer.render_dict(**var_dict_with_filters_simple)
    eq_("#1a1a1a", r['color_hex'])

    var_dict_with_filters_second_degree = {
        "message": "{{ @another_color }}",
        "another_color": "{{ @color|norm_hex }}",
        "color": "1a1a1a",
        "somenum": 1
    }
    r = renderer.render_dict(**var_dict_with_filters_second_degree)
    eq_("#1a1a1a", r['message'])

    var_dict_with_filters_third_degree = {
        "message": "{{ @another_color }}",
        "another_color": "{{ @color|norm_hex }}",
        "base_color": "1a1a1a",
        "color": "{{ @base_color }}",
        "somenum": 1
    }
    r = renderer.render_dict(**var_dict_with_filters_third_degree)
    eq_("#1a1a1a", r['message'])

    # a variable reference within a dictionary
    var_with_dict = {
        "hello": "world",
        "iamdict": {
            "hi": "{{ @hello }}",
            "there": 1,
            "somebol": True
        }
    }
    r = renderer.render_dict(**var_with_dict)
    eq_("world", r['iamdict']['hi'])

    # a variable reference within a list
    var_with_list = {
        "hello": "world",
        "iamlist": [
            "{{ @hello }}",
            1, 2, True
        ]
    }
    r = renderer.render_dict(**var_with_list)
    eq_("world", r['iamlist'][0])

    # circular dependency detection
    var_circ_dep = {
        "nowimthere": "{{ @hello }}",
        "nowimhere": "{{ @nowimthere }}",
        "hello": "{{ @nowimhere }}",
        "iamlist": [
            "{{ @hello }}",
            1, 2, True
        ]
    }
    assert_raises(DepGraphException, renderer.render_dict, **var_circ_dep)

    # a variable that references itself indirectly
    var_circ_dep = {
        "nowimthere": "{{ @hello }}",
        "nowimhere": "{{ @nowimthere }}",
        "hello": "{{ @nowimhere }}",
    }
    assert_raises(DepGraphException, renderer.render_dict, **var_circ_dep)

    # a variable that references itself directly
    var_circ_dep = {
        "hello": "{{ @hello }}",
    }
    assert_raises(DepGraphException, renderer.render_dict, **var_circ_dep)
