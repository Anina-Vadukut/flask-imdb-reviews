from flask import Flask, render_template, request, flash
import pandas as pd
from gevent.pywsgi import WSGIServer
from gensim.summarization.summarizer import summarize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from app.imdb_scraper import get_rating, get_movie_title, get_review_text, get_reviews
from multiprocessing import Pool
from flask_sqlalchemy import SQLAlchemy
import os


analyser = SentimentIntensityAnalyzer()

app = Flask(__name__)
app.secret_key = 'faultinyourstar'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Title(db.Model):
    __tablename__ = 'my_table'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(200))
    
    def __init__(self, key):
        self.key = key


@app.route('/', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':
        movie = request.form['text']
        data = Title(movie)
        db.session.add(data)
        db.session.commit()
        print(movie)
        try:
            soup1, rating = get_rating(movie)
            print(rating)
            dictionary = get_reviews(soup1)
            for url in [*dictionary]:
                name = get_movie_title(url)
                break
        
            rate = dictionary.values()
            a = [*dictionary]
            
            pool = Pool(10)
            results = pool.map(get_review_text, a)
            pool.close()
            pool.join()
                   
            movie_rev = dict(zip(results, rate))
            print(results)
            # construct a dataframe
            df = pd.DataFrame(movie_rev.items(), columns=['user_review', 'user_rating'])
            df['user_rating'] = df['user_rating'].astype(int)
            neg_lis, good_lis = [], []
            pos_correct, neg_correct = 0, 0
            print(df)
            for doc in zip(df['user_review'], df['user_rating']):
                if doc[1] > 6:
                    pos_correct += 1
                    good_lis.append(doc[0])
                elif doc[1] < 5:
                    neg_lis.append(doc[0])
                    neg_correct += 1  
                elif doc[1] in (5,6):
                    score = analyser.polarity_scores(doc[0])
                    if score['compound'] >= 0.1:
                        print(score['pos'] , score['neg'])
                        pos_correct += 1
                        good_lis.append(doc[0])
                    if score['compound'] < 0.1:
                        neg_lis.append(doc[0])
                        print(score['neg'])
                        neg_correct += 1    
            per = round(pos_correct*100/(pos_correct + neg_correct)) 
            neg = round(neg_correct*100/(pos_correct + neg_correct)) 
            lis = " ".join(good_lis)
            nlis = " ".join(neg_lis)  
            # Summary (200 words)
            psumm = summarize(lis, word_count=200)
            nsumm = summarize(nlis, word_count=200)
            print(pos_correct, neg_correct)
       
            return render_template('result.html',name=name, psumm=psumm, nsumm=nsumm, rating=rating, pos=per, neg=neg)
            
        except Exception:
            flash("No results found for")
            return render_template('error.html', movie=movie)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run()

   
