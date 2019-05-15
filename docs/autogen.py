from __future__ import unicode_literals

import re
import inspect
import os
import shutil

import sys
sys.path.append('..')

from template_package import my_module_1
from template_package import my_module_2

# The functions to exclude from the documentation, it is faster to give one to
# avoid out of ten than the opposite.
EXCLUDE = {}

# The existing tags for the parsing of the source files are :
#   - detailled_classes: will details the class/es as well as the available
#     methods inside the class
#   - all_module_functions: will details all the function in a module
#   - all_module_classes: will details all the functions in a module
#   - functions: will details the functions specified

PAGES = [
    {
        'page': 'my_module_1/some_functions.md',
        'autogenerated': [
            ['functions', [my_module_1.this_function_is_parsed, my_module_1.this_function_is_also_parsed]]
        ]
    },{
        'page': 'my_module_2/all_module_functions.md',
        'autogenerated': [
            ['functions', [my_module_1.this_function_is_parsed, my_module_1.this_function_is_also_parsed]]
        ]
    },{
        'page': 'my_module_2/all_module_classes.md',
        'autogenerated': [
            ['functions', [my_module_1.this_function_is_parsed, my_module_1.this_function_is_also_parsed]]
        ]
    },{
        'page': 'my_module_2/detailled_classes.md',
        'autogenerated': [
            ['functions', [my_module_1.this_function_is_parsed, my_module_1.this_function_is_also_parsed]]
        ]
    }
]

# The root path of the gitlab
ROOT = 'https://github.com/D3lt4lph4/pythondoc'


def get_function_signature(function, method=True):
    wrapped = getattr(function,
                      '_original_function',
                      None)
    if wrapped is None:
        signature = inspect.getargspec(function)
    else:
        signature = inspect.getargspec(wrapped)
    defaults = signature.defaults
    if method:
        args = signature.args[1:]
    else:
        args = signature.args
    if defaults:
        kwargs = zip(args[-len(defaults):], defaults)
        args = args[:-len(defaults)]
    else:
        kwargs = []
    st = '%s.%s(' % (function.__module__, function.__name__)

    for a in args:
        st += str(a) + ', '
    for a, v in kwargs:
        if isinstance(v, str):
            v = '\'' + v + '\''
        st += str(a) + '=' + str(v) + ', '
    if kwargs or args:
        signature = st[:-2] + ')'
    else:
        signature = st + ')'

    if not method:
        # Prepend the module name.
        signature = function.__module__ + '.' + signature
    return post_process_signature(signature)


def get_class_signature(cls):
    try:
        class_signature = get_function_signature(cls.__init__)
        class_signature = class_signature.replace('__init__', cls.__name__)
    except (TypeError, AttributeError):
        # in case the class inherits from object and does not
        # define __init__
        class_signature = cls.__module__ + '.' + cls.__name__ + '()'
    return post_process_signature(class_signature)


def post_process_signature(signature):
    parts = re.split('\.(?!\d)', signature)
    if len(parts) >= 4:
        if parts[1] == 'layers':
            signature = 'keras.layers.' + '.'.join(parts[3:])
        if parts[1] == 'utils':
            signature = 'keras.utils.' + '.'.join(parts[3:])
        if parts[1] == 'backend':
            signature = 'keras.backend.' + '.'.join(parts[3:])
    return signature


def class_to_docs_link(cls):
    module_name = cls.__module__
    assert module_name[:6] == 'keras.'
    module_name = module_name[6:]
    link = ROOT + module_name.replace('.', '/') + '#' + cls.__name__.lower()
    return link


def class_to_source_link(cls):
    module_name = cls.__module__
    path = module_name.replace('.', '/')
    path += '.py'
    line = inspect.getsourcelines(cls)[-1]
    link = ('https://github.com/D3lt4lph4/pythondoc/tree/master/' + path + '#L' + str(line))
    return '[[source]](' + link + ')'


