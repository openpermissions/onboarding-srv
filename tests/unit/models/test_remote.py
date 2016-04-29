# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import json
from mock import Mock, patch

from tornado.gen import coroutine, Return
from tornado.concurrent import Future
from tornado import httpclient
import pytest
from koi.exceptions import HTTPError
from koi.test_helpers import make_future

from onboarding.models import remote
from onboarding.models.assets import onboard


@patch('onboarding.models.remote.oauth2.get_token', return_value=make_future('token1234'))
@patch('onboarding.models.remote.options')
@patch('onboarding.models.remote.API')
def test_onboard_csv(API, options, get_token):
    options.service_id = 'test service ID'
    options.url_transformation = ''
    client = API()

    client.transformation.get.return_value = make_future({
        'data': {
            'serivce_name': 'transformation service',
            'service_id': 'tid123',
            'version': '0.1.0'
        }
    })

    future_transformation = Future()
    future_transformation.set_result({
        'status': 200,
        'data': {
            'id_map': [],
            'rdf_n3': ['']
        }
    })
    future_repository = Future()
    future_repository.set_result(([], []))
    API.return_value.transformation.assets.post = Mock(
        return_value=future_transformation)
    API.return_value.repository.repositories.__getitem__().assets.post = Mock(
        return_value=future_repository)

    data = (
        u'source_id_type,source_id,offer_ids,description\n'
        u'MaryEvánsPictureID,100123,1~2~3~4,Sunset over a Caribbean beach\n')
    data_type = 'csv'

    # MUT
    future_onboard = onboard(data, data_type, 'https://localhost:8004', 'test')
    (assets, http_status, errors) = future_onboard.result()

    assert assets is not None
    assert http_status == 200
    assert not errors


def test_raise_client_http_error():
    error = Mock()
    error.code = 404
    errors = {
        "status": 404,
        "errors": [
            {"source": "authentication", "message": "Organisation not found"}
        ]
    }
    error.response.body = json.dumps(errors)
    with pytest.raises(HTTPError) as err:
        remote.raise_client_http_error(error)
    assert err.value.status_code == error.code
    assert err.value.errors == errors


def test_raise_from_remote():
    @remote.raise_from_remote
    def func1():
        return 1

    @remote.raise_from_remote
    @coroutine
    def func2():
        raise Return(1)

    @remote.raise_from_remote
    @coroutine
    def func3():
        response = Mock()
        response.body = json.dumps({
            "status": 400,
            "errors": [
                {"source": "onboarding",
                 "message": "missing asset_type"}
            ]
        })
        raise httpclient.HTTPError(400, 'doh', response)

    assert func1().result() == 1
    assert func2().result() == 1
    with pytest.raises(HTTPError):
        func3().result()


@patch('onboarding.models.remote.oauth2.get_token', return_value=make_future('token1234'))
@patch('onboarding.models.remote.options')
@patch('onboarding.models.remote.API')
def test_get_repository(API, options, get_token):
    client = API()
    client.accounts.get.return_value = make_future({
        'data': {
            'serivce_name': 'accounts service',
            'service_id': 'aid123',
            'version': '0.1.0'
        }
    })
    data = {'data': {'id': 'repo1', 'name': 'my repo'}}
    response = make_future(data)
    API().accounts.repositories.__getitem__().get.return_value = response
    API().accounts.repositories.__getitem__.reset_mock()

    future = remote.get_repository('repo1')
    result = future.result()

    API().accounts.repositories.__getitem__.assert_called_once_with('repo1')
    assert result == data['data']


@patch('onboarding.models.remote.oauth2.get_token', return_value=make_future('token1234'))
@patch('onboarding.models.remote.options')
@patch('onboarding.models.remote.API')
def test_get_repository_empty(API, options, get_token):
    client = API()
    client.accounts.get.return_value = make_future({
        'data': {
            'serivce_name': 'accounts service',
            'service_id': 'aid123',
            'version': '0.1.0'
        }
    })
    data = {}
    response = make_future(data)
    API().accounts.repositories.__getitem__().get.return_value = response

    future = remote.get_repository('repo1')
    with pytest.raises(HTTPError) as exc:
        future.result()

    assert exc.value.status_code == 404
