# -*- coding: utf-8 -*-
"""
    sphinxcontrib.extcode
    ~~~~~~~~~~~~~~~~~~~~~~

    This package is a namespace package that contains all extensions
    distributed in the ``sphinx-contrib`` distribution.

    :copyright: Copyright 2007-2013 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import os
from os import path
import re

import docutils.frontend
from docutils import nodes
from docutils.utils import new_document
from docutils.parsers.rst import directives
from docutils.parsers.rst import Parser as RSTParser
from docutils.io import DocTreeInput, StringOutput
from docutils.readers.doctree import Reader as DoctreeReader
from docutils.core import Publisher, publish_doctree
from sphinx.util.nodes import set_source_info
from sphinx.util.osutil import ensuredir, copyfile
from sphinx.directives.code import CodeBlock
from sphinx.environment import SphinxStandaloneReader


BASEDIR = path.dirname(path.abspath(__file__))
STATICDIR = path.join(BASEDIR, 'static')

#FIXME: `#:` is special comment for source, but it is batting with Sphinx document comment
# I need another special comment syntax. (as like as `#<label>` )
annotation_matcher = re.compile(r'^(.*[^\s])\s*#:([^:]+):$').match


class extcode(nodes.Element):
    """Extended code-block element"""


def sandbox_rst_parser(source, source_path=None, settings_overrides=None):
    try:  #FIXME: htmlビルダー以外の場合にraiseする
        return publish_doctree(
                source=source,
                source_path=source_path,
                settings_overrides=settings_overrides)
    except:
        return None


class SandboxDoctreeReader(DoctreeReader):
    transforms = SphinxStandaloneReader.transforms

    def get_transforms(self):
        return DoctreeReader.get_transforms(self) + self.transforms


def sandbox_partial_builder(doc, env):
    from sphinx.writers.html import HTMLWriter as writer  #FIXME: need latex version or epub or...
    env.resolve_references(doc, env.docname, env.app.builder)
    pub = Publisher(
            reader=SandboxDoctreeReader(),
            writer=writer(env.app.builder),
            source=DocTreeInput(doc),
            destination_class=StringOutput,
            )
    pub.set_components(None, 'restructuredtext', None)
    defaults = env.settings.copy()
    defaults['output_encoding'] = 'unicode'
    pub.process_programmatic_settings(None, defaults, None)
    pub.set_destination(None, None)
    out = pub.publish(enable_exit_status=False)
    return pub.writer.parts['fragment']


def annotation_parser(argument):
    if argument:
        doc = sandbox_rst_parser(argument)
        if doc is not None:
            docinfo = doc[0]
            annotations = nodes.field_list()
            annotations.source, annotations.line = docinfo.source, docinfo.line
            annotations.extend(docinfo.children)
            return annotations
    return []


def rendered_block_choice(argument):
    return directives.choice(
            argument,
            ('horizonal', 'vertical', 'tab', 'toggle'))


def build_table(elements, colwidths, head_rows=0, stub_columns=0, attrs={}):
    """build_table bulid table node from elements list of list.

    :param elements:
       [[col11, col12, col13], [col21, col22, col23], ...]: col is node.
    :type elements: list of list of node
    :param heads: header line nodes
    :type heads: list of node
    :param attrs: all entry node aim attrs
    """
    cols = len(colwidths)
    table = nodes.table()
    tgroup = nodes.tgroup(cols=cols)
    table += tgroup

    #colspec
    for colwidth in colwidths:
        colspec = nodes.colspec(colwidth=colwidth)
        if stub_columns:
            colspec['stub'] = 1
            stub_columns -= 1
        tgroup += colspec

    #head
    if head_rows:
        thead = nodes.thead()
        tgroup += thead
        head_elements, elements = elements[:head_rows], elements[head_rows:]
        for heads in head_elements:
            row = nodes.row()
            for cell in heads:
                entry = nodes.entry(**attrs)
                entry += cell
                row += entry
            thead += row

    #body
    tbody = nodes.tbody()
    tgroup += tbody
    for row_cells in elements:
        row = nodes.row()
        for cell in row_cells:
            entry = nodes.entry(**attrs)
            entry += cell
            row += entry
        tbody += row

    return table


class ExtCode(CodeBlock):

    option_spec = {}
    option_spec.update(CodeBlock.option_spec)
    extra_option_spec = {
        #: display rendered reST by 'horizonal', 'vertical' or 'tab'
        'rendered-block': rendered_block_choice,
        #: annotation definitions used by field-list
        'annotations': annotation_parser,
        #: display inline annotation label
        'annotate-inline': directives.flag,
        #: display annotation ndescription table
        'annotate-block': directives.flag,
    }
    option_spec.update(extra_option_spec)

    def run(self):
        if all(opt not in self.options for opt in self.extra_option_spec):
            return super(ExtCode, self).run()  # nothing to do special

        line_annotations = {}
        annotations = self.options.get('annotations', [])
        annotationsmap = dict((k.astext(), v) for k, v in annotations)
        for i,c in enumerate(self.content):
            match = annotation_matcher(c)
            if match:
                self.content[i], label = match.groups()
                if label in annotationsmap:
                    line_annotations[i] = (label, annotationsmap[label])
                else:
                    #TODO: warning
                    line_annotations[i] = (label, None)

        # get literal from modified self.content
        literal = super(ExtCode, self).run()[0]
        # line_annotations attribute will be used for writer (not yet)
        literal['line_annotations'] = line_annotations

        wrapper = extcode(classes=['extcode'])
        set_source_info(self, wrapper)

        #check: can parse rst? and partial build?
        env = self.state.document.settings.env
        try:
            partial_doc = sandbox_rst_parser(
                    u'\n'.join(self.content),
                    env.doc2path(env.docname),
                    env.settings)
            partial_out = sandbox_partial_builder(partial_doc, env)
        except:
            env.warn(
                    env.docname,
                    u'extcode: partial build failed.',
                    lineno=self.lineno)
            partial_doc = None
            partial_out = None

        if literal['language'] == 'rst' and 'rendered-block' in self.options:
            wrapper['classes'].append(
                    'extcode-layout-' + self.options['rendered-block'])
            rendered = nodes.raw(
                    partial_out,
                    partial_out,
                    format='html',
                    classes=['extcode-rendered'])
            set_source_info(self, rendered)

            #FIXME: need translation support
            make_text = lambda t: nodes.inline(t, t)

            if self.options['rendered-block'] == 'horizonal':
                table = build_table(
                        [[make_text('literal'), make_text('rendered')],
                         [literal, rendered]],
                        [1, 1],
                        head_rows=1,
                        attrs={'classes': ['extcode-layout']})
                table.setdefault('classes', []).append('extcode-layout')
                wrapper.append(table)

            elif self.options['rendered-block'] == 'vertical':
                table = build_table(
                        [[make_text('literal'), literal],
                         [make_text('rendered'), rendered]],
                        [2, 8],
                        stub_columns=1,
                        attrs={'classes': ['extcode-layout']})
                table.setdefault('classes', []).append('extcode-layout')
                wrapper.append(table)

            else:  # toggle, tab
                wrapper.append(literal)
                wrapper.append(rendered)
        else:
            wrapper.append(literal)

        if line_annotations and 'annotate-inline' in self.options:
            prefix = '... '  #TODO prefixi customization
            contents = []
            for i in range(0, len(self.content)):
                label, value = line_annotations.get(i, ('', None))
                line = nodes.line()
                if label and value:
                    #FIXME: label and explanation need translation support
                    abbr = nodes.abbreviation(label, label)  #TODO: label customization (i.e. render with number)
                    abbr['explanation'] = value.astext()
                    line.append(nodes.inline(prefix, prefix))
                    line.append(abbr)
                elif label:
                    line.append(nodes.inline(prefix, prefix))
                    line.append(nodes.Text(label, label))
                contents.append(line)
            overlay = nodes.line_block(classes=['extcode-overlay'])
            set_source_info(self, overlay)
            overlay.extend(contents)
            wrapper.append(overlay)

        if annotations and 'annotate-block' in self.options:
            annotations['classes'] = ['extcode-annotations']
            set_source_info(self, annotations)
            wrapper.append(annotations)

        return [wrapper]


def visit_extcode_node_html(self, node):
    self.body.append(self.starttag(node, 'div'))


def depart_extcode_node_html(self, node=None):
    self.body.append('</div>\n')


def on_doctree_resolved(self, doctree, docname):
    if self.builder.name in ('singlehtml', 'html', 'epub'):
        return

    #FIXME: remove extcode nodes if not html output

    def find_extcode_removable_subnode(node):
        if (isinstance(node, nodes.compound) and
            'extcode-rendered' in node['classes']):
            return True
        if (isinstance(node, nodes.line_block) and
            'extcode-overlay' in node['classes']):
            return True
        return False

    for node in doctree.traverse(find_extcode_removable_subnode):
        node.parent.remove(node)


def on_html_coolect_pages(app):
    """on copy static files"""
    app.info(' extcode', nonl=1)
    ensuredir(path.join(app.outdir, '_static'))
    for f in os.listdir(STATICDIR):
        copyfile(
                path.join(STATICDIR, f),
                path.join(app.outdir, '_static', f))

    return []  #no pages


def setup(app):
    dummy_func = lambda *args, **kw: None
    app.add_node(extcode,
            html=(visit_extcode_node_html, depart_extcode_node_html),
            latex=(dummy_func, dummy_func),
            text=(dummy_func, dummy_func),
            man=(dummy_func, dummy_func),
            texinfo=(dummy_func, dummy_func),
            )
    app.add_directive('code-block', ExtCode)
    app.add_stylesheet('extcode.css')
    app.add_javascript('extcode.js')
    app.connect("html-collect-pages", on_html_coolect_pages)
    app.connect("doctree-resolved", on_doctree_resolved)
