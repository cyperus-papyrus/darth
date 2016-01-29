# coding: utf-8

import re
import argparse
import time


parser = argparse.ArgumentParser(description='Выделяем isbn')
parser.add_argument('--in', required=True, dest='InFileName', help='укажите имя входного файла')
parser.add_argument('--v', required=False, dest='verbose', action="store_true", help='verbose режим')
args = parser.parse_args()

import pymarc

r = pymarc.MARCReader(file(args.InFileName))
for x in r:
    print x
