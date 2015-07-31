# Copyright 2014-2015 SpendRight, Inc.
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
"""Table definitions."""
TABLES = dict(
    brand=dict(
        columns=dict(
            brand='text',
            company='text',
            facebook_url='text',
            is_former='integer',
            is_licensed='integer',
            is_prescription='integer',
            logo_url='text',
            tm='text',
            twitter_handle='text',
            url='text',
        ),
        primary_key=['company', 'brand'],
    ),
    campaign=dict(
        columns=dict(
            author='text',
            author_url='text',
            campaign='text',
            campaign_id='text',
            contributors='text',
            copyright='text',
            date='text',
            donate_url='text',
            email='text',
            facebook_url='text',
            goal='text',
            twitter_handle='text',
            url='text',
        ),
        primary_key=['campaign_id'],
    ),
    category=dict(
        columns=dict(
            brand='text',
            category='text',
            company='text',
            is_implied='integer',
        ),
        primary_key=['company', 'brand', 'category'],
    ),
    claim=dict(
        columns=dict(
            brand='text',
            campaign_id='text',
            claim='text',
            company='text',
            date='text',
            judgment='tinyint',
            scope='text',
            url='text',
        ),
        primary_key=['campaign_id', 'company', 'brand', 'scope', 'claim'],
    ),
    company=dict(
        columns=dict(
            company='text',
            company_full='text',
            email='text',
            facebook_url='text',
            feedback_url='text',
            hq_country='text',
            logo_url='text',
            parent_company='text',
            phone='text',
            twitter_handle='text',
            url='text',
        ),
        primary_key=['company'],
    ),
    rating=dict(
        columns=dict(
            brand='text',
            campaign_id='text',
            company='text',
            date='text',
            description='text',
            grade='text',
            judgment='tinyint',
            max_score='numeric',
            min_score='numeric',
            num_ranked='integer',
            rank='integer',
            scope='text',
            score='numeric',
            url='text',
        ),
        primary_key=['campaign_id', 'company', 'brand', 'scope'],
    ),
    scraper_brand_map=dict(
        columns=dict(
            brand='text',
            company='text',
            scraper_brand='text',
            scraper_company='text',
            scraper_id='text',
        ),
        primary_key=['scraper_id', 'scraper_company', 'scraper_brand'],
    ),
    scraper=dict(
        columns=dict(
            last_scraped='text',
            scraper_id='text',
        ),
        primary_key=['scraper_id'],
    ),
    scraper_category_map=dict(
        columns=dict(
            category='text',
            scraper_category='text',
            scraper_id='text',
        ),
        primary_key=['scraper_id', 'scraper_category'],
    ),
    scraper_company_map=dict(
        columns=dict(
            company='text',
            scraper_company='text',
            scraper_id='text',
        ),
        primary_key=['scraper_id', 'scraper_company'],
    ),
    subcategory=dict(
        columns=dict(
            category='text',
            is_implied='tinyint',
            subcategory='text',
        ),
        primary_key=['category', 'subcategory'],
    ),
    url=dict(
        columns=dict(
            url='text',
            last_scraped='text',
            facebook_url='text',
            twitter_handle='text',
        ),
        indexes=[
            ['url'],
        ],
        output=False,
        primary_key=['scraper_id', 'url'],
    ),
)
