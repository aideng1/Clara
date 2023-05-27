import requests
import csv
import json
title = []
i = 0
with open('books-isbns.csv', 'r') as a_file:
    for rows in a_file:
        isbn = rows
        book = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:{}&jscmd=details&format=json".format(isbn))
        print(book.json())
        title.append(book.json())
    with open('full-data.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        #for line in book:
        writer.writerow(title)
                #writer.writerow('\n')
        #title=[(book.json())]
        #print(title)
