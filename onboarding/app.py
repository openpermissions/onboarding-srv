# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Configures and starts up the Onboarding Service.
"""
import os.path

import tornado.ioloop
import tornado.httpserver
from tornado.options import options

import koi

from .controllers import (root_handler, capabilities_handler,
                          repository_handler)
from . import __version__

# directory containing the config files
CONF_DIR = os.path.join(os.path.dirname(__file__), '../config')


APPLICATION_URLS = [
    (r"", root_handler.RootHandler, {'version': __version__}),
    (r"/capabilities", capabilities_handler.CapabilitiesHandler),

    # Repository assets endpoints
    # POST - onboard assets to an organisations repository
    (r"/repositories/{repository_id}/assets",
     repository_handler.AssetHandler)
]


def main():
    """
    The entry point for the Onboarding service.
    This will load the configuration files and start a Tornado webservice
    with one or more sub processes.

    NOTES:
    tornado.options.parse_command_line(final=True)
    Allows you to run the service with custom options.

    Examples:
        Change the logging level to debug:
            + python template --logging=DEBUG
            + python template --logging=debug

        Configure custom syslog server:
            + python template --syslog_host=54.77.151.169
    """
    koi.load_config(CONF_DIR)
    app = koi.make_application(
        __version__,
        options.service_type,
        APPLICATION_URLS)
    server = koi.make_server(app)

    # Forks multiple sub-processes, one for each core
    server.start(int(options.processes))

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':      # pragma: no cover
    main()                      # pragma: no cover
