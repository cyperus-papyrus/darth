# -*- coding: utf-8
import MySQLdb

card = [[u'LDR', u'', u'000111'],
['001', '', u'004716111'],
['017', '##', u'0121 лыололо'],
['020', '##', u'$a 978-5-9922-0646-3'],
['041', '0#', u'$a rus'],
['100', '1#', u'$a Кружевский']]


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
