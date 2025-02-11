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
from collections import OrderedDict

# Constants
DEFAULT_TEST_SIZE = 2 ** 26
DEFAULT_OUTPUT_DIR = f"./report/{datetime.now().strftime('%Y_%d_%m_%H_%M_%S')}"
MAX_THREAD = multiprocessing.cpu_count()
DEFAULT_THREADS = [2 ** i for i in range(int(math.log(MAX_THREAD, 2))+ 1)] # [1, 2, 4, ..., N_CPU]
DEFAULT_SKEWS = [
  0,
  0.1,
  0.2,
  0.3,
  0.4,
  0.5,
  0.55,
  0.6,
  0.65,
  0.7,
  0.75,
  0.8,
  0.825,
  0.85,
  0.875,
  0.9,
  0.92,
  0.94,
  0.96,
  0.98,
  0.99,
  0.991,
  0.992,
  0.993,
  0.994,
  0.995,
  0.996,
  0.997,
  0.998,
  0.999,
]
DEFAULT_CATEGORIES = [
  'ins',
  'mix',
  'agg',
  'con',
  'del',
]
DEFAULT_HASHTABLES = [
  'folly',
  'folklore',
  'TBBum',
  'cuckoo',
]

def run_multithreaded_benchmark(test_name, num_threads, test_size, test_dir, output_dir):
  for n_threads in num_threads:
    # Run test.
    logging.info(f"Running test <{test_name}> with {n_threads} threads.")
    outfile_path = path.join(output_dir, f"{test}_{n_threads}.log")
    with open(outfile_path, 'w') as outfile:
      subprocess.run([path.join(test_dir, test_name), '-c', str(capacity), '-n', str(test_size), '-p', str(n_threads)], stdout=outfile).check_returncode()

    # Parse output.
    logging.debug(f"Parsing test <{test_name}> output.")
    with open(outfile_path, 'r', newline='') as outfile:
      output_csv = pd.read_csv(outfile, sep='\s+')
      metrics = list(filter(lambda s: s.startswith('t_'), output_csv.columns))
      logging.debug(f"Found metrics {metrics} for <{test_name}>")
      for metric in metrics:
        rows = results.setdefault(metric, OrderedDict())
        row = rows.setdefault(n_threads, OrderedDict({'num_threads': n_threads}))
        row[test] = "{:.2f}".format(args.test_size / output_csv[metric].mean() / 1000)
  
  logging.info(f"Finished running test <{test_name}> with {n_threads} threads.")

def run_skew_benchmark(test_name, skews, test_size, test_dir, output_dir):
  for skew in skews:
    # Run test.
    logging.info(f"Running test <{test_name}> with {MAX_THREAD} threads and skew {skew}.")
    outfile_path = path.join(output_dir, f"{test}_{str(skew).replace('.', '_')}.log")
    with open(outfile_path, 'w') as outfile:
      subprocess.run([path.join(test_dir, test_name), '-c', str(capacity), '-n', str(test_size), '-p', str(MAX_THREAD), '-skew', str(skew)], stdout=outfile).check_returncode()

    # Parse output.
    logging.debug(f"Parsing test <{test_name}> output.")
    with open(outfile_path, 'r', newline='') as outfile:
      output_csv = pd.read_csv(outfile, sep='\s+')
      metrics = list(filter(lambda s: s.startswith('t_'), output_csv.columns))
      logging.debug(f"Found metrics {metrics} for <{test_name}>")
      for metric in metrics:
        rows = results.setdefault(metric, OrderedDict())
        row = rows.setdefault(skew, OrderedDict({'skew': skew}))
        row[test] = "{:.2f}".format(args.test_size / output_csv[metric].mean() / 1000)
  
  logging.info(f"Finished running test <{test_name}> with {MAX_THREAD} threads and skew {skew}.")


# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S")
file_handler = logging.FileHandler(filename="report.log", mode='w')
file_handler.setFormatter(LOG_FORMATTER)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input", help="path to the directories containing all the test binaries.", default="./build")
parser.add_argument("--output", help="output directory.", default=DEFAULT_OUTPUT_DIR)
parser.add_argument("-m", "--mode", help="mode to run. skew or thread", default='skew', type=str)
parser.add_argument("-n", "--test-size", help="number of operations(insert/delete) per test.", default=DEFAULT_TEST_SIZE, type=int)
parser.add_argument("-l", "--load-factor", help="hashtable load factor", default=0.75, type=float)
parser.add_argument("-t", "--num_threads", help="a list of number of threads", default=DEFAULT_THREADS, type=int, nargs='+')
parser.add_argument("-s", "--skews", help="a list of skews", default=DEFAULT_SKEWS, type=float, nargs='+')
parser.add_argument("-c", "--test_categories", help="test categories to run", default=DEFAULT_THREADS, type=str, nargs='+')
parser.add_argument("--hashtables", help="hashtables to run", default=DEFAULT_HASHTABLES, type=str, nargs='+')
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
logging.info(f"Running tests with categories {args.test_categories}, hashtables {args.hashtables}, size {args.test_size}, capacity {capacity}, and {args.num_threads} threads.")
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
  results = {} # A map of CSV files.
  for test in test_files:
    # Only run the tests that's specified in the cmd args.
    if all(map(lambda ht: test.find(ht) == -1, args.hashtables)):
      continue
    if args.mode == 'thread':
      run_multithreaded_benchmark(test, args.num_threads, args.test_size, test_dir, output_dir)
    elif args.mode == 'skew':
      run_skew_benchmark(test, args.skews, args.test_size, test_dir, output_dir)
    else:
      raise ValueError(f"Invalid mode {args.mode}")

  # Write results to CSVs
  for metric in results:
    output_report_path = path.join(output_dir, f'{category}_{metric}.csv')
    logging.info(f"Writting the report of category <{category}> to {output_report_path}")
    with open(output_report_path, 'w', newline='') as csvfile:
      rows = results[metric]
      writer = csv.DictWriter(csvfile, fieldnames=next(iter(rows.values())).keys(), quoting=csv.QUOTE_NONE)
      writer.writeheader()
      writer.writerows(rows.values())

