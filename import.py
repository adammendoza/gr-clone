import csv 
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker





engine = create_engine("postgres://pykberctlnrhmr:856e0e8c5ce2be2837e2c847ba66b48ed9a96067ff6d896979cd7d145ea14092@ec2-54-83-33-213.compute-1.amazonaws.com:5432/d12hatdbde7ikn")
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


