# coding: utf-8
import urllib
import re
import xml.etree.ElementTree as ET
import argparse
import MySQLdb
import time
import string

parser = argparse.ArgumentParser(description='Выделяем isbn')
parser.add_argument('--in', required=True, dest='InFileName', help='укажите имя входного файла')
parser.add_argument('--v', required=False, dest='verbose', action="store_true", help='verbose режим')
args = parser.parse_args()
#print (args.InFileName)

# распаковка строки, в которой поля записаны с разделителем ";"
def unpack_line(line):
    line = re.sub('\r\n', '', line, 0, re.M)
    line = re.sub('"', '', line, 0, re.M)
    line = re.sub(u'\([.*?]\)', '', line, 0, re.M)
    line = re.sub(u'^\s+', '', line, 0, re.M)
    line = re.sub(u'\s+$', '', line, 0, re.M)
    line = re.sub(u', ', ',', line, 0, re.M)
    els = string.split(line, ",")
    if( re.search(u'\d+',line) is None):
       els = []   
    return els

# открываем исходный csv-файл
f = open(args.InFileName, "r")
# представляем его в виде массива строк
lines = f.readlines()

lst_isbn = []

for line in lines:
    lst_isbn+= unpack_line(line)
#print lst_isbn

# подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
db = MySQLdb.connect(host="localhost", user="marc", passwd="123", db="marc", use_unicode=True,
                         charset='utf8') #charset='utf-8'
# формируем курсор, с помощью которого можно исполнять SQL-запросы
db.set_character_set('utf8')
cursor = db.cursor()

cursor.execute("SET NAMES utf8;")
cursor.execute("SET CHARACTER SET utf8")
cursor.execute("SET character_set_connection=utf8")
sql = u"""INSERT IGNORE INTO cards(isbn, field, marker, info)
        VALUES (%(isbn)s, %(field)s, %(marker)s, %(info)s)
        """ 

n = 0
for isbn in  lst_isbn:
    url = 'http://old.rsl.ru/view.jsp?f=7&t=3&v0=' + str(isbn) + '&f=1003&t=1&v1=&f=4&t=2&v2=&f=21&t=3&v3=&f=1016&t=3&v4=&f=1016&t=3&v5=&cc=a1&v=marc&s=2&ce=4'
    if args.verbose:
        print url 
    for http_attempts in range(1, 5):
#        try:
        data = urllib.urlopen(url).read() #.decode('utf-8') #.encode('utf-8')
#            break
#        except 
#    else:
#        print "Network global trouble"
#        exit()

        table = re.search('<span class="fcard"><b>.+?(<table.*?</table>)', data, re.DOTALL)
        try:
            t3 = ''.join(table.groups())
            break
        except AttributeError:
            print isbn, u' не могу найти! ', http_attempts
            time.sleep(1.1)
    else:    
        print isbn, u' не могу найти!'
        # исполняем SQL-запрос
        #print sql
        cursor.execute(sql, {"isbn":isbn, "field": u'xxx', "marker": '', "info": ''})

        # применяем изменения к базе данных
        db.commit()
        continue
    t3 = re.sub('bgcolor="?#EDEBE6"?', '', t3, 0, re.M)
    t3 = re.sub('\r', '', t3, 0, re.M)
    t3 = re.sub(u'^\s+$', '', t3, 0, re.M)
    t3 = re.sub(u'\n\n+', '\n', t3, 0, re.M)
    t3 = re.sub(u'(<strong>)|(</strong>)', '', t3, 0, re.M)
    t3 = re.sub(u'(<br\s{0,3}/>)', '', t3, 0, re.M)
    t3 = re.sub(u'(<)(?P<digits>\d{0,13}[\-\/\+\.0-9]{0,6}\d{0,13})(>)', '&lt;\g<digits>&gt;', t3, 0, re.M)
    t3 = re.sub(u'(<)(?P<alpha>[\-\/\+\.0-9А-Яа-яёЁ\s]{0,56})(>)', '&lt;\g<alpha>&gt;', t3, 0, re.M)
    t3 = re.sub('\x00', '', t3, 0, re.M)
    t3 = re.sub('&(?P<badamp>[ $CA-Яа-яёЁ])', '&amp;\g<badamp>', t3, 0, re.M)
    t3 = re.sub(u'LDR', '000', t3, 0, re.M)
    t3 = re.sub(u'<td colspan="2"></td>', '', t3, 0, re.M)
    with open('t3.txt','w') as f:
        f.write(t3)
        f.close
    tree = ET.fromstring(t3)
    #формируем список из списков с одной карточкой
    card = []

    for child in tree.findall('tr'):
        texts = [child2.text for child2 in child.findall('td')]
        #print child2.text
        if len(texts) > 1:
            if int(texts[0]) < 10:
                myrow = [texts[0], '', texts[1]]
            else:
                myrow = [texts[0], texts[1][:2], texts[1]]
        else: 
            continue
        card.append(myrow)

        #print card

    q = 0
    if args.verbose:
        print isbn, n
    for element in card:
        # исполняем SQL-запрос
        #print sql
        cursor.execute(sql,{"isbn":isbn, "field": card[q][0], "marker": card[q][1], "info": card[q][2]})
        # применяем изменения к базе данных
        db.commit()
        q = q + 1

    n = n + 1
    time.sleep(1.1)

# закрываем соединение с базой данных
db.close()


"""
CREATE TABLE `cards` (
	`isbn` VARCHAR(50) NULL DEFAULT NULL,
	`field` VARCHAR(4) NULL DEFAULT NULL,
	`marker` VARCHAR(2) NULL DEFAULT NULL,
	`info` TEXT NULL,
	UNIQUE INDEX `Индекс 2` (`isbn`, `field`, `marker`, `info`(100)),
	INDEX `Индекс 1` (`isbn`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
"""

