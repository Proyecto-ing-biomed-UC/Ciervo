from setuptools import setup, find_packages
import os


VERSION = os.getenv('VERSION')
DESCRIPTION = 'Ciervo for prosthetic leg control'
LONG_DESCRIPTION = 'First version'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="ciervo", 
        version=VERSION,
        author="Carlos Valle",
        author_email="cgvallea@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            # Linux
            "Operating System :: POSIX :: Linux",
        ],
        package_data={'ciervo': ['tests/data/marcha/*.csv', 'tests/data/marcha_larga/*.csv']},
        include_package_data=True,


)