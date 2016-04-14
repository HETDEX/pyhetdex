# -*- coding: utf-8 -*-
"""
Copied from `sphinx.ext.todo`. The modification has been published on `github
<https://github.com/montefra/sphinx/tree/todo_function>`_

Allow todos to be inserted into your documentation. Inclusion of todos can
be switched of by a configuration variable. The todolist directive collects
all todos of your project and lists them along with a backlink to the
original location.

Copyright 2007-2015 by the Sphinx team, see `AUTHORS
<https://github.com/sphinx-doc/sphinx/blob/master/AUTHORS>`_.

BSD, see LICENSE for details.

.. note:: Deprecated in pyhetdex 0.5.1

    The modifications to the ``todo`` have been integrated into
    `sphinx.ext.todo <http://www.sphinx-doc.org/en/stable/ext/todo.html>`_ and
    released as part of sphinx 1.4.

    ``pyhetdex.doc.sphinxext.todo`` will be removed in future releases.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from docutils import nodes

import sphinx
from sphinx.locale import _
from sphinx.environment import NoUri
from sphinx.util.nodes import set_source_info
from sphinx.util.compat import Directive, make_admonition


class todo_node(nodes.Admonition, nodes.Element):
    pass


class todolist(nodes.General, nodes.Element):
    pass


class Todo(Directive):
    """
    A todo entry, displayed (if configured) in the form of an admonition.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        targetid = 'index-%s' % env.new_serialno('index')
        targetnode = nodes.target('', '', ids=[targetid])

        ad = make_admonition(todo_node, self.name, [_('Todo')], self.options,
                             self.content, self.lineno, self.content_offset,
                             self.block_text, self.state, self.state_machine)
        set_source_info(self, ad[0])
        return [targetnode] + ad


def process_todos(app, doctree):
    # collect all todos in the environment
    # this is not done in the directive itself because it some transformations
    # must have already been run, e.g. substitutions
    env = app.builder.env
    if not hasattr(env, 'todo_all_todos'):
        env.todo_all_todos = []
    for node in doctree.traverse(todo_node):
        try:
            targetnode = node.parent[node.parent.index(node) - 1]
            if not isinstance(targetnode, nodes.target):
                raise IndexError
        except IndexError:
            targetnode = None
        newnode = node.deepcopy()
        del newnode['ids']
        env.todo_all_todos.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'todo': newnode,
            'target': targetnode,
        })


class TodoList(Directive):
    """
    A list of all todo entries.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        # Simply insert an empty todolist node which will be replaced later
        # when process_todo_nodes is called
        return [todolist('')]


def process_todo_nodes(app, doctree, fromdocname):
    if not app.config['todo_include_todos']:
        for node in doctree.traverse(todo_node):
            node.parent.remove(node)

    # Replace all todolist nodes with a list of the collected todos.
    # Augment each todo with a backlink to the original location.
    env = app.builder.env

    if not hasattr(env, 'todo_all_todos'):
        env.todo_all_todos = []

    for node in doctree.traverse(todolist):
        if not app.config['todo_include_todos']:
            node.replace_self([])
            continue

        content = []

        for todo_info in env.todo_all_todos:
            para = nodes.paragraph(classes=['todo-source'])
            if app.config['todo_link_only']:
                description = _('<<original entry>>')
            else:
                description = _('(The <<original entry>> is located in '
                                ' %s, line %d.)') % \
                            (todo_info['source'], todo_info['lineno'])
            desc1 = description[:description.find('<<')]
            desc2 = description[description.find('>>')+2:]
            para += nodes.Text(desc1, desc1)

            # Create a reference
            newnode = nodes.reference('', '', internal=True)
            innernode = nodes.emphasis(_('original entry'),
                                       _('original entry'))
            try:
                newnode['refuri'] = app.builder.get_relative_uri(
                    fromdocname, todo_info['docname'])
                newnode['refuri'] += '#' + todo_info['target']['refid']
            except NoUri:
                # ignore if no URI can be determined, e.g. for LaTeX output
                pass
            newnode.append(innernode)
            para += newnode
            para += nodes.Text(desc2, desc2)

            # (Recursively) resolve references in the todo content
            todo_entry = todo_info['todo']
            env.resolve_references(todo_entry, todo_info['docname'],
                                   app.builder)

            # Insert into the todolist
            content.append(todo_entry)
            content.append(para)

        node.replace_self(content)


def purge_todos(app, env, docname):
    if not hasattr(env, 'todo_all_todos'):
        return
    env.todo_all_todos = [todo for todo in env.todo_all_todos
                          if todo['docname'] != docname]


def merge_info(app, env, docnames, other):
    if not hasattr(other, 'todo_all_todos'):
        return
    if not hasattr(env, 'todo_all_todos'):
        env.todo_all_todos = []
    env.todo_all_todos.extend(other.todo_all_todos)


def visit_todo_node(self, node):
    self.visit_admonition(node)


def depart_todo_node(self, node):
    self.depart_admonition(node)


def setup(app):

    import warnings

    msg = ("The module '{name}' have been deprecated and"
           " will be removed in future releases. The modifications to the"
           " ``todo`` have been integrated into sphinx.ext.todo and have"
           " been released as part of sphinx 1.4.").format(name=__name__)

    with warnings.catch_warnings():
        warnings.simplefilter("always")
        warnings.warn(msg, DeprecationWarning)

    app.add_config_value('todo_include_todos', False, 'html')
    app.add_config_value('todo_link_only', False, 'html')

    app.add_node(todolist)
    app.add_node(todo_node,
                 html=(visit_todo_node, depart_todo_node),
                 latex=(visit_todo_node, depart_todo_node),
                 text=(visit_todo_node, depart_todo_node),
                 man=(visit_todo_node, depart_todo_node),
                 texinfo=(visit_todo_node, depart_todo_node))

    app.add_directive('todo', Todo)
    app.add_directive('todolist', TodoList)
    app.connect(str('doctree-read'), process_todos)
    app.connect(str('doctree-resolved'), process_todo_nodes)
    app.connect(str('env-purge-doc'), purge_todos)
    # app.connect('env-merge-info', merge_info)
    return {'version': sphinx.__version__, 'parallel_read_safe': True}