def code_snippet(snippet):
    result = '```python\n'
    result += snippet + '\n'
    result += '```\n'
    return result


def count_leading_spaces(s):
    ws = re.search('\S', s)
    if ws:
        return ws.start()
    else:
        return 0


def process_docstring(docstring):
    """ Process the docstring extrated from the object to parse.



    """
    # First, extract code blocks and process them.
    code_blocks = []
    if '```' in docstring:
        tmp = docstring[:]
        while '```' in tmp:
            tmp = tmp[tmp.find('```'):]
            index = tmp[3:].find('```') + 6
            snippet = tmp[:index]
            # Place marker in docstring for later reinjection.
            docstring = docstring.replace(snippet, '$CODE_BLOCK_%d' % len(code_blocks))
            snippet_lines = snippet.split('\n')
            # Remove leading and trailing spaces.
            num_leading_spaces = snippet_lines[-1].find('`')
            snippet_lines = ([snippet_lines[0]] + [line[4:].rstrip() for line in snippet_lines[1:]])
            snippet_lines[-1] = snippet_lines[-1].strip()

            snippet = '\n'.join(snippet_lines)
            code_blocks.append(snippet)
            tmp = tmp[index:]

    # Format docstring section titles.
    docstring = re.sub(r'\n(\s+)# (.*)\n', r'\n\1__\2__\n\n', docstring)
    # Format docstring lists.
    docstring = re.sub(r'([a-z\_]+):(.*)\n', r'- __\1__:\2\n', docstring)
    # Strip all leading spaces.
    lines = docstring.split('\n')
    docstring = '\n'.join([line.lstrip(' ') for line in lines])

    # Reinject code blocks.
    for i, code_block in enumerate(code_blocks):
        docstring = docstring.replace('$CODE_BLOCK_%d' % i, code_block)

    return docstring


def parse_function(function, indentation):
    subblock = []
    signature = get_function_signature(function, method=False)
    signature = signature.replace(function.__module__ + '.', '')
    subblock.append(indentation + ' ' + function.__name__ + '\n')
    subblock.append(code_snippet(signature))
    docstring = function.__doc__
    if docstring:
        subblock.append(process_docstring(docstring))
    return subblock


def parse_class(cls, indentation):
    subblock = []
    signature = get_class_signature(cls)
    subblock.append('<span style="float:right;">' + class_to_source_link(cls) + '</span>')
    subblock.append(indentation + ' ' + cls.__name__ + '\n')
    subblock.append(code_snippet(signature))
    docstring = cls.__doc__
    if docstring:
        subblock.append(process_docstring(docstring))
    return subblock


def initialize():
    """ First function ran in main, used to initialize the architecture of the documentation."""

    print('Cleaning up existing sources directory.')
    if os.path.exists('sources'):
        shutil.rmtree('sources')

    print('Populating sources directory with templates.')
    for subdir, dirs, fnames in os.walk('templates'):
        new_subdir = subdir.replace('templates', 'sources')
        if not os.path.exists(new_subdir):
            os.makedirs(new_subdir)
        for fname in fnames:
            if fname[-3:] == '.md':
                fpath = os.path.join(subdir, fname)
                new_fpath = fpath.replace('templates', 'sources')
                shutil.copy(fpath, new_fpath)

    # Initialize the index page with the README from the root directory
    readme = open('../README.md').read()
    index = open('templates/index.md').read()
    index = index.replace('{{autogenerated}}', readme)
    f = open('sources/index.md', 'w')
    f.write(index)
    f.close()


