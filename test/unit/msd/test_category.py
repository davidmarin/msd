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

from msd.category import _imply_category_ancestors
from msd.category import split_category


class TestImplyCategoryAncestors(TestCase):

    def test_empty(self):
        self.assertEqual(_imply_category_ancestors({}), {})

    def test_parent(self):
        self.assertEqual(
            _imply_category_ancestors({'parent': {'child'}}),
            {'child': {'parent'}})

    def test_tree(self):
        self.assertEqual(
            _imply_category_ancestors({'grandparent': {'parent', 'aunt'},
                                       'parent': {'child1', 'child2'}}),
            {'parent': {'grandparent'},
             'aunt': {'grandparent'},
             'child1': {'grandparent', 'parent'},
             'child2': {'grandparent', 'parent'}})

    def test_loop_of_size_1(self):
        self.assertEqual(
            _imply_category_ancestors({1: {1}}), {})

    def test_loop_of_size_2(self):
        self.assertEqual(
            _imply_category_ancestors({1: {2}, 2: {1}}),
            {1: {2}, 2: {1}})

    def test_loop_of_size_3(self):
        self.assertEqual(
            _imply_category_ancestors({1: {2}, 2: {3}, 3: {1}}),
            {1: {2, 3}, 2: {1, 3}, 3: {1, 2}})


class TestSplitCategory(TestCase):

    def test_empty(self):
        self.assertEqual(split_category(''), set())

    def test_simple_split(self):
        self.assertEqual(split_category('Home and Garden'),
                         {'Home', 'Garden'})

    def test_custom_split(self):
        self.assertEqual(split_category('Skin and Hair Care'),
                         {'Skin Care', 'Hair Care'})

    def test_oxford_comma(self):
        self.assertEqual(split_category('Foo, Bar, and Baz'),
                         {'Foo', 'Bar', 'Baz'})
