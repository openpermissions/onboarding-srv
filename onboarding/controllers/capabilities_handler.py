# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""This handler returns information how many IDs can be generated in one
operation.
"""

from tornado.options import options
from koi.base import BaseHandler


class CapabilitiesHandler(BaseHandler):

    """ Returns information on the service Capabilities.
    """

    def get(self):
        """GET current service capabilities.

        Returns a JSON with info on the maximum body size for a post.
        """
        msg = {
            'status': 200,
            'data': {
                'max_post_body_size': options.max_post_body_size
            }
        }
        self.finish(msg)
