# -*- coding: utf-8 -*-

#   Copyright 2014 SpendRight, Inc.
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
"""General utilities for merging and normalization."""
import re

from titlecase import titlecase
from unidecode import unidecode

# use this to turn e.g. "babyGap" into "baby Gap"
# this can also turn "G.I. Joe" into "G. I. Joe"
CAMEL_CASE_RE = re.compile('(?<=[a-z\.])(?=[A-Z])')

# use to remove excess whitespace
WHITESPACE_RE = re.compile(r'\s+')

BAD_CHAR_REPLACEMENTS = [
    (u'\xa0', ' '),  # &nbsp;
    (u'\u2019', "'"),
]


def fix_bad_chars(s):
    for bad, good in BAD_CHAR_REPLACEMENTS:
        s = s.replace(bad, good)
    return s


def group_by_keys(items, keyfunc):
    key_to_group = {}

    for item in items:
        keys = set(keyfunc(item))

        group = {'keys': keys.copy(), 'items': [item]}

        # merge all matching groups into this one
        ids_seen = set()

        for key in keys:
            group_to_merge = key_to_group.get(key)
            if group_to_merge and id(group_to_merge) not in ids_seen:
                group['keys'].update(group_to_merge['keys'])
                group['items'].extend(group_to_merge['items'])
                ids_seen.add(id(group_to_merge))

        # make all keys point at our new group
        for key in group['keys']:
            key_to_group[key] = group

    # read out all groups
    ids_seen = set()

    for group in key_to_group.itervalues():
        if id(group) not in ids_seen:
            yield group['items']
            ids_seen.add(id(group))



def simplify_whitespace(s):
    """Strip s, and use only single spaces within s."""
    return WHITESPACE_RE.sub(' ', s.strip())


def norm(s):
    return unidecode(s).lower()


def norm_with_variants(s):
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


def merge_dicts(ds):
    """Merge a list of dictionaries."""
    result = {}

    for d in ds:
        for k, v in d.iteritems():
            if k not in result:
                if hasattr(v, 'copy'):
                    result[k] = v.copy()
                else:
                    result[k] = v
            else:
                if hasattr(result[k], 'update'):
                    result[k].update(v)
                elif hasattr(result[k], 'extend'):
                    result[k].extend(v)
                elif result[k] is None:
                    result[k] = v
                elif result[k] == '' and v != '':
                    result[k] = v

    return result


def to_title_case(s):
    """Like titlecase.titlecase(), but treat hyphens as spaces."""
    return ''.join(
        '-' if s[i] == '-' else c
        for i, c in enumerate(titlecase(s.replace('-', ' '))))
