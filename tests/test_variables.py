# -*- coding: utf-8 -*-

"""
Test for: variables module
"""

from nose.tools import raises, eq_, ok_, assert_raises
from zenfig.api import color

from zenfig import variables

def test_get_vars_from_env():
    correct_paths = [
        ("/home", ['/home']),
        ("hello there:i 4m a p4th", ['hello there', 'i 4m a p4th']),
        ("hello:asdf:fsd", ['hello', 'asdf', 'fsd'])
    ]
    incorrect_paths = [
        ":asdf",
        "hello:there:",
        "hello:there::yo"
        ""
    ]

    for path, result in correct_paths:
        eq_(variables._get_vars_from_env(path), result)
    for path in incorrect_paths:
        eq_(variables._get_vars_from_env(path), None)
