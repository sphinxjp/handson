# -*- coding: utf-8 -*-

import sys, os

extensions = ['sphinx.ext.todo', 'sphinxjp.themecore']
html_static_path = ['_static']
source_suffix = '.rst'
master_doc = 'index'
project = u'Sphinx Hands-on 2015.10'
copyright = u'2015, Sphinx-users.jp'
version = release = '1.0'

exclude_patterns = ['_build']

pygments_style = 'sphinx'
html_theme = 's6'
html_use_index = False

def setup(app):
    app.add_stylesheet('custom.css')
