# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import logging
import json
import functools
import socket
from urllib import urlencode

from tornado.options import options
from tornado import httpclient
from tornado.gen import coroutine, Return
from tornado.concurrent import Future
from chub import API, oauth2
from koi import exceptions
from koi.configure import ssl_server_options


def raise_client_http_error(error):
    """
    Raise the httpclient.HTTPError as exceptions.HTTPError
    :param error: an httpclient.HTTPError
    :raise: exceptions.HTTPError
    """
    raise exceptions.HTTPError(error.code, json.loads(error.response.body))


def raise_from_remote(func):
    """
    Decorator to re-raise the http error from a remote server call
    """
    @coroutine
    @functools.wraps(func)
    def wrapper(*arg, **kw):
        try:
            result = func(*arg, **kw)
            if isinstance(result, Future):
                result = yield result
            raise Return(result)
        except httpclient.HTTPError as exc:
            raise_client_http_error(exc)
    return wrapper


@coroutine
def transform(data, content_type, r2rml_url):
    """
    Transforms source data into RDF triples
    :param data: the source data
    :param content_type: the http request content type
    :param r2rml_url: karma mapping file url
    :return: Transformed data and errors
    """
    logging.debug('>>> transform')

    response = None
    http_status = 200
    errors = []

    try:
        token = yield oauth2.get_token(
            options.url_auth,
            options.service_id,
            options.client_secret,
            scope=oauth2.Write(options.url_transformation),
            ssl_options=ssl_server_options()
        )
    except httpclient.HTTPError as exc:
        logging.exception('Error getting token for the transformation service')
        raise exceptions.HTTPError(500, 'Internal Server Error')

    headers = {'Accept': 'application/json', 'Content-Type': content_type}

    client = API(options.url_transformation,
                 token=token,
                 ssl_options=ssl_server_options())

    if r2rml_url:
        params = urlencode({'r2rml_url': r2rml_url})
        client.transformation.assets.path += '?{}'.format(params)

    try:
        client.transformation.assets.prepare_request(
            request_timeout=180,
            headers=headers,
            body=data
        )
        response = yield client.transformation.assets.post()
    except httpclient.HTTPError as exc:
        response = exc.response
        logging.exception(
            'Transformation service error body:{}'.format(exc.response))
        http_status = exc.code
        errors = json.loads(exc.response.body)['errors']

    logging.debug('<<< transform')
    raise Return((response, http_status, errors))


@raise_from_remote
@coroutine
def get_repository(repository_id):
    """
    Get the repository service address from accounts service
    for storing data.

    :param repository_id: the repository ID
    :return: url of the repository url
    :raise: HTTPError
    """
    client = API(options.url_accounts, ssl_options=ssl_server_options())
    try:
        response = yield client.accounts.repositories[repository_id].get()
        logging.debug(response['data'])
        raise Return(response['data'])
    except KeyError:
        error = 'Cannot find a repository'
        raise exceptions.HTTPError(404, error)


@coroutine
def exchange_delegate_token(token, repository_id):
    """
    Exchange a token for a delegated token

    :param token: a JWT granting the onboarding service access to write on the
        client's behalf
    :param repository_id: the target repsitory's ID
    :returns: a new JWT authorized to write to the repository
    :raises: HTTPError
    """
    try:
        new_token = yield oauth2.get_token(
            options.url_auth,
            options.service_id,
            options.client_secret,
            scope=oauth2.Write(repository_id),
            jwt=token,
            ssl_options=ssl_server_options()
        )
    except httpclient.HTTPError as exc:
        if exc.code in (403, 400):
            try:
                body = json.loads(exc.response.body)
                errors = [x['message'] for x in body['errors']]
            except (AttributeError, KeyError):
                errors = exc.message

            raise exceptions.HTTPError(403, errors, source='authentication')
        else:
            msg = 'Error authorizing access to the repository'
            logging.exception(msg)
            raise exceptions.HTTPError(500, msg)

    raise Return(new_token)


@coroutine
def store(response_trans, repository_url, repository_id, token=None):
    """
    Send the rdf N3 content to the repository service
    :param response_trans: transformed data from the transformation service
    :param repository_url: url of the repository service
    :param repository_id: the repository ID
    :param token: an authorization token
    :return: Errors
    """
    http_status = 200
    errors = []

    headers = {
        'Content-Type': 'text/rdf+n3',
        'Accept': 'application/json'
    }

    client = API(repository_url, ssl_options=ssl_server_options(), token=token)
    endpoint = client.repository.repositories[repository_id].assets

    try:
        rdf_n3 = response_trans['data']['rdf_n3']
        endpoint.prepare_request(
            request_timeout=180, headers=headers, body=rdf_n3)
        yield endpoint.post()
    except httpclient.HTTPError as exc:
        logging.debug('Repository service error code:{}'.format(exc.code))
        logging.debug('Repository service error body:{}'.format(exc.response))
        if exc.code in (400, 403):
            http_status = exc.code
            errors = json.loads(exc.response.body)['errors']
        else:
            http_status = 500
            errors = [
                {"message": "Repository service error {}".format(exc.code)}]
    # socket error can occur if repository_url doesn't resolve to anything
    # by the dns server
    except socket.error as exc:
        http_status = 500
        message = "Socket error {} from {}".format(exc.args, repository_url)
        errors = [{"message": message}]
    logging.debug('<<< transform')
    raise Return((http_status, errors))

@coroutine
def delete(response_trans, repository_url, repository_id, token=None):
    """
    Send the rdf N3 content to the repository service for it to be deleted
    :param response_trans: transformed data from the transformation service
    :param repository_url: url of the repository service
    :param repository_id: the repository ID
    :param token: an authorization token
    :return: Errors
    """
    http_status = 200
    errors = []

    headers = {
        'Content-Type': 'text/rdf+n3',
        'Accept': 'application/json'
    }

    client = API(repository_url, ssl_options=ssl_server_options(), token=token)
    endpoint = client.repository.repositories[repository_id].assets

    try:
        rdf_n3 = response_trans['data']['rdf_n3']
        endpoint.prepare_request(
            request_timeout=180, headers=headers, body=rdf_n3)
        yield endpoint.delete()
    except httpclient.HTTPError as exc:
        logging.debug('Repository service error code:{}'.format(exc.code))
        logging.debug('Repository service error body:{}'.format(exc.response))
        if exc.code in (400, 403):
            http_status = exc.code
            errors = json.loads(exc.response.body)['errors']
        else:
            http_status = 500
            errors = [
                {"message": "Repository service error {}".format(exc.code)}]
    # socket error can occur if repository_url doesn't resolve to anything
    # by the dns server
    except socket.error as exc:
        http_status = 500
        message = "Socket error {} from {}".format(exc.args, repository_url)
        errors = [{"message": message}]
    logging.debug('<<< transform')
    raise Return((http_status, errors))
