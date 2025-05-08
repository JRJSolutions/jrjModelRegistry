from setuptools import setup, find_packages

setup(
    name='jrjModelRegistry',
    version='0.0.4',
    packages=find_packages(),
    description='True way to save and serve python models',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jason Jafari',
    author_email='me@jasonjafari.com',
    url='https://github.com/JRJSolutions/jrjModelRegistry',
    classifiers=[
       'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='machine learning model saving serving',
    install_requires=[
        'dill>=0.3.8',
    ],
    project_urls={  # Optional
        'Documentation': 'https://github.com/JRJSolutions/jrjModelRegistry/blob/main/README.md',
        'Source': 'https://github.com/JRJSolutions/jrjModelRegistry',
        'Tracker': 'https://github.com/JRJSolutions/jrjModelRegistry/issues',
    },
)
