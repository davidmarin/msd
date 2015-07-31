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
from logging import getLogger

from msd.db import select_groups
from msd.merge import create_output_table
from msd.merge import merge_dicts
from msd.merge import output_row

log = getLogger(__name__)


def build_scraper_table(output_db, scratch_db):
    log.info('  building scraper table')
    create_output_table(output_db, 'scraper')

    for (scraper_id,), rows in select_groups(
            scratch_db, 'scraper', ['scraper_id']):

        if not scraper_id:
            continue

        scraper_row = merge_dicts(rows)
        output_row(output_db, 'scraper', scraper_row)
