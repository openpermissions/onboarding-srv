# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from mock import MagicMock, patch

from tornado.escape import json_encode

from onboarding.controllers.capabilities_handler import CapabilitiesHandler


@patch('onboarding.controllers.capabilities_handler.options')
def test_get_capabilites(options):
    options.max_post_body_size = 1000
    handler = CapabilitiesHandler(MagicMock(), MagicMock())
    handler.finish = MagicMock()

    # MUT
    handler.get()
    msg = {
        'status': 200,
        'data': {
            'max_post_body_size': options.max_post_body_size
        }
    }

    handler.finish.assert_called_once_with(msg)
