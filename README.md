# Python Documentation Project

This was taken from the Keras github and then modified a bit to make it more modular, they have a nice tool for auto-documentation generation but as far as I know they use it only for their project and it cannot be used on other project.

This is intended to be used with Mkdocs.

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
mkdocs serve

```

Once you are done with the above commands, simply open in your browser the following [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Making its own documentation

This was build to generate documentation as easily as possible. Simply create the docs directory in your project, copy the autogen.py file and modify it to your needs and run the commands as in [Generating the documentation](##Generating-the-documentation).

### Supported generation modes

The module supports various type of generation for the documentation.

### Generating the main page of the documentation

By default, the autogen.py script will look for the README.md file in the above folder of "docs". It will load this file and try to replace any "{{autogenerated}}"
tag in the "index.md" file in the template folder of "docs". To prevent this behavior, simply do not use the "{{autogenerated}}" tag in the "index.md" file.

### Documenting the code

```python

```

## TO DO

Things to do:

- finalize readme
