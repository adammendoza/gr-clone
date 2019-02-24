#returns list of book rating count and average rating from GoodReads API

import requests

def get_gr_info(isbn):
    #use API key here:
    key = ""
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    data = res.json() 
    data = data['books'][0]    
    return [data['ratings_count'], data['average_rating']]

if __name__ == "__main__":

    print(get_gr_info("0380795272"))
