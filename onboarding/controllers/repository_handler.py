# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# See the License for the specific language governing permissions and
# limitations under the License.

"""API assets handler. Returns information on onboarded assets"""
import logging

from tornado.gen import coroutine, Return
from tornado.options import options
from koi import base, exceptions

from onboarding.models.remote import get_repository, exchange_delegate_token
from onboarding.models import assets


class AssetHandler(base.CorsHandler, base.JsonHandler):
    """Onboarding Rights Raw Data to RDF data into a repository"""

    CONTENT_TYPES = ['text/csv', 'application/json']

    @coroutine
    def post(self, repository_id):
        """
        Respond with JSON containing audit of assets on boarded

        :param repository_id: str
        """
        token = yield self.get_token(repository_id)

        self.verify_content_type()
        self.verify_body_size()

        repository = yield get_repository(repository_id)
        repository_url = repository['service']['location']

        data, http_status, errors = yield assets.onboard(
            self.request.body,
            self.request.headers.get('Content-Type', None),
            repository_url,
            repository_id,
            token=token,
            r2rml_url=self.get_argument("r2rml_url", None))

        if not errors:
            self.finish({'status': 200, 'data': data})
        else:
            raise exceptions.HTTPError(
                http_status,
                {'errors': errors, 'data': data})

    @coroutine
    def get_token(self, repository_id):
        """Get a token granting access to the repository"""
        token = self.request.headers.get('Authorization')
        if token is None:
            raise exceptions.HTTPError(401, 'OAuth token not provided')
        token = token.split()[-1]

        new_token = yield exchange_delegate_token(token, repository_id)
        raise Return(new_token)

    def verify_content_type(self):
        """Return a 415 Unsupported Media Type error if invalid Content-Type"""
        content_type = self.request.headers.get('Content-Type', '')

        if content_type.split(';')[0] not in self.CONTENT_TYPES:
            msg = ('Unsupported content type "{}". '
                   'Content-Type header must be one of {}'
                   .format(content_type, self.CONTENT_TYPES))

            raise exceptions.HTTPError(415, msg)

    def verify_body_size(self):
        """Verify the size of the body is within the limit of the system"""
        content_length = long(self.request.headers.get('Content-Length', 0))
        logging.debug("Request size:{}".format(content_length))

        if content_length > options.max_post_body_size:
            msg = 'Content length:{} is too large. Max allowed is:{}'.format(
                content_length, options.max_post_body_size)
            raise exceptions.HTTPError(400, msg)
