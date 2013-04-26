import os
from setuptools import setup
from setuptools import find_packages

import django_xmlrpc


setup(name='django-xmlrpc',
      version=django_xmlrpc.__version__,

      description='XML-RPC Server App for the Django framework.',
      long_description=open(os.path.join('README.rst')).read(),
      keywords='django, service, xmlrpc',

      author='Graham Binns',
      author_email='graham.binns@gmail.com',
      maintainer='Fantomas42',
      maintainer_email='fantomas42@gmail.com',
      url='https://github.com/Fantomas42/django-xmlrpc',

      packages=find_packages(),
      classifiers=[
          'Framework :: Django',
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Programming Language :: Python',
          'Programming Language :: Python 3',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules'],

      license='New BSD License',
      include_package_data=True,
      zip_safe=False
      )
