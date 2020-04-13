# Python Documentation Project

This was taken from the Keras github and then modified a bit to make it more modular, they have a nice tool for auto-documentation generation but as far as I know they use it only for their project and it cannot be used on other project.

This is intended to be used with Mkdocs. The example in this repo should be enough to get you started.

## Generating the documentation

A fully working example is provided. We run it local for more simplicity, but the generated doc can be hosted anywere.

This exemple relies on the following python packages:

- numpy

To generate the documentation for the example, run the following commands:

```bash
mkdir .venv
cd .venv

python3 -m venv pythondoc

source pythondoc/bin/activate

cd ..

# Install mkdocs (to run it locally for the example)
pip install mkdocs

# Install the dependencies of your project
pip install numpy

# Generate the documentation
cd docs
python autogen.py

# Run the documentation server
cd ..
mkdocs serve

```

Once you are done with the above commands, simply open in your browser the following [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Making its own documentation

This was build to generate documentation as easily as possible. Simply create the docs directory in your project, copy the autogen.py file and modify the variable at the beginning to your needs and run the commands as in [Generating the documentation](##Generating-the-documentation). You also need to create your own [mkdocs.yml](mkdocs.yml) file to create your documentation tree.

The main parts to modify are the following ones:

- PAGES, used to define the mode to use for each of the modules, you can define multiple mode per module.
- git_path, is the root of your github repo, this is used to set up the links to your code from the documentation

You'll also want to generate dummy templates with a title for each of the pages of the documentation as it provides with a better formatting.

### Supported generation modes

The module supports various type of generation for the documentation:

- all_functions_module: will details all the function in a module
- all_classes_module: will details all the functions in a module
- classes: will details the class/es as well as the available methods inside the class
- functions: will detail the functions specified

Take a look at the autogen.py file, the "PAGES" array is used to define the mode you wish to use.

```python
PAGES = [{
    'page': 'path_to_my_page.md',
    'autogenerated': [['mode', [list_of_modules/functions/classes]]]
}, {
    'page':
    'my_module_1/some_functions.md',
    'autogenerated': [[
        'functions',
        [
            my_module_1.this_function_is_parsed,
            my_module_1.this_function_is_also_parsed
        ]
    ]]
}]
```

You can have multiple mode for the autogenerated list, each of the {{autegenerated}} tags in the templates will be fill with the generated documentation.

### Generating the main page of the documentation

By default, the autogen.py script will look for the README.md file in the above folder of "docs". It will load this file and try to replace any "{{autogenerated}}"
tag in the "index.md" file in the template folder of "docs". To prevent this behavior, simply do not use the "{{autogenerated}}" tag in the "index.md" file.

### Documenting the code

The documentation follow the simple schemes define hereafter:

```python
# Documenting function, hinting and default are supported.
# You can add any section using the # tag.
def this_function_is_parsed(param_1: int, param_2: int, *args, **kwargs):
    """ The same function adds two numbers.

    # Arguments:
        - param_1: An int, to be summed.
        - param_2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).

    # Return:
        - The sum of param_1 and param_2.

    # Example:

    ```python
    value = this_function_is_parsed(5, 7)
    ```
    """

    return param_1 + param_2

# Documenting class, the main documentation for the class uses the __init__ function.
class TheClassParsed(object):
    def __init__(self, init_1: float, init_2: str = "value"):
        """ The init function of the class, used to describe the class.

        # Arguments:
            - init_1: The first init parameter.
            - init_2: The second init parameter.
        """
        self.init_1 = init_1
        self.init_2 = init_2

    def addition(self, param_1: int, param_2: int):
        """ The same function as foo_1 from my_module_1 but with a different name.

        # Arguments:
            - param_1: An int, to be summed.
            - param_2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).

        # Return:
            - The sum of param_1 and param_2.

        """
        return param_1 + param_2
```
