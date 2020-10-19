import requests
from bs4 import BeautifulSoup


def get_rating(text):
    """
    function which takes a movie name and returns a Soup object of reviews and movie rating.
    """
    movie = text
    page = requests.get('http://www.imdb.com/find?ref_=nv_sr_fn&q=' + movie + '&s=tt')
    soup1 = BeautifulSoup(page.content, 'html.parser')
    movieid = soup1.select(".findList tr a")[0].get('href')
    movielink = "http://www.imdb.com" + movieid
    mlinkpage = requests.get(movielink)
    soup2 = BeautifulSoup(mlinkpage.content, 'html.parser')
    movierating = soup2.select(".ratingValue span")[0].text
    metascore = soup2.select(".metacriticScore")
    reviewlink = movielink + 'reviews'
    linkpage = requests.get(reviewlink)
    soup3 = BeautifulSoup(linkpage.content, 'html.parser')
    
    return soup3, movierating

def get_soup(url):
    """
    Utility function which takes a url and returns a Soup object.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def get_review_text(review_url):
    '''Returns the user review text given the review url.'''
    
    # get the review_url's soup
    soup = get_soup(review_url)
    
    # find div tags with class text show-more__control
    tag = soup.find('div', attrs={'class': 'text show-more__control'})
    return tag.getText()

def get_movie_title(review_url):
    '''Returns the movie title from the review url.'''
    
    # get the review_url's soup
    soup = get_soup(review_url)
    # find h1 tag
    tag = soup.find('h1')
    return list(tag.children)[1].getText()

def get_reviews(soup):
    '''Function returns reviews url for the movie.'''    

    review_dict={}
    # get a list of user ratings

    for i in soup.find_all('div', attrs={'class':'review-container'}):
        if i.find('span', attrs={'class':'spoiler-warning'}):
            pass
        else:
            a = i.find('a', attrs={'class':'title'})
            b = "https://www.imdb.com" + a['href']
            if i.find('span', attrs={'class': 'point-scale'}):
                review_dict[b] = next(tag.previous_element.previous_element for tag in i.find('span', attrs={'class': 'point-scale'}))
                

    return review_dict
