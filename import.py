import csv 
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker





engine = create_engine("")
db = scoped_session(sessionmaker(bind=engine))

def adbooks():
    

    f = open('books.csv')
    r = csv.reader(f)

    for isbn, title, author, year in r:
        if isbn.isdigit():
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": title, "author": author, "year": int(year)})
            print(f"added {isbn}, {title}, {author}, {year}")
        
    db.commit()

   
if __name__ == "__main__":    
    adbooks()


