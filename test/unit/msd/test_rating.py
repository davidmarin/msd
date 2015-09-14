# -*- coding: utf-8 -*-
# Copyright 2015 SpendRight, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from unittest import TestCase

from msd.db import insert_row
from msd.rating import build_rating_table
from msd.rating import grade_to_judgment

from ...db import DBTestCase
from ...db import select_all
from ...db import strip_null


class TestBuildRatingTable(DBTestCase):

    SCRATCH_TABLES = ['rating']

    OUTPUT_TABLES = ['scraper_brand_map', 'scraper_company_map']

    def setUp(self):
        super().setUp()

        # have company/brand maps ready
        insert_row(self.output_db, 'scraper_company_map', dict(
            scraper_id='sr.campaign.qux',
            company='Foo',
            scraper_company='Foo & Co.'))

        insert_row(self.output_db, 'scraper_brand_map', dict(
            scraper_id='sr.campaign.qux',
            company='Foo',
            brand='Bar',
            scraper_company='Foo & Co.',
            scraper_brand='BAR™'))

    def test_map_company(self):
        insert_row(self.scratch_db, 'rating', dict(
            scraper_id='sr.campaign.qux',
            campaign_id='qux',
            company='Foo & Co.',
            brand='',
            judgment=1))

        build_rating_table(self.output_db, self.scratch_db)

        self.assertEqual(
            [strip_null(row) for row in select_all(self.output_db, 'rating')],
            [dict(campaign_id='qux',
                  company='Foo',
                  brand='',
                  scope='',
                  judgment=1)])

    def test_map_brand(self):
        insert_row(self.scratch_db, 'rating', dict(
            scraper_id='sr.campaign.qux',
            campaign_id='qux',
            company='Foo & Co.',
            brand='BAR™',
            judgment=-1))

        build_rating_table(self.output_db, self.scratch_db)

        self.assertEqual(
            [strip_null(row) for row in select_all(self.output_db, 'rating')],
            [dict(campaign_id='qux',
                  company='Foo',
                  brand='Bar',
                  scope='',
                  judgment=-1)])

    def test_discard_null_judgment(self):
        # this tests issue #22
        insert_row(self.scratch_db, 'rating', dict(
            scraper_id='sr.campaign.qux',
            campaign_id='qux',
            company='Foo & Co.',
            brand='',
            scope=''))

        build_rating_table(self.output_db, self.scratch_db)

        self.assertEqual(select_all(self.output_db, 'rating'), [])

    def test_infer_judgment_from_grade(self):
        # this tests issue #23
        insert_row(self.scratch_db, 'rating', dict(
            scraper_id='sr.campaign.qux',
            campaign_id='qux',
            company='Foo & Co.',
            brand='',
            scope='',
            grade='B'))

        build_rating_table(self.output_db, self.scratch_db)

        self.assertEqual(
            [strip_null(row) for row in select_all(self.output_db, 'rating')],
            [dict(campaign_id='qux',
                  company='Foo',
                  brand='',
                  scope='',
                  grade='B',
                  judgment=1)])

    def test_judgment_trumps_grade(self):
        insert_row(self.scratch_db, 'rating', dict(
            scraper_id='sr.campaign.qux',
            campaign_id='qux',
            company='Foo & Co.',
            brand='',
            scope='',
            grade='B',
            judgment=-1))

        build_rating_table(self.output_db, self.scratch_db)

        self.assertEqual(
            [strip_null(row) for row in select_all(self.output_db, 'rating')],
            [dict(campaign_id='qux',
                  company='Foo',
                  brand='',
                  scope='',
                  grade='B',
                  judgment=-1)])

    def test_capitalize_grade(self):
        insert_row(self.scratch_db, 'rating', dict(
            scraper_id='sr.campaign.qux',
            campaign_id='qux',
            company='Foo & Co.',
            brand='',
            scope='',
            grade='b',
            judgment=1))

        build_rating_table(self.output_db, self.scratch_db)

        self.assertEqual(
            [strip_null(row) for row in select_all(self.output_db, 'rating')],
            [dict(campaign_id='qux',
                  company='Foo',
                  brand='',
                  scope='',
                  grade='B',
                  judgment=1)])

    def test_clamp_judgment(self):
        insert_row(self.scratch_db, 'rating', dict(
            scraper_id='sr.campaign.qux',
            campaign_id='qux',
            company='Foo & Co.',
            brand='',
            scope='',
            judgment=100))

        build_rating_table(self.output_db, self.scratch_db)

        self.assertEqual(
            [strip_null(row) for row in select_all(self.output_db, 'rating')],
            [dict(campaign_id='qux',
                  company='Foo',
                  brand='',
                  scope='',
                  judgment=1)])


class TestGradeToJudgment(TestCase):

    def test_uppercase_grades(self):
        self.assertEqual(grade_to_judgment('A'), 1)
        self.assertEqual(grade_to_judgment('B-'), 1)
        self.assertEqual(grade_to_judgment('C++'), 0)
        self.assertEqual(grade_to_judgment('D'), -1)
        self.assertEqual(grade_to_judgment('E'), -1)
        self.assertEqual(grade_to_judgment('F---'), -1)

    def test_no_lowercase_grades(self):
        self.assertEqual(grade_to_judgment('a'), None)

    def test_no_other_letters(self):
        self.assertEqual(grade_to_judgment('G-'), None)
