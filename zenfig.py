import jinja2
import yaml
import sys
import os
import re

########################################################
# zenfig [ -I <variable file/directory> ... ] [ -o <rendered file> ]<template>
########################################################

# read yaml file and get variables from it
file_name = sys.argv[1]
if not re.match(".*\.yml$", file_name):
    file_name = "{}.yml".format(file_name)
with open(file_name, "r") as file:
    tpl_vars = yaml.load(file)

# load template environment
tpl_loader = jinja2.FileSystemLoader(os.getcwd())

# everything begins with a jinja environment
tpl_env = jinja2.Environment(
        loader=tpl_loader,
        trim_blocks=True
        )
def hello():
    return "Hoooooooola!"
tpl_env.globals['hello'] = hello

# load the template
tpl_file = "hello.jinja"
tpl = tpl_env.get_template(tpl_file)

# render template to stdout
print (tpl.render(**tpl_vars))

