import numpy as np


def this_function_is_parsed(param1: int, param2: int):
    """ The same function adds two numbers.

    # Arguments:
        - param1: An int, to be summed.
        - param2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).
    
    # Return:
        - The sum of param1 and param2.

    # Example:

    ```python
    value = this_function_is_parsed(5, 7)
    ```        
    """

    return param1 + param2


def this_function_is_also_parsed(param1: int = 5, param2: int = 3):
    """ The same function as this_function_is_parsed, but with default args.

    # Arguments:
        - param1: An int, to be summed.
        - param2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).
    
    # Return:
        - The sum of param1 and param2.

    """

    return param1 + param2


def but_not_this_one(param1: int, param2: int):
    """ The same function as foo_1 from my_module_1 but with a different name.

    # Arguments:
        - param1: An int, to be summed.
        - param2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).
    
    # Return:
        - The sum of param1 and param2.

    """

    return param1 + param2