def fill_page(path, autogenerated_blocks):
    """ Open a file and replace the {{autogenerated}} text with what is inside the autogenerated_blocks list.

    # Arguments
        path: Path to the file to write.
        autogenerated_blocks: A list with the bunch of texts to be written.

    # Return
        A string with all data inside autogenerated_blocks written in it.
    """

    # First let's check if we have the correct number of tags for the length of our array.
    path = os.path.join('templates', page_name)
    if os.path.exists(path):
        with open(path) as f:
            mkdown = f.read()
            autogenerated_number = template.count('{{autogenerated}}')
            assert autogenerated_number == len(page_data['autogenerated']), (
                        'Template found for ' + path + ' but there is {} {{autogenerated}} tag for {} entries in the array in PAGES.'.format(
                    autogenerated_number, len(page_data['autogenerated'])))
            # Filling the page
            for autogenerated_block in autogenerated_blocks:
                mkdown = mkdown.replace('{{autogenerated}}', autogenerated_block, 1)
            return mkdown
    else:
        return '\n***\n\n'.join(autogenerated_blocks)

    return to_write


def parse_detailled_classes(to_be_detailled):
    """ Parse the to_be_detailled (a list of classes) and return a block with the corresponding documentation.

    # Arguments
        to_be_detailled: A list with all the classes to be detailled.

    # Return
        A string (block) with the documentation to be written.
    """
    blocks = []
    for detailled_class in to_be_detailled:
        subblock = parse_class(detailled_class, '##')
        blocks.append('\n\n'.join(subblock))
        for function in inspect.getmembers(detailled_class):
            # Ignoring the private functions
            if function[0][0] == '_':
                continue
            # Ignoring the properties
            if isinstance(function[1], property):
                continue
            subblock = parse_function(function[1], '###')
            blocks.append('\n\n'.join(subblock))
    return '\n***\n\n'.join(blocks)


def parse_all_module_functions(to_be_detailled):
    """ Parse the to_be_detailled (a module) and return a block with the corresponding documentation.

    # Arguments
        to_be_detailled: A list, the module to be detailled.

    # Return
        A string (block) with the documentation to be written.
    """
    for module in to_be_detailled:
        blocks = []
        for name in dir(module):
            if name[0] == '_' or name in EXCLUDE:
                continue
            module_member = getattr(module, name)
            if inspect.isfunction(module_member):
                function = module_member
                if module.__name__ in function.__module__:
                    subblocks = parse_function(function, '### ')
                    blocks.append('\n\n'.join(subblocks))
    return '\n***\n\n'.join(blocks)


def parse_functions(to_be_detailled):
    blocks = []
    for function in to_be_detailled:
        subblocks = parse_function(function, '### ')
        blocks.append('\n\n'.join(subblocks))
    return '\n***\n\n'.join(blocks)


if __name__ == '__main__':

    initialize()

    print('Starting autogeneration.')
    for page_data in PAGES:
        autogenerated_blocks = []
        # First we check for the .md file to have the same number of '{{autogenerated}}' as we have entries in the page data. If the page is non-existing we generate a new one.
        page_name = page_data['page']
        path = os.path.join('sources', page_name)
        if os.path.exists(path):
            with open(path) as f:
                template = f.read()
                autogenerated_number = template.count('{{autogenerated}}')
                assert autogenerated_number == len(page_data['autogenerated']), (
                            'Template found for ' + path + ' but there is {} {{autogenerated}} tag for {} entries in the array in PAGES.'.format(
                        autogenerated_number, len(page_data['autogenerated'])))

        # We extract the corresponding data for each existing tag.
        for tag, to_be_detailled in page_data['autogenerated']:
            if tag == 'detailled_classes':
                block = parse_detailled_classes(to_be_detailled)
            elif tag == 'all_module_functions':
                block = parse_all_module_functions(to_be_detailled)
            elif tag == 'functions':
                block = parse_functions(to_be_detailled)

            # We happen the generated documentation.

            autogenerated_blocks.append(block)
        # We fill the documentation page with the generated documentation
        to_write = fill_page(page_name, autogenerated_blocks)

        # Make the directory to write the file to if it does not already existing.
        subdir = os.path.dirname(path)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        # Write the file
        print("Filling file : {}".format(path))
        open(path, 'w').write(to_write)
