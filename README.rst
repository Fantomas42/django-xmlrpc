==============
Django XML-RPC
==============

**Django_xmlrpc** offers a means by which a Django developer can expose their
views (or indeed any other function) using XML-RPC.

This is a fork of the version hosted at :
https://code.launchpad.net/~aartemenko/django-xmlrpc/svetlyak40wt
compatible with Django >= 1.4 and Python >= 2.5.

If you want to use **django_xmlrpc** for an older version of Django or Python,
please use an old release.

.. contents::

Installation
============

You could retrieve the last sources from
http://github.com/Fantomas42/django-xmlrpc and run the installation script
::

  $> python setup.py install

or use pip ::

  $> pip install -e git://github.com/Fantomas42/django-xmlrpc.git#egg=django-xmlrpc

Usage
=====

Register **django_xmlrpc** in your INSTALLED_APPS section of your project'
settings.

Then register methods you want to handle like this in your project'
settings. ::

  >>> XMLRPC_METHODS = (('path.to.your.method', 'Method name'),
  ...                   ('path.to.your.othermethod', 'Other Method name'),)

Finally we need to register the url of the XML-RPC server. Insert something
like this in your project's urls.py: ::

  >>> url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc', name='xmlrpc'),
