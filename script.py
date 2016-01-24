# coding: utf-8
import urllib
import re
import xml.etree.ElementTree as ET
import argparse
import MySQLdb
import time
import string

parser = argparse.ArgumentParser(description='Выделяем isbn')
parser.add_argument('--in',required=True,dest='InFileName',help='укажите имя входного файла')
args = parser.parse_args()
#print (args.InFileName)

# распаковка строки, в которой поля записаны с разделителем ";"
def unpack_line(line):
    line = re.sub('\r\n', '', line,0, re.M )
    line = re.sub('"', '', line,0, re.M )
    line = re.sub(u'\([.*?]\)', '', line,0, re.M )
    line = re.sub(u'^\s+', '', line,0, re.M )
    line = re.sub(u'\s+$', '', line,0, re.M )
    els = string.split(line, ", ")
    return els

# открываем исходный csv-файл
f = open(args.InFileName, "r")
# представляем его в виде массива строк
lines = f.readlines()

lst_isbn = []

for line in lines:
    els = unpack_line(line)
    lst_isbn.append(els)
#print lst_isbn

n = 0
for i in lst_isbn:
    url = 'http://old.rsl.ru/view.jsp?f=7&t=3&v0=' + str(lst_isbn[n]) + '&f=1003&t=1&v1=&f=4&t=2&v2=&f=21&t=3&v3=&f=1016&t=3&v4=&f=1016&t=3&v5=&cc=a1&v=marc&s=2&ce=4'
    #url = 'http://old.rsl.ru/view.jsp?f=7&t=3&v0=978-5-9922-0646-3&f=1003&t=1&v1=&f=4&t=2&v2=&f=21&t=3&v3=&f=1016&t=3&v4=&f=1016&t=3&v5=&cc=a1&v=marc&s=2&ce=4'
    data = urllib.urlopen(url).read() #.decode('utf-8') #.encode('utf-8')
    table = re.search('<span class="fcard"><b>.+?(<table.*?</table>)', data, re.DOTALL)
    try:
        t3 = ''.join(table.groups())
    except AttributeError:
        t3 = 'xxx'
    t3 = re.sub('bgcolor="?#EDEBE6"?', '', t3,0, re.M )
    t3 = re.sub('\r', '', t3,0, re.M )
    t3 = re.sub(u'^\s+$', '', t3,0, re.M )
    t3 = re.sub(u'\n\n+', '\n', t3,0, re.M )
    t3 = re.sub(u'(<strong>)|(</strong>)', '', t3,0, re.M )
    t3 = re.sub(u'(<br\s{0,3}/>)', '', t3,0, re.M )
    t3 = re.sub(u'LDR', '000', t3,0, re.M )
    n = n + 1
    tree = ET.fromstring(t3)
    #формируем список из списков с одной карточкой 
    card = []

    for child in tree.findall('tr'):
        texts = [child2.text for child2 in child.findall('td')]
        #print child2.text
        if len(texts) > 1:
            if int(texts[0]) < 010:
                myrow = [texts[0], 'No', texts[1]]
            else:
                myrow = [texts[0], texts[1][:2], texts[1]]
        else:
            myrow = ['x', 'x', 'x']
        card.append(myrow)

    #print card

# подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
    db = MySQLdb.connect(host="localhost", user="marc", passwd="123", db="marc", use_unicode=True, charset='utf8') #charset='utf-8'
# формируем курсор, с помощью которого можно исполнять SQL-запросы
    db.set_character_set('utf8')
    cursor = db.cursor()

    cursor.execute("SET NAMES utf8;")
    cursor.execute("SET CHARACTER SET utf8")
    cursor.execute("SET character_set_connection=utf8")
    n = 0
    for element in card:
# подставляем эти данные в SQL-запрос
        sql = u"""INSERT INTO cards(field, marker, info)
        VALUES ('%(field)s', '%(marker)s', '%(info)s')
        """%{"field":card[n][0], "marker":card[n][1], "info":card[n][2]}
# исполняем SQL-запрос
        print sql
        cursor.execute(sql)
# применяем изменения к базе данных
        db.commit()
        n = n + 1

# закрываем соединение с базой данных
    db.close()
