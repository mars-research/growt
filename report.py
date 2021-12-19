#!/usr/bin/env python3

import os
from os import listdir, path
import argparse
import logging
from datetime import datetime

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S")
file_handler = logging.FileHandler(filename="report.log", mode='w')
file_handler.setFormatter(LOG_FORMATTER)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Parse arguments
DEFAULT_TEST_SIZE = 2 ** 26
DEFAULT_OUTPUT_DIR = f"./result/{datetime.now().strftime('%Y_%d_%m_%H_%M_%S')}"
parser = argparse.ArgumentParser()
parser.add_argument("--input", help="path to the directories containing all the test binaries.", default="./build")
parser.add_argument("--output", help="output directory.", default=DEFAULT_OUTPUT_DIR)
parser.add_argument("-n", "--test-size", help="number of operations(insert/delete) per test.", default=DEFAULT_TEST_SIZE, type=int)
parser.add_argument("-l", "--load-factor", help="hashtable capacity", default=0.75, type=int)
parser.add_argument("--log", help="log level", default="INFO")
args = parser.parse_args()
logger.debug(f"Program arguments: {args}")

# Setup console logging handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(LOG_FORMATTER)
stream_handler.setLevel(args.log)
logger.addHandler(stream_handler)

# Validate arguments
assert os.path.isdir(args.input), f"input directory not found: {args.input}"
if not os.path.isdir(args.output):
  logger.warning(f"Output directory not found, creating a new one: {args.output}")
  os.mkdir(args.output)

test_categories = [
  'ins',
  'mix',
  'agg',
  'con',
  'del',
]

for cat in test_categories:
  test_dir = path.join(args.input, cat)
  if path.isdir(test_dir):
    logging.info(f"Running tests in category {cat}")
  else:
    logging.warning(f"Category {cat} not found. Skipping.")
    continue
  test_files = [f for f in listdir(test_dir) if path.isfile(path.join(test_dir, f))]
  logger.debug(f"Test category <{cat}> has test files: {test_files}")

  for test in test_files:
    logger.debug(f"Running test {test}")



