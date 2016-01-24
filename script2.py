# -*- coding: utf-8

import MySQLdb
import string

# распаковка строки, в которой поля записаны с разделителем ";"
def unpack_line(line):
    line = string.replace(line, "'", "")
    els = string.split(line, ";")
    # выделяем имя, емейл, адрес и телефон
    fname = els[0]
    fmail = els[1]
    fadres = els[2]
    ftel = els[3]
    return fname, fmail, fadres, ftel

# подключаемся к базе данных (не забываем указать кодировку, а то в базу запишутся иероглифы)
db = MySQLdb.connect(host="localhost", user="root", passwd="пароль", db="contacts", charset='utf8')
# формируем курсор, с помощью которого можно исполнять SQL-запросы
cursor = db.cursor()

# открываем исходный csv-файл
f = open("log", "r")
# представляем его в виде массива строк
lines = f.readlines()

for line in lines:
    # если в строе присутствует емейл (определяем по наличию "@")
    if string.find(line, "@") > -1:
        # извлекаем данные из строки
        fname, fmail, fadres, ftel = unpack_line(line)
        # подставляем эти данные в SQL-запрос
        sql = """INSERT INTO contacts(name, mail, adres, tel)
        VALUES ('%(name)s', '%(mail)s', '%(adres)s', '%(tel)s')
        """%{"name":fname, "mail":fmail, "adres":fadres, "tel":ftel}
        # исполняем SQL-запрос
        cursor.execute(sql)
        # применяем изменения к базе данных
        db.commit()

# закрываем соединение с базой данных
db.close()
# закрываем файл
f.close()
