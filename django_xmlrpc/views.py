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

from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django_xmlrpc.dispatcher import xmlrpc_dispatcher


logger = getLogger('xmlrpc.views')


@csrf_exempt
def handle_xmlrpc(request):
    """Handles XML-RPC requests. All XML-RPC calls should be forwarded here

    request
        The HttpRequest object that carries the XML-RPC call. If this is a
        GET request, nothing will happen (we only accept POST requests)
    """
    if request.method == 'POST':
        logger.info(request.body)
        try:
            response = HttpResponse(content_type='text/xml')
            response.write(
                xmlrpc_dispatcher._marshaled_dispatch(request.body))
            logger.debug(response)
            return response
        except:
            return HttpResponseServerError()
    else:
        methods = xmlrpc_dispatcher.system_listMethods()
        method_list = []

        for method in methods:
            sig_ = xmlrpc_dispatcher.system_methodSignature(method)
            sig = {
                'returns': sig_[0],
                'args': ', '.join(sig_[1:]),
            }

            # This just reads your docblock, so fill it in!
            method_help = xmlrpc_dispatcher.system_methodHelp(method)

            method_list.append((method, sig, method_help))

        return render(request, 'xmlrpc_get.html', {'methods': method_list})
