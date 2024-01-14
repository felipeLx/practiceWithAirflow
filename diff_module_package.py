"""Module vs Package vs Library"""

# module
def square(number):
    """Function square number"""
    return number ** 2

# you can import like
    # from my_module import square
    

# package
# package is a collection of modules into a dictionary-like structure
    """
    myproject
    myproject/__init__.py
    myproject/my_module1.py
    myproject/my_module2.py
    """

# Important: when you import a module or a package, the corresponding object created by Python is always a type module.

# library
# a collection of packages or a single package
    """
    myproject
    myproject/__init__.py
    myproject/my_package1/__init__.py
    myproject/my_package1/my_module1.py
    myproject/my_package1/my_module2.py
    myproject/my_package2/__init__.py
    myproject/my_package2/my_module1.py
    myproject/my_package2/my_module2.py
    """
    
# Creating a package
    """
    module1.py
    def square(number):
        return number ** 2
    
    module2.py
    def mean(numbers):
        return sum(numbers) / len(numbers)
    
    to make my_project folder into a package, you must have __init__.py as a file in the my_project folder
    __init__.py
    from . import module1
    from . import module2
    """