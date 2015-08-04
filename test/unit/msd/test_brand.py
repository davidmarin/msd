# -*- coding: utf-8 -*-
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
from unittest import TestCase

from msd.brand import split_brand_and_tm


class TestSplitBrandAndTM(TestCase):

    def test_empty(self):
        self.assertEqual(split_brand_and_tm(None), ('', ''))
        self.assertEqual(split_brand_and_tm(None), ('', ''))

    def test_plain_brand(self):
        self.assertEqual(split_brand_and_tm('Panasonic'), ('Panasonic', ''))

    def test_brand_with_symbol(self):
        self.assertEqual(split_brand_and_tm('Sprite®'), ('Sprite', '®'))

    def test_discard_part_after_symbol(self):
        self.assertEqual(split_brand_and_tm('INVOKANA™ (canagliflozin) USPI'),
                         ('INVOKANA', '™'))

    def test_strip(self):
        self.assertEqual(split_brand_and_tm(' RTFM ™ '),
                         ('RTFM', '™'))

    def test_on_tm(self):
        self.assertEqual(split_brand_and_tm('™'), ('', '™'))
