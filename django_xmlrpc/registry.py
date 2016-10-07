"""registry module for the django_xmlrpc package

Authors::
    Julien Fache

Credit must go to Brendan W. McAdams <brendan.mcadams@thewintergrp.com>, who
posted the original SimpleXMLRPCDispatcher to the Django wiki:
http://code.djangoproject.com/wiki/XML-RPC

New BSD License
===============
Copyright (c) 2007, Graham Binns http://launchpad.net/~codedragon

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the <ORGANIZATION> nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from collections import Callable
from logging import getLogger

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_xmlrpc.dispatcher import xmlrpc_dispatcher

logger = getLogger('xmlrpc.registry')


def register_xmlrpc_methods():
    """
    Register all xmlrpc methods in the server.
    """
    if hasattr(settings, 'XMLRPC_METHODS'):
        register_xmlrpc_methods_legacy()
    else:
        register_xmlrpc_methods_autodiscover()
    register_xmlrpc_methods_helpers()


def register_xmlrpc_method(path, name):
    """
    Register a method into the server.
    """
    # If 'path' is actually a function, just add it without fuss
    if isinstance(path, Callable):
        logger.info("Registering '%s:%s' => '%s'" % (
            path.__module__, path.__name__, name))
        xmlrpc_dispatcher.register_function(path, name)
        return

    # Otherwise we try and find something that we can call
    logger.debug('%s not callable, resolving path...' % path)
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]

    try:
        mod = __import__(module, globals(), locals(), [attr])
    except ImportError:
        raise ImproperlyConfigured(
            "Error registering XML-RPC method: "
            "module %s can't be imported" % module)

    try:
        func = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured(
            'Error registering XML-RPC method: '
            'module %s doesn\'t define a method "%s"' % (module, attr))

    if not isinstance(func, Callable):
        raise ImproperlyConfigured(
            'Error registering XML-RPC method: '
            '"%s" is not callable in module %s' % (attr, module))

    logger.info("Registering '%s:%s' => '%s'" % (module, attr, name))
    xmlrpc_dispatcher.register_function(func, name)


def register_xmlrpc_methods_legacy():
    """
    Load up any methods that have been registered
    with the server via settings.
    """
    logger.info('Register XML-RPC methods from settings.XMLRPC_METHODS')
    for path, name in settings.XMLRPC_METHODS:
        register_xmlrpc_method(path, name)


def register_xmlrpc_methods_autodiscover():
    """
    Looks in app directories for a module called 'xmlrpc'
    This should contain a distribution XMLRPC_METHODS declaration.
    """
    logger.info('Register XML-RPC methods by inspecting INSTALLED_APPS')
    for application in apps.get_app_configs():
        application_name = application.name
        logger.debug('Checking %s...' % application_name)
        try:
            module = __import__('%s.xmlrpc' % application_name,
                                globals(), locals(), [''])
            logger.debug('Found %s.xmlrpc' % application_name)
        except ImportError:
            logger.debug('Not found %s.xmlrpc' % application_name)
            continue
        if hasattr(module, 'XMLRPC_METHODS'):
            logger.info('Found XMLRPC_METHODS in %s.xmlrpc' % application_name)
            for path, name in module.XMLRPC_METHODS:
                register_xmlrpc_method(path, name)


def register_xmlrpc_methods_helpers():
    """Register the introspection and multicall methods
    with the XML-RPC namespace.
    """
    xmlrpc_dispatcher.register_introspection_functions()
    xmlrpc_dispatcher.register_multicall_functions()
