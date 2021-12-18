#!/usr/bin/env python3

import os
from os import listdir, path
import argparse


DEFAULT_TEST_SIZE = 2 ** 26
parser = argparse.ArgumentParser()
parser.add_argument("--input", help="path to the directories containing all the test binaries.", default="./build")
parser.add_argument("--output", help="output directory.", default="./result")
parser.add_argument("-n", "--test-size", help="number of operations(insert/delete) per test.", default=DEFAULT_TEST_SIZE, type=int)
parser.add_argument("-l", "--load-factor", help="hashtable capacity", default=0.75, type=int)
parser.parse_args()


test_categories = [
  'ins',
  'mix',
  'agg',
  'con',
  'del',
]

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]