# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import logging
import re
from tornado.options import options
from tornado.gen import coroutine, Return
from remote import transform, store
from bass.hubkey import generate_hub_key

ASSET_ID = re.compile(r'http://openpermissions.org/ns/id/[0-9a-f]{32}')


@coroutine
def onboard(data, content_type, repository_url, repository_id, token=None, r2rml_url=None):
    """
    Transforms source data into RDF triples
    :param data: the source data
    :param content_type: the http request content type
    :param repository_url: url of the repository service
    :param repository_id: the repository ID
    :param token: an authorization token
    :param r2rml_url: karma mapping file url (used by transformation)
    :return: list of on boarded assets and errors
    """
    assets = None

    response_trans, http_status, errors = yield transform(data, content_type, r2rml_url)

    if 'id_map' not in response_trans['data']:
        response_trans['data']['id_map'] = generate_idmap(
            response_trans, repository_id)

    logging.debug(response_trans)
    if not errors and http_status == 200:
        http_status, errors = yield store(response_trans, repository_url,
                                          repository_id, token=token)
        assets = response_trans['data']['id_map']
    logging.debug('<<< onboard')
    raise Return((assets, http_status, errors))


def verify(request):
    """
    Verify the request
    :param request: http request
    :returns: list of error dictionary
    """
    verify_results = (
        func(request) for func in
        [verify_content_type, verify_post_body_size])
    errors = [{'message': message}
              for message in verify_results if message]
    return errors


def verify_content_type(request):
    """
    Verify if the type of the source data is supported
    :param request: http request
    :returns: error message if there is any
    """
    supported_types = ['text/csv', 'application/json']
    content_type = request.headers.get('Content-Type', '')
    if content_type.split(';')[0] not in supported_types:
        return 'Unsupported content type "{}"'.format(content_type)


def verify_post_body_size(request):
    """
    Determines that the size of the body is within the limit of the system
    :param request: http request
    :returns: error message if there is any
    """
    content_length = long(request.headers.get('Content-Length', 0))
    logging.debug("Request size:{}".format(content_length))
    if content_length > options.max_post_body_size:
        return 'Content length:{} is too large. Max allowed is:{}'.format(
            content_length, options.max_post_body_size)


RE_ENTITY_ID="<http://openpermissions.org/ns/id/([^>]*)> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openpermissions.org/ns/op/1.1/Asset>"
RE_SOURCE_ID_TYPES="_:([^ ]+) <http://openpermissions.org/ns/op/1.1/id_type> <http://openpermissions.org/ns/hub(?:[^/]*)/([^>]+)>"
RE_SOURCE_IDS="_:([^ ]+) <http://openpermissions.org/ns/op/1.1/value> \"((?:[^\"]|\\\\\")*)\""
def generate_idmap(data, repository_id):
    """
    Generate hub_keys for assets and returns an id_map linking
    the final part of the asset with the key.

    :param data: A dictionary of containing different version of the
                 transformed data (output format is assumed to be n3)
    :param repository_id: ID of repository
    :returns: a dictionary mapping ids used in final part of the hub key
              with the hub key.
    """
    id_map = {}
    resolver_id = options.default_resolver_id
    hub_id = options.hub_id

    for value in data['data'].values():

        # now process each block in the triple data - karma outputs a double new line for each new record or EOF(FIXME!)
        for p in re.findall("(([^\n]|(\n[^\n]))*)(?:\n\n|\Z)", value, re.M):
            p = p[0]
            if len(p.strip()):
                # extract the necessary information
                try:
                    entity_id = re.findall(RE_ENTITY_ID, p, re.M)[0]
                except:
                    logging.warning("Could not find entity_id in triple data")
                    continue
                entity_source_id_types = dict(re.findall(RE_SOURCE_ID_TYPES, p, re.M))
                entity_source_id_values = dict(re.findall(RE_SOURCE_IDS, p, re.M))
                source_ids = []
                for k in entity_source_id_values.keys():
                    try:
                        source_ids.append({'source_id': entity_source_id_values[k], 'source_id_type': entity_source_id_types[k]})
                    except Exception, e:
                        logging.warning("exception extraction source ids %r" % (e,))
                        logging.warning("data=%s" % (p,))

                hub_key = generate_hub_key(resolver_id, hub_id, repository_id, 'asset', entity_id)

                id_map[hub_key] = {
                    "entity_type": 'asset',
                    "entity_id": entity_id,
                    "hub_key": hub_key,
                    "source_ids": source_ids
                }

    return id_map.values()
