import re
import inspect
import os
from os.path import dirname
import shutil
import argparse
import types 

from importlib import import_module

# The functions to exclude from the documentation, it is faster to give one to
# avoid out of ten than the opposite.
EXCLUDE = {}

# Adding the import relative to the documentation

# Here define what is to be parsed
PAGES = []

# The root path of the gitlab
ROOT = ''

# The existing tags for the parsing of the source files are :
#   - detailled_classes: will details the class/es as well as the available
#     methods inside the class
#   - all_module_functions: will details all the function in a module
#   - all_module_classes: will details all the functions in a module
#   - functions: will details the functions specified

def get_function_signature(function, method=True):
    """ Return the signature of a function. """
    wrapped = getattr(function, '_original_function', None)
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
    return signature


def get_class_signature(cls):
    """ Get the signature of a class. 
    
    # Argument
        cls: The class to get the signature from.

    # Return
        A string with the signature of the class. The __init__ function is actually parsed.
    """
    try:
        class_signature = get_function_signature(cls.__init__)
        class_signature = class_signature.replace('__init__', cls.__name__)
    except (TypeError, AttributeError):
        # in case the class inherits from object and does not
        # define __init__
        class_signature = cls.__module__ + '.' + cls.__name__ + '()'
    return class_signature


def class_to_docs_link(cls):
    module_name = cls.__module__
    assert module_name[:6] == 'keras.'
    module_name = module_name[6:]
    link = ROOT + module_name.replace('.', '/') + '#' + cls.__name__.lower()
    return link


def class_to_source_link(cls):
    """ Create a link to thesource of the class. 
    
    # Argument
        cls: The target class.
    
    # Return
        A string in markdown format with a link to the class
    """
    module_name = cls.__module__
    path = module_name.replace('.', '/')
    path += '.py'
    line = inspect.getsourcelines(cls)[-1]
    link = ('' + path + '#L' + str(line))
    return '[[source]](' + link + ')'


def code_snippet(snippet):
    """ Function to add the python code descriptor of a markdown file.
    
    # Argument
        snippet: The string to put inside the code descriptor.

    # Return
        The snippet formated to the correct format.
    """
    result = '```python\n'
    result += snippet + '\n'
    result += '```\n'
    return result

