# -*- coding: utf-8

import MySQLdb
import string
import re

# распаковка строки, в которой поля записаны с разделителем ";"
def unpack_line(line):
    line = re.sub('\r\n', '', line,0, re.M )
    line = re.sub('"', '', line,0, re.M )
    line = re.sub(u'\([.*?]\)', '', line,0, re.M )
    line = re.sub(u'^\s+', '', line,0, re.M )
    line = re.sub(u'\s+$', '', line,0, re.M )
    els = string.split(line, ", ")
    fisbn = els
    return fisbn

# открываем исходный csv-файл
f = open("ISBN.csv", "r")
# представляем его в виде массива строк
lines = f.readlines()

lst = []

for line in lines:
    fisbn = unpack_line(line)
    lst.append(fisbn)
print lst
