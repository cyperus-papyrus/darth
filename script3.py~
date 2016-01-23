# -*- coding: utf-8

import MySQLdb
import string
import re

# распаковка строки, в которой поля записаны с разделителем ";"
def unpack_line(line):
    #line = re.sub('[0-9Xx](, )[0-9]', '', line,0, re.M )
    line = re.sub('\r\n', '', line,0, re.M )
    line = re.sub('"', '', line,0, re.M )
    #line = string.replace(line, ", ", ";")
    els = string.split(line, ";")
    fisbn = els[2:]
    return fisbn

# открываем исходный csv-файл
f = open("isbn_example.csv", "r")
# представляем его в виде массива строк
lines = f.readlines()

lst = []

n = 0
for line in lines:
    fisbn = unpack_line(line)
    lst[n] = string.split(fisbn, ";")
    n = n + 1
print(lst)

import operator
listmerge = lambda s: reduce(operator.iadd, s, [])
lst_isbn = listmerge(lst)