def process_docstring(docstring):
    """ Process the docstring extrated from the object to parse.

    # Argument
        docstring: The docstring to process.
    
    # Return
        The processed docstring to be readable in a markdown format.
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
    """ Parse the dicumentation of the provided function.
    
    # Arguments
        function: The function to be parsed.
        indentation: What to append in front of the definition of the parsed function. Something like '###'.
    
    # Return
        A string containing the documentation of the parsed function.
    """
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
    """ Parse the class, the member functions are not parsed by this function. 
    
    # Arguments
        cls: The class to be parsed.
        indentation: The string to put in front of the class name ('##').
    
    # Return
        The parsed class, with the potential docstring.
    """
    subblock = []
    signature = get_class_signature(cls)
    subblock.append('<span style="float:right;">' + class_to_source_link(cls) + '</span>')
    subblock.append(indentation + ' ' + cls.__name__ + '\n')
    subblock.append(code_snippet(signature))
    docstring = cls.__doc__
    if docstring:
        subblock.append(process_docstring(docstring))
    return subblock

def parse_detailled_classes(to_be_detailled):
    """ Parse the to_be_detailled (a list of classes) and return a block with the corresponding documentation.

    # Arguments
        to_be_detailled: A list with all the classes to be detailled.

    # Return
        A string (block) with the documentation to be written.
    """
    blocks = []
    for detailled_class in to_be_detailled:
        modules = detailled_class.split('.')
        detailled_class = ''
        for module_iterator in range(len(modules) - 1):
            detailled_class += modules[module_iterator]
            detailled_class += '.'
        detailled_class = detailled_class[:-1]
        detailled_class = __import__(detailled_class)
        detailled_class = getattr(detailled_class, modules[-1])
        subblock = parse_class(detailled_class, '##')
        blocks.append('\n\n'.join(subblock))
        for function in inspect.getmembers(detailled_class):
            # Ignoring the private functions
            if function[0][0] == '_':
                continue
            if type(function[1]) == types.FunctionType:
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
        module = import_module(module)
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
    """ Parse all the function given in the entry argument.
    
    # Argument
        to_be_detailled: A list containing all the function to be detailled. The function objects are to be given here.
    
    # Return
        A string with all the documentation for each functions.
    """
    blocks = []
    for function in to_be_detailled:
        modules = function.split('.')
        function = ''
        for module_iterator in range(len(modules) - 1):
            function += modules[module_iterator]
            function += '.'
        function = function[:-1]
        function = __import__(function)
        print(function)
        function = getattr(function, modules[-1])
        subblocks = parse_function(function, '### ')
        blocks.append('\n\n'.join(subblocks))
    return '\n***\n\n'.join(blocks)

def fill_page(path, autogenerated_blocks):
    """ Open a file and replace the {{autogenerated}} text with what is inside the autogenerated_blocks list.
    Assert that the number of autogenerated_blocks is the same as the number of {{autogenerated}} tags.

    # Arguments
        path: Path to the file to write inside the template directory.
        autogenerated_blocks: A list with the autogenerated blocks of text to be written.

    # Return
        A string with all data inside autogenerated_blocks written in it. If there is no existing file at path, simply return the concatenated the blocks.
    """

    # First let's check if we have the correct number of tags for the length of our array.
    path = os.path.join('templates', page_name)
    if os.path.exists(path):
        with open(path) as f:
            mkdown = f.read()
            autogenerated_number = mkdown.count('{{autogenerated}}')
            assert autogenerated_number == len(autogenerated_blocks), ('Template found for ' + path + ' but there is {} {{autogenerated}} tag for {} entries in the array in PAGES.'.format(autogenerated_number, len(autogenerated_blocks)))
            # Filling the page
            for autogenerated_block in autogenerated_blocks:
                mkdown = mkdown.replace('{{autogenerated}}', autogenerated_block,1)
            return mkdown
    else:
        return '\n***\n\n'.join(autogenerated_blocks)

def clean_directories():
    """ Clean the output directories. The new generated files will be saved into the cleaned directories. """
    print('Cleaning up existing sources directory.')
    if os.path.exists('sources'):
        shutil.rmtree('sources')

def load_templates():
    """ Load the templates files, before parsing the functions from the modules. """
    print('Populating sources directory with templates.')
    for subdir, _, fnames in os.walk('templates'):
        new_subdir = subdir.replace('templates', 'sources')
        if not os.path.exists(new_subdir):
            os.makedirs(new_subdir)
        for fname in fnames:
            if fname[-3:] == '.md':
                fpath = os.path.join(subdir, fname)
                new_fpath = fpath.replace('templates', 'sources')
                shutil.copy(fpath, new_fpath)

def load_project_read_me():
    """ Loads the project README file and load it into the main index file. An {{autogenerated}} tag should be present. """
    with open('../README.md') as readme:
        readme = readme.read()
        with open('templates/index.md') as index:
            index = index.read()
            index = index.replace('{{autogenerated}}', readme)
            with open('sources/index.md', 'w') as source_index:
                source_index.write(index)


if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-pr", "--projectReadMe", help="If the project read me should be load inside the main index file. Default is False.", default=False)
    args = parser.parse_args()

    clean_directories()
    load_templates()
    if args.projectReadMe:
        load_project_read_me()

    # Now that we have loaded all the files, we load the data from the modules.
    print('Starting autogeneration.')
    for page_data in PAGES:
        autogenerated_blocks = []
        page_name = page_data['page']
        path = os.path.join('sources', page_name)

        # We extract the corresponding data for each existing tag.
        for tag, to_be_detailled in page_data['autogenerated']:
            if tag == 'detailled_classes':
                block = parse_detailled_classes(to_be_detailled)
            elif tag == 'all_module_functions':
                block = parse_all_module_functions(to_be_detailled)
            elif tag == 'functions':
                block = parse_functions(to_be_detailled)
            else:
                block = ''

            # We append the generated documentation.
            autogenerated_blocks.append(block)
            
        # We fill the documentation page with the generated documentation
        to_write = fill_page(page_name, autogenerated_blocks)

        # Make the directory to write the file to if it is not already existing.
        subdir = os.path.dirname(path)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        # Write the file
        print("Filling file : {}".format(path))
        open(path, 'w').write(to_write)