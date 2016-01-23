# coding: utf-8
import urllib
import re
import csv
import xml.etree.ElementTree as ET

lst = []
with open('isbn_example.csv') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        lst.append(row)

n = 0
for i in lst:
    lst[n] = i[2:]
    n = n + 1
#print(lst)

import operator
listmerge = lambda s: reduce(operator.iadd, s, [])
lst_isbn = listmerge(lst)


res = []

url = "http://old.rsl.ru/view.jsp?f=7&t=3&v0=978-5-9922-0646-3&f=1003&t=1&v1=&f=4&t=2&v2=&f=21&t=3&v3=&f=1016&t=3&v4=&f=1016&t=3&v5=&cc=a1&v=marc&s=2&ce=4"
data = urllib.urlopen(url).read() #.decode('utf-8') #.encode('utf-8')
#data = s.read()
#s.close()

table = re.search('<span class="fcard"><b>.+?(<table.*?</table>)', data, re.DOTALL)
t3=''.join(table.groups())

t3 = re.sub('bgcolor="?#EDEBE6"?', '', t3,0, re.M )
t3 = re.sub('\r', '', t3,0, re.M )
t3 = re.sub(u'^\s+$', '', t3,0, re.M )
t3 = re.sub(u'\n\n+', '\n', t3,0, re.M )
t3 = re.sub(u'(<strong>)|(</strong>)', '', t3,0, re.M )
t3 = re.sub(u'^\s+$', '', t3,0, re.M )
t3 = re.sub(u'(<br\s{0,3}/>)', '', t3,0, re.M )

with open('www.txt', 'w') as f1:
    f1.write(t3)
	
tree = ET.fromstring(t3)	

for child in tree.findall('tr'):
    for child2 in child.findall('td'):
		print child2.text

