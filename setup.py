from setuptools import setup, find_packages

setup(
    name='facereclib',
    version='0.1',
    description='Face recognition and face verification toolchain',

    #url='http://pypi.python.org/pypi/TowelStuff/',
    #license='LICENSE.txt',

    author='Manuel Guenther',
    author_email='Manuel.Guenther@idiap.ch',

    packages=find_packages(),

    entry_points={
      'console_scripts': [
        'faceverify.py = facereclib.script.faceverify:main',
        'faceverify_gbu.py = facereclib.script.faceverify_gbu:main',
        'faceverify_lfw.py = facereclib.script.faceverify_lfw:main',
        'faceverify_pose.py = facereclib.script.faceverify_pose:main',
        'parameter_test.py = facereclib.script.parameter_test:main',
        'baselines.py = facereclib.script.baselines:main'
        ],
      },

    #long_description=open('doc/install.rst').read(),

    install_requires=[
        "setuptools", # for whatever
        "bob >= 1.1.0a0",      # base signal proc./machine learning library
        # databases
    ],
)
