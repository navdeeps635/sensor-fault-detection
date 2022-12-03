from setuptools import find_packages,setup

from typing import List

requirement_file_name = 'requirements.txt'
e_dot = '-e .' 
def get_requirements(): # will return list of libraries mentioned in requirements.txt
    
    with open(requirement_file_name) as requirement_file:
        requirement_list = requirement_file.readlines()
    requirement_list = [requirement_name.replace('\n','') for requirement_name in requirement_list]
    
    if e_dot in requirement_list:
        requirement_list.remove(e_dot)
    return requirement_list
        
setup(
    name='sensor',
    version='0.0.1',
    author='Navdeep Singh',
    author_email='navdeep3135@gmail.com',
    packages=find_packages(),
    install_requires = get_requirements()
)