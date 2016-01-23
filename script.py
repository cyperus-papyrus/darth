# coding: utf-8
import urllib
import re
import csv
import xml.etree.ElementTree as ET
import argparse
import MySQLdb

parser = argparse.ArgumentParser(description='Выделяем isbn')
parser.add_argument('--in',required=True,dest='InFileName',help='укажите имя входного файла')
args = parser.parse_args()
#print (args.InFileName)

lst = []
with open(args.InFileName) as f:
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

n = 0
for i in lst_isbn:
    #url = 'http://old.rsl.ru/view.jsp?f=7&t=3&v0=' + str(l[n]) + '&f=1003&t=1&v1=&f=4&t=2&v2=&f=21&t=3&v3=&f=1016&t=3&v4=&f=1016&t=3&v5=&cc=a1&v=marc&s=2&ce=4'
    url = 'http://old.rsl.ru/view.jsp?f=7&t=3&v0=978-5-9922-0646-3&f=1003&t=1&v1=&f=4&t=2&v2=&f=21&t=3&v3=&f=1016&t=3&v4=&f=1016&t=3&v5=&cc=a1&v=marc&s=2&ce=4'
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
    t3 = re.sub(u'(<br\s{0,3}/>)', '', t3,0, re.M )    
    n = n + 1
    
#with open('www.txt', 'w') as f1:
#    f1.write(t3)
	
tree = ET.fromstring(t3)	

for child in tree.findall('tr'):
    for child2 in child.findall('td'):
		print child2.text


#формируем список из списков с одной карточкой 

card = []

# подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
db = MySQLdb.connect(host="localhost", user="root", passwd="123", db="bookcards", charset='utf8')
# формируем курсор, с помощью которого можно исполнять SQL-запросы
cursor = db.cursor()

for element in card:
        # подставляем эти данные в SQL-запрос
        sql = """INSERT INTO bookcards(field, marker, info)
        VALUES ('%(field)s', '%(marker)s', '%(info)s')
        """%{"field":card[0], "marker":card[1], "info":card[2]}
        # исполняем SQL-запрос
        cursor.execute(sql)
        # применяем изменения к базе данных
        db.commit()

# закрываем соединение с базой данных
db.close()
# закрываем файл
f.close()
