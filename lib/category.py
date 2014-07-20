# -*- coding: utf-8 -*-

#   Copyright 2014 David Marin
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Utilities for category information."""
import logging
from collections import defaultdict

from .vendor.titlecase import titlecase

from .db import output_row
from .db import select_all_categories
from .db import select_company_categories
from .norm import group_by_keys
from .norm import merge_dicts
from .norm import simplify_whitespace


BAD_CATEGORIES = ['Other']

log = logging.getLogger(__name__)


def fix_category(category):
    category = category.replace('&', ' and ')
    category = simplify_whitespace(category)
    category = titlecase(category)

    if not category or category in BAD_CATEGORIES:
        return None
    else:
        return category


def get_category_map():
    key_to_category = {}

    for campaign_id, campaign_category in select_all_categories():
        category = fix_category(campaign_category)
        if category is None:
            continue

        key_to_category[(campaign_id, campaign_category)] = category

    return key_to_category


def output_category_rows(category_map):
    category_to_keys = defaultdict(set)
    for key, category in category_map.iteritems():
        category_to_keys[category].add(key)

    for category, keys in sorted(category_to_keys.items()):
        campaign_ids = sorted(set(key[0] for key in keys))
        log.info(u'{} ({})'.format(
            category, ', '.join(c for c in campaign_ids)))

        for campaign_id, campaign_category in keys:
            map_row = dict(campaign_id=campaign_id,
                           campaign_category=campaign_category,
                           category=category)

            output_row(map_row, 'campaign_category_map')


def get_company_categories(company, keys, category_map):
    category_rows = []

    for campaign_id, campaign_company in keys:
        for row in select_company_categories(campaign_id, campaign_company):
            category = category_map.get((campaign_id, row['category']))
            if not category:  # bad category like "Other"
                continue
            row['category'] = category

            category_rows.append(row)

    for cr_group in group_by_keys(
            category_rows, keyfunc=lambda cr: [cr['category']]):
        row = merge_dicts(cr_group)

        row['company'] = company
        del row['campaign_id']

        yield row
