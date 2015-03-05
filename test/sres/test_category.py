from unittest import TestCase

from sres.category import _imply_category_ancestors


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
