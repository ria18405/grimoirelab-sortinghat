#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from sortinghat import api
from sortinghat.cmd.move import Move
from sortinghat.db.database import Database

from tests.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT


MOVE_FROM_ID_NOT_FOUND_ERROR = "Error: FFFFFFFFFFF not found in the registry"
MOVE_TO_UUID_NOT_FOUND_ERROR = "Error: Jane Rae not found in the registry"

MOVE_OUTPUT = """Identity b4c250eaaf873a04093319f26ca13b02a9248251 moved to unique identity John Smith"""
MOVE_EMPTY_OUTPUT = ""


class TestBaseCase(unittest.TestCase):
    """Defines common setup and teardown methods on add unit tests"""

    def setUp(self):
        if not hasattr(sys.stdout, 'getvalue') and not hasattr(sys.stderr, 'getvalue'):
            self.fail('This test needs to be run in buffered mode')

        # Create a connection to check the contents of the registry
        self.db = Database(DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT)

        self.db.clear()

        self._load_test_dataset()

        # Create command
        self.kwargs = {'user' : DB_USER,
                       'password' : DB_PASSWORD,
                       'database' :DB_NAME,
                       'host' : DB_HOST,
                       'port' : DB_PORT}
        self.cmd = Move(**self.kwargs)

    def tearDown(self):
        self.db.clear()

    def _load_test_dataset(self):
        api.add_unique_identity(self.db, 'John Smith')
        api.add_identity(self.db, 'scm', 'jsmith@example.com',
                         uuid='John Smith')
        api.add_identity(self.db, 'scm', 'jsmith@example.com', 'John Smith',
                         uuid='John Smith')

        api.add_unique_identity(self.db, 'John Doe')
        api.add_identity(self.db, 'scm', 'jdoe@example.com',
                         uuid='John Doe')


class TestMove(TestBaseCase):
    """Unit tests for move"""

    def test_move(self):
        """Check behaviour moving an identity"""

        self.cmd.move('b4c250eaaf873a04093319f26ca13b02a9248251', 'John Smith')
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, MOVE_OUTPUT)

    def test_not_found_from_id_identity(self):
        """Check if it fails moving an identity that does not exist"""

        self.cmd.move('FFFFFFFFFFF', 'John Smith')
        output = sys.stderr.getvalue().strip()
        self.assertEqual(output, MOVE_FROM_ID_NOT_FOUND_ERROR)

    def test_not_found_to_uuid_unique_identity(self):
        """Check if it fails moving an identity to a unique identity that does not exist"""

        self.cmd.move('b4c250eaaf873a04093319f26ca13b02a9248251', 'Jane Rae')
        output = sys.stderr.getvalue().strip()
        self.assertEqual(output, MOVE_TO_UUID_NOT_FOUND_ERROR)

    def test_none_ids(self):
        """Check behavior moving None ids"""

        self.cmd.move(None, 'John Smith')
        self.cmd.move('b4c250eaaf873a04093319f26ca13b02a9248251', None)

        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, MOVE_EMPTY_OUTPUT)

        output = sys.stderr.getvalue().strip()
        self.assertEqual(output, MOVE_EMPTY_OUTPUT)

    def test_empty_ids(self):
        """Check behavior moving empty ids"""

        self.cmd.move('', 'John Smith')
        self.cmd.move('b4c250eaaf873a04093319f26ca13b02a9248251', '')

        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, MOVE_EMPTY_OUTPUT)

        output = sys.stderr.getvalue().strip()
        self.assertEqual(output, MOVE_EMPTY_OUTPUT)


if __name__ == "__main__":
    unittest.main(buffer=True, exit=False)
