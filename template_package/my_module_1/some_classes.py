import numpy as np


def this_function_is_not_parsed(param_1: int, param_2: int):
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


def this_function_is_also_not_parsed(param_1: int = 5, param_2: int = 3):
    """ The same function as this_function_is_parsed, but with default args.

    # Arguments:
        - param_1: An int, to be summed.
        - param_2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).
    
    # Return:
        - The sum of param_1 and param_2.

    """

    return param_1 + param_2


def and_this_one_as_well(param_1: int, param_2: int):
    """ The same function as foo_1 from my_module_1 but with a different name.

    # Arguments:
        - param_1: An int, to be summed.
        - param_2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).
    
    # Return:
        - The sum of param_1 and param_2.

    """

    return param_1 + param_2


class TheClassNotParsed(object):
    def __init__(self):
        pass

    def method_1(self):
        pass

    def methode_2(self):
        pass


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

    def also_addition_but_with_pre_set_value(self,
                                             param_1: int = 5,
                                             param_2: int = 3):
        """ The same function as foo_1 from my_module_1 but with a different name.

        # Arguments:
            - param_1: An int, to be summed.
            - param_2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).
        
        # Return:
            - The sum of param_1 and param_2.

        """
        return param_1 + param_2


class TheClassAlsoParsed(object):
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

    def also_addition_but_with_pre_set_value(self,
                                             param_1: int = 5,
                                             param_2: int = 3):
        """ The same function as foo_1 from my_module_1 but with a different name.

        # Arguments:
            - param_1: An int, to be summed.
            - param_2: Also an int, but you could pass a float, we're not checking anything (seriously pass an int).
        
        # Return:
            - The sum of param_1 and param_2.

        """
        return param_1 + param_2
