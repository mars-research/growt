#!/usr/bin/env python3

import os
from os import listdir, path
import argparse
import logging
from datetime import datetime
import pathlib
import subprocess
import csv
import pandas as pd
import multiprocessing
import math

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
DEFAULT_OUTPUT_DIR = f"./report/{datetime.now().strftime('%Y_%d_%m_%H_%M_%S')}"
DEFAULT_THREADS = [2 ** i for i in range(int(math.log(multiprocessing.cpu_count(), 2))+ 1)] # [1, 2, 4, ..., N_CPU]
DEFAULT_CATEGORIES = [
  'ins',
  'mix',
  'agg',
  'con',
  'del',
]
parser = argparse.ArgumentParser()
parser.add_argument("--input", help="path to the directories containing all the test binaries.", default="./build")
parser.add_argument("--output", help="output directory.", default=DEFAULT_OUTPUT_DIR)
parser.add_argument("-n", "--test-size", help="number of operations(insert/delete) per test.", default=DEFAULT_TEST_SIZE, type=int)
parser.add_argument("-l", "--load-factor", help="hashtable load factor", default=0.75, type=float)
parser.add_argument("-t", "--num_threads", help="number of threads", default=DEFAULT_THREADS, type=int, nargs='+')
parser.add_argument("-c", "--test_categories", help="test categories to run", default=DEFAULT_THREADS, type=str, nargs='+')
parser.add_argument("--log", help="log level", default="INFO")
args = parser.parse_args()
logging.debug(f"Program arguments: {args}")
capacity = int(args.test_size / args.load_factor)

# Setup console logging handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(LOG_FORMATTER)
stream_handler.setLevel(args.log)
logger.addHandler(stream_handler)

# Validate arguments
assert os.path.isdir(args.input), f"input directory not found: {args.input}"
if not os.path.isdir(args.output):
  logging.warning(f"Output directory not found, creating a new one: {args.output}")
  pathlib.Path(args.output).mkdir(parents=True, exist_ok=True)

# Run all tests and generate reports.
logging.info(f"Running tests with categories {args.test_categories}, size {args.test_size}, capacity {capacity}, and {args.num_threads} threads.")
for category in args.test_categories:
  test_dir = path.join(args.input, category)
  if path.isdir(test_dir):
    logging.info(f"Running tests in category <{category}>")
  else:
    logging.warning(f"Category <{category}> not found. Skipping.")
    continue
  test_files = [f for f in listdir(test_dir) if path.isfile(path.join(test_dir, f))]
  logging.debug(f"Test category <{category}> has test files: {test_files}")

  output_dir = path.join(args.output, category) 
  pathlib.Path(output_dir).mkdir()
  results = [] # Lists of KV pairs results which will be written the a CSV.
  column_names = {'name'}
  for test in test_files:
    for n_threads in args.num_threads:
      # Run test.
      logging.info(f"Running test <{test}> with {n_threads} threads.")
      outfile_path = path.join(output_dir, f"{test}_{n_threads}.log")
      with open(outfile_path, 'w') as outfile:
        subprocess.run([path.join(test_dir, test), '-c', str(capacity), '-n', str(args.test_size), '-p', str(n_threads)], stdout=outfile).check_returncode()

      # Parse output.
      logging.debug(f"Parsing test <{test}> output.")
      with open(outfile_path, 'r', newline='') as outfile:
        output_csv = pd.read_csv(outfile, sep='\s+')
        columns = list(filter(lambda s: s.startswith('t_'), output_csv.columns))
        logging.debug(f"Found columns {columns} for <{test}>")
        column_names.update(columns)
        result = {column: output_csv[column].mean() for column in columns}
        result['name'] = test
        results.append(result)
      logging.info(f"Finished running test <{test}>.")

  # Write results to CSV
  output_report_path = path.join(output_dir, f'{category}.csv')
  logging.info(f"Writting the report of category <{category}> to {output_report_path}")
  with open(output_report_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=column_names)
    writer.writeheader()
    writer.writerows(results)

