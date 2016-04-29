# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""API assets handler. Returns information on onboarded assets.
"""

from tornado.gen import coroutine
from koi import base, exceptions

from onboarding.models.remote import get_repository, exchange_delegate_token
from onboarding.models import assets


class AssetHandler(base.CorsHandler, base.JsonHandler):
    """Onboarding Rights Raw Data to RDF data into a repository"""

    @coroutine
    def post(self, repository_id):
        """
        Respond with JSON containing audit of assets on boarded

        :param repository_id: str
        """
        token = self.request.headers.get('Authorization')
        if token is None:
            raise exceptions.HTTPError(401, 'OAuth token not provided')
        token = token.split()[-1]
        new_token = yield exchange_delegate_token(token, repository_id)

        repository = yield get_repository(repository_id)
        repository_url = repository['service']['location']

        data = {}
        errors = assets.verify(self.request)
        http_status = 400

        if not errors:
            data, http_status, errors = yield assets.onboard(
                self.request.body,
                self.request.headers.get('Content-Type', None),
                repository_url,
                repository_id,
                token=new_token,
                r2rml_url=self.get_argument("r2rml_url", None))

        if not errors:
            self.set_status(http_status)
            self.finish({'status': 200, 'data': data})
        else:
            raise exceptions.HTTPError(
                http_status,
                {'errors': errors, 'data': data})
