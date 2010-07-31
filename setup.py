from setuptools import setup, find_packages
setup(
    name = 'django-xmlrpc',
    version = '0.1.0',
    description = 'XML-RPC Server App for the Django framework.',
    keywords = 'django apps xmlrpc',
    license = 'New BSD License',
    author = 'Graham Binns',
    author_email = 'graham.binns@gmail.com',
    maintainer = 'Alexander Artemenko',
    maintainer_email = 'svetlyak.40wt@gmail.com',
    url = 'https://launchpad.net/django-xmlrpc',
    install_requires = [],
    dependency_links = [],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(),
    include_package_data = True,
)

