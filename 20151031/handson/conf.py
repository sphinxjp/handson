#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'ext')

extensions = ['extcode']
source_suffix = '.rst'
master_doc = 'index'

project = 'handson'
copyright = '2015, sphinx-users.jp'
author = 'sphinx-users.jp'

version = release = '1.0'
language = 'ja'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'bizstyle'
html_logo = 'logo.jpg'



