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
import re
from functools import lru_cache
from logging import getLogger

from .company_data import BAD_COMPANY_ALIASES
from .company_data import COMPANY_CORRECTIONS
from .company_data import COMPANY_NAME_REGEXES
from .company_data import COMPANY_ALIASES
from .company_data import COMPANY_ALIAS_REGEXES
from .company_data import COMPANY_TYPE_CORRECTIONS
from .company_data import COMPANY_TYPE_RE
from .company_data import UNSTRIPPABLE_COMPANIES
from .company_data import UNSTRIPPABLE_COMPANY_TYPES
from .merge import create_output_table
from .merge import group_by_keys
from .merge import merge_dicts
from .merge import output_row
from .norm import norm
from .norm import simplify_whitespace
from .scratch import get_distinct_values

log = getLogger(__name__)


# use this to turn e.g. "babyGap" into "baby Gap"
# this can also turn "G.I. Joe" into "G. I. Joe"
CAMEL_CASE_RE = re.compile('(?<=[a-z\.])(?=[A-Z])')


def build_company_table(output_db, scratch_db):
    log.info('  building company table')
    create_output_table(output_db, 'company')
    log.warning('  filling company table not yet implemented')


def build_company_name_and_scraper_company_map_tables(output_db, scratch_db):
    log.info('  building scraper_company_map and company_name tables')
    create_output_table(output_db, 'scraper_company_map')
    create_output_table(output_db, 'company_name')

    # company dicts ("cds") containing the following sets:
    #
    # names: possible company names
    # aliases: name variants usable for matching (may include *names*)
    # scraper_companies: tuples of (scraper_id, scraper_company)

    cds = [dict(aliases=set(), names=set(), scraper_companies=set())]

    # populate with COMPANY_ALIASES
    for aliases in COMPANY_ALIASES:
        cds.append(dict(aliases=aliases()))

    # populate with 'company' and 'company_full' fields
    scraper_companies = (
        get_distinct_values(scratch_db, ['scraper_id', 'company']) |
        get_distinct_values(scratch_db, ['scraper_id', 'company_full']))

    for (scraper_id, scraper_company) in scraper_companies:
        if not (scraper_id and scraper_company):
            continue

        cds.append(dict(
            aliases=get_company_aliases(scraper_company),
            names=get_company_names(scraper_company),
            scraper_companies={(scraper_id, scraper_company)}))

    # populate from company_name table
    select_sql = 'SELECT company, company_name, is_alias FROM company_name'
    for scraper_company, scraper_company_name, is_alias in (
            scratch_db.execute(select_sql)):
        if not (scraper_company and scraper_company_name):
            continue

        aliases = (get_company_aliases(scraper_company) |
                   get_company_aliases(scraper_company_name))
        names = set()
        if not is_alias:
            # already did this for scraper_company, above
            names = get_company_names(scraper_company_name)

        cds.append(dict(aliases=aliases, names=names))

    # group together by normed variants of aliases
    def keyfunc(cd):
        keys = set()
        for cd in cds:
            for alias in cd.get('aliases', set()) | cd.get('names', set()):
                keys.update(norm_company(alias))
        return keys

    for cd_group in group_by_keys(cds, keyfunc):
        cd = merge_dicts(cd_group)

        if not (cd['scraper_companies'] and cd['names']):
            # this can happen if hard-coded variants don't match anything
            continue

        company = pick_company_name(cd['names'])
        company_full = pick_company_full(cd['names'])

        # write to scraper_company_map
        for scraper_id, scraper_company in sorted(cd['scraper_companies']):
            output_row(output_db, 'scraper_company_map', dict(
                company=company,
                scraper_id=scraper_id,
                scraper_company=scraper_company))

        # write to company_name
        for company_name in sorted(cd['names'] | cd['aliases']):
            row = dict(company=company, company_name=company_name)
            if company_name not in cd['names']:
                row['is_alias'] = 1
            if company_name == company_full:
                row['is_company_full'] = 1
            output_row(output_db, 'company_name', row)



def pick_company_name(names):
    # shortest name, ties broken by, not all lower/upper, has accents
    return sorted(names,
                  key=lambda n: (len(n), n == n.lower(), n == n.upper(),
                                 -len(n.encode('utf8'))))[0]


def pick_company_full(names):
    # longest name, ties broken by, not all lower/upper, has accents
    return sorted(names,
                  key=lambda n: (-len(n), n == n.lower(), n == n.upper(),
                                 -len(n.encode('utf8'))))[0]





def norm_company(s):
    variants = set()

    variants.add(norm(CAMEL_CASE_RE.sub(' ', s)))

    norm_s = norm(s)
    variants.add(norm_s)
    variants.add(norm_s.replace('-', ''))
    variants.add(norm_s.replace('-', ' '))
    variants.add(norm_s.replace(' and ', ' & '))
    variants.add(norm_s.replace(' and ', '&'))
    variants.add(norm_s.replace('&', ' & '))
    variants.add(norm_s.replace('&', ' and '))
    variants.add(norm_s.replace('.', ''))
    variants.add(norm_s.replace('.', '. '))
    variants.add(norm_s.replace("'", ''))

    return set(simplify_whitespace(v) for v in variants)


@lru_cache()
def get_company_names(company):
    """Get a set of possible ways to display company name."""
    return set(v for v in _yield_company_names(company)
               if len(v) > 1)


def _yield_company_names(company):
    company = COMPANY_CORRECTIONS.get(company) or company

    # if it's a name like Foo, Inc., allow "Foo" as a display variant
    m = COMPANY_TYPE_RE.match(company)
    if m and m.group('company') not in BAD_COMPANY_ALIASES:
        # process and re-build
        company = m.group('company')
        intl1 = m.group('intl1') or ''
        c_type = m.group('type')
        intl2 = m.group('intl2') or ''
        c_type = COMPANY_TYPE_CORRECTIONS.get(c_type) or c_type
        c_full = company + intl1 + ' ' + c_type + intl2

        yield c_full

        # if the "Inc." etc. is part of the name, stop here
        if (c_type in UNSTRIPPABLE_COMPANY_TYPES or
            c_full in UNSTRIPPABLE_COMPANIES):
            return

    yield company

    # handle # "The X Co.", "X [&] Co."
    for regex in COMPANY_NAME_REGEXES:
        m = regex.match(company)
        if m:
            name = m.group('company')
            if name not in BAD_COMPANY_ALIASES:
                yield name
                break


@lru_cache()
def get_company_aliases(company):
    """Get a set of all ways to match against this company. Some of
    these may be too abbreviated to use as the company's display name."""
    aliases = get_company_names()

    # Match "The X Company", "X Company", "Groupe X"
    for regex in COMPANY_ALIAS_REGEXES:
        m = regex.match(company)
        if m:
            alias = m.group('company')
            if alias not in BAD_COMPANY_ALIASES:
                aliases.add(aliases)
                break

    # split on slashes
    for a in list(aliases):
        if '/' in a and not COMPANY_TYPE_RE.match(a):  # don't split A/S
            aliases.update((part.strip() for part in a.split('/')))

    # remove short/empty matches
    return set(a for a in aliases if len(a) > 1)
