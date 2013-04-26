"""Uses SimpleXMLRPCServer's SimpleXMLRPCDispatcher to serve XML-RPC requests

Authors::
    Graham Binns
    Reza Mohammadi
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
from logging import getLogger
from collections import Callable

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt

from django_xmlrpc.decorators import xmlrpc_func
from django_xmlrpc.dispatcher import DjangoXMLRPCDispatcher


logger = getLogger('xmlrpc')
xmlrpcdispatcher = DjangoXMLRPCDispatcher(allow_none=False, encoding=None)


@xmlrpc_func(returns='string', args=['string'])
def test_xmlrpc(text):
    """Simply returns the args passed to it as a string"""
    return "Here's a response! %s" % str(text)


@csrf_exempt
def handle_xmlrpc(request):
    """Handles XML-RPC requests. All XML-RPC calls should be forwarded here

    request
        The HttpRequest object that carries the XML-RPC call. If this is a
        GET request, nothing will happen (we only accept POST requests)
    """
    if request.method == "POST":
        logger.info(request.body)
        try:
            response = HttpResponse(content_type='text/xml')
            response.write(
                xmlrpcdispatcher._marshaled_dispatch(request.body))
            logger.debug(response)
            return response
        except:
            return HttpResponseServerError()
    else:
        methods = xmlrpcdispatcher.system_listMethods()
        method_list = []

        for method in methods:
            sig_ = xmlrpcdispatcher.system_methodSignature(method)
            sig = {
                'returns': sig_[0],
                'args': ", ".join(sig_[1:]),
            }

            # this just reads your docblock, so fill it in!
            method_help = xmlrpcdispatcher.system_methodHelp(method)

            method_list.append((method, sig, method_help))

        return render_to_response('xmlrpc_get.html', {'methods': method_list},
                                  context_instance=RequestContext(request))


# Load up any methods that have been registered with the server in settings
if hasattr(settings, 'XMLRPC_METHODS'):
    for path, name in settings.XMLRPC_METHODS:
        # if "path" is actually a function, just add it without fuss
        if isinstance(path, Callable):
            xmlrpcdispatcher.register_function(path, name)
            continue

        # Otherwise we try and find something that we can call
        i = path.rfind('.')
        module, attr = path[:i], path[i + 1:]

        try:
            mod = __import__(module, globals(), locals(), [attr])
        except ImportError as ex:
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

        xmlrpcdispatcher.register_function(func, name)


# Finally, register the introspection and multicall methods with the XML-RPC
# namespace
xmlrpcdispatcher.register_introspection_functions()
xmlrpcdispatcher.register_multicall_functions()
