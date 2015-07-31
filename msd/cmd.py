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
import logging
from argparse import ArgumentParser

from msd.scratch import build_scratch_db

DEFAULT_SCRATCH_DB = 'scratch.sqlite'
DEFAULT_OUTPUT_DB = 'data.sqlite'

log = logging.getLogger('msd.cmd')


def main(args=None):
    run(parse_args())


def run(opts):
    set_up_logging(opts)

    build_scratch_db(
        opts.input_dbs, opts.scratch_db, force=opts.force)


def set_up_logging(opts):
    level = logging.INFO
    if opts.verbose:
        level = logging.DEBUG
    elif opts.quiet:
        level = logging.WARN
    logging.basicConfig(format='%(name)s: %(message)s', level=level)


def parse_args(args=None):
    parser = ArgumentParser()
    parser.add_argument(
        dest='input_dbs', nargs='+',
        help='SQLite databases to merge')
    parser.add_argument(
        '-v', '--verbose', dest='verbose', default=False, action='store_true',
        help='Enable debug logging')
    parser.add_argument(
        '-q', '--quiet', dest='quiet', default=False, action='store_true',
        help='Turn off info logging')
    parser.add_argument(
        '-f', '--force', dest='force', default=False, action='store_true',
        help='Force rebuild of scratch DB, even if newer than input')
    parser.add_argument(
        '-i', '--scratch', dest='scratch_db',
        default=DEFAULT_SCRATCH_DB,
        help='Path to scratch DB (default: %(default)s)')
    parser.add_argument(
        '-o', '--output', dest='output_db', default=DEFAULT_OUTPUT_DB,
        help='Path to output DB (default: %(default)s)')

    return parser.parse_args(args)



if __name__ == '__main__':
    main()
