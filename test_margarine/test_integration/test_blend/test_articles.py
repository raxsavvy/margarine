# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 by Alex Brandt <alex.brandt@rackspace.com>
#
# margarine is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import functools
import gridfs
import json
import logging
import mock
import pymongo
import unittest

from test_margarine import test_helpers
from test_margarine.test_common.test_blend import BaseBlendTest

logger = logging.getLogger(__name__)


@unittest.skipUnless(test_helpers.is_vagrant_up('datastore'), 'vagrant up datastore')
class BlendArticleReadWithDatastoreTest(BaseBlendTest):
    mocks_mask = set().union(BaseBlendTest.mocks_mask)

    mocks_mask = mocks_mask.union('datastores.get_collection')
    mocks_mask = mocks_mask.union('datastores.get_gridfs')

    mocks = set().union(BaseBlendTest.mocks)

    def setUp(self):
        super(BlendArticleReadWithDatastoreTest, self).setUp()

        self.datastore_url = 'mongodb://192.0.2.7/test'

        if self.mock_parameters():
            parameters = {
                'datastore.url': self.datastore_url,
            }

            self.mocked_PARAMETERS.__getitem__.side_effect = lambda _: parameters[_]

    mocks.add('parameters.PARAMETERS')

    def mock_parameters(self):
        if 'parameters.PARAMETERS' in self.mocks_mask:
            return False

        _ = mock.patch('margarine.datastores.PARAMETERS')

        self.addCleanup(_.stop)

        self.mocked_PARAMETERS = _.start()

        return True

    def add_fixture_to_datastore(self, fixture):
        database = pymongo.MongoClient(self.datastore_url)[self.datastore_url.rsplit('/', 1)[-1]]

        grid = gridfs.GridFS(database)

        fixture['bson']['body'] = grid.put(fixture['json']['body'], _id = fixture['bson']['body'], encoding = 'utf-8')

        self.addCleanup(functools.partial(grid.delete, fixture['bson']['body']))

        database['articles'].insert(fixture['bson'])

        self.addCleanup(functools.partial(database['articles'].remove, fixture['bson']['_id']))

    def test_article_read_get_unsubmitted(self):
        '''blend.articles—GET    /articles/? → 404—unmocked datastores,unsubmitted'''

        for article in self.articles['all']:
            response = self.fetch(self.base_url + article['uuid'])

            self.assertEqual(404, response.code)
            self.assertEqual(0, len(response.body))

    def test_article_read_head_unsubmitted(self):
        '''blend.articles—HEAD   /articles/? → 404—unmocked datastores,unsubmitted'''

        for article in self.articles['all']:
            response = self.fetch(self.base_url + article['uuid'], method = 'HEAD')

            self.assertEqual(404, response.code)
            self.assertEqual(0, len(response.body))

    def test_article_read_get_submitted_incomplete(self):
        '''blend.articles—GET    /articles/? → 404—umocked datastores,submitted,incomplete'''

        for article in self.articles['all']:
            del article['bson']['parsed_at']

            self.add_fixture_to_datastore(article)

            response = self.fetch(self.base_url + article['uuid'])

            self.assertEqual(404, response.code)
            self.assertEqual(0, len(response.body))

    def test_article_read_head_submitted_incomplete(self):
        '''blend.articles—HEAD   /articles/? → 404—unmocked datastores,submitted,incomplete'''

        for article in self.articles['all']:
            del article['bson']['parsed_at']

            self.add_fixture_to_datastore(article)

            response = self.fetch(self.base_url + article['uuid'], method = 'HEAD')

            self.assertEqual(404, response.code)
            self.assertEqual(0, len(response.body))

    def test_article_read_get_submitted_complete(self):
        '''blend.articles—GET    /articles/? → 200—ummocked datastores,submitted,complete'''

        for article in self.articles['all']:
            self.add_fixture_to_datastore(article)

            response = self.fetch(self.base_url + article['uuid'])

            self.assertEqual(200, response.code)

            self.assertIsNotNone(response.headers.get('Access-Control-Allow-Origin'))

            self.assertEqual('application/json', response.headers.get('Content-Type'))

            self.assertEqual(article['etag'], response.headers.get('ETag'))
            self.assertEqual(article['updated_at'], response.headers.get('Last-Modified'))
            self.assertEqual('<{0}>; rel="original"'.format(article['url']), response.headers.get('Link'))

            _, self.maxDiff = self.maxDiff, None
            self.assertEqual(article['json'], json.loads(response.body))
            self.maxDiff = _

    def test_article_read_head_submitted_complete(self):
        '''blend.articles—HEAD   /articles/? → 200—unmocked datastores,submitted,complete'''

        for article in self.articles['all']:
            self.add_fixture_to_datastore(article)

            response = self.fetch(self.base_url + article['uuid'], method = 'HEAD')

            self.assertEqual(200, response.code)

            self.assertIsNotNone(response.headers.get('Access-Control-Allow-Origin'))

            self.assertEqual('application/json', response.headers.get('Content-Type'))

            self.assertEqual(article['etag'], response.headers.get('ETag'))
            self.assertEqual(article['updated_at'], response.headers.get('Last-Modified'))
            self.assertEqual('<{0}>; rel="original"'.format(article['url']), response.headers.get('Link'))

            self.assertEqual(0, len(response.body))
