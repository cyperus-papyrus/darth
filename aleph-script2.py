# coding: utf-8
import urllib
import re
import xml.etree.ElementTree as ET
import argparse
import MySQLdb
import time
import string
from HTMLParser import HTMLParser

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
    line = re.sub(u', ', ',', line, 0, re.M)
    line = re.sub(u' [-()\.А-Яа-яЁёI ,:;+\[\]]*', ',', line, 0, re.M)
    line = re.sub(u'. ', ',', line, 0, re.M)
    line = re.sub(u',+$', '', line, 0, re.M)
    line = re.sub(u',{2,}', ',', line, 0, re.M)
    line = re.sub(u'^\s+', '', line, 0, re.M)
    line = re.sub(u'\s+$', '', line, 0, re.M)
    els = string.split(line, ",")
    if( re.search(u'\d+',line) is None):
       els = []   
    return els

class UrlFinder(HTMLParser):
    ''' Класс-наследник HTMLParser. 
    '''
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []  

    def handle_starttag(self, tag, attrs):
        ''' Переопределяем метод HTMLParser (в базовом классе - метод ничего не делает)
        Сам метод вызывается для обработки начала тега (фактически вызывается для каждого 
        начального тега при вызове метода "feed"). 
        '''
        attrs = dict(attrs)
        # если находим тег 'a'
        if 'a' == tag:
            #try:
                # записываем значение аттрибута href в список-свойство links нашего класса
            self.links.append(attrs['href'])

# открываем исходный csv-файл
f = open(args.InFileName, "r")
# представляем его в виде массива строк
lines = f.readlines()
f.close()

lst_isbn = []

for line in lines:
    lst_isbn+= unpack_line(line)

# подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
db = MySQLdb.connect(host="localhost", user="marc", passwd="123", db="marc", use_unicode=True,
                         charset='utf8') #charset='utf-8'
# формируем курсор, с помощью которого можно исполнять SQL-запросы
db.set_character_set('utf8')
cursor = db.cursor()

cursor.execute("SET NAMES utf8;")
cursor.execute("SET CHARACTER SET utf8")
cursor.execute("SET character_set_connection=utf8")
sql = u"""INSERT IGNORE INTO aleph(isbn, field, info)
        VALUES (%(isbn)s, %(field)s, %(info)s)
        """ 

n = 0
for isbn in  lst_isbn:
    # урл к страничке, откуда будем тянуть ссылки
    BASE_URL = 'http://aleph.rsl.ru/F/JS6L9T5BA15ANLHE38MLVU1YAHDE6KBBDYUP2RNDJ5NY7RUSNY-01364?func=find-b&request=' + str(isbn) + '&find_code=WIB&adjacent=N&x=50&y=10'
    # создаём экземпляр класса UrlFinder()
    parser = UrlFinder()
    # вызываем метод feed, который передаёт текст в parser. 
    # Сам текст получаем по ссылке с помощью функций библиотеки urllib
    parser.feed(urllib.urlopen(BASE_URL).read())
    #теперь считаем количество найденных ссылок (просто подсчитывая количество элементов в links нашго экзепляра класса UrlFinder())
    #for link in parser.links:
    if 'format' in parser.links[17]:
        url = parser.links[17]
        continue
    else:    
        print isbn, u' не могу найти такой isbn!'
        cursor.execute(sql,{"isbn":isbn, "field": u'xxx', "info": ''})
        # применяем изменения к базе данных
        db.commit()
        continue

    url = url.replace('format=999', 'format=001')
    if args.verbose:
        print url 
    for http_attempts in range(1, 5):
        data = urllib.urlopen(url).read()
        table = re.search('(<table cellspacing=2 border=0 width=100%>.*?</table>)', data, re.DOTALL)
        try:
            t3 = ''.join(table.groups())
            break
        except AttributeError:
            print isbn, u' не могу найти карточку! ', http_attempts
            time.sleep(0.5)
    else:    
        print isbn, u' не могу найти!'
        # исполняем SQL-запрос
        #print sql
        cursor.execute(sql,{"isbn":isbn, "field": u'xxx', "info": ''})
        # применяем изменения к базе данных
        db.commit()
        continue
    t3 = ''.join(table.groups())
    t3 = re.sub(' class=td1 id=bold width="10%" nowrap', '', t3, 0, re.M)
    t3 = re.sub(' cellspacing=2 border=0 width=100%', '', t3, 0, re.M)
    t3 = re.sub(' class=td1', '', t3, 0, re.M)
    t3 = re.sub('<!-- filename: full-000-body -->', '', t3, 0, re.M)
    t3 = re.sub('<!-- filename: full-set-tail -->', '', t3, 0, re.M)
    t3 = re.sub(u'^\s+', '', t3, 0, re.M)
    t3 = re.sub(u'\s+$', '', t3, 0, re.M)
    t3 = re.sub('\r', '', t3, 0, re.M)
    t3 = re.sub(u'^\s+$', '', t3, 0, re.M)
    t3 = re.sub(u'^/(\s)/+', ' ', t3, 0, re.M)
    t3 = re.sub(u'\n\n+', '\n', t3, 0, re.M)
    t3 = re.sub(u'(<br\s{0,3}/>)', '', t3, 0, re.M)
    t3 = re.sub(u'&nbsp;', ' ', t3, 0, re.M)
    t3 = re.sub(u'LDR', '000', t3,0, re.M)
    with open('t3.txt','w') as f:
        f.write(t3)
        f.close
    tree = ET.fromstring(t3)
    #формируем список из списков с одной карточкой
    card = []

    for child in tree.findall('tr'):
        texts = [child2.text for child2 in child.findall('td')]
        card.append(texts)
    #print card
    q = 0
    if args.verbose:
        print isbn, n
    for element in card:
    # подставляем эти данные в SQL-запрос
        # исполняем SQL-запрос
        #print sql
        cursor.execute(sql,{"isbn":isbn, "field": card[q][0], "info": card[q][1]})
        # применяем изменения к базе данных
        db.commit()
        q = q + 1

    n = n + 1
    time.sleep(2.2)

# закрываем соединение с базой данных
db.close()

"""
CREATE TABLE `aleph` (
	`isbn` VARCHAR(50) NULL DEFAULT NULL,
	`field` VARCHAR(4) NULL DEFAULT NULL,
	`info` TEXT NULL,
	UNIQUE INDEX `Индекс 2` (`isbn`, `field`, `info`(100)),
	INDEX `Индекс 1` (`isbn`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
"""
