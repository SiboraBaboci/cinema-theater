from website import create_app
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from website.models import Movie, Projection
from datetime import date
from sqlalchemy import func

app = create_app()

#if we start the main page and nothing else, the main_view template is loaded into the skeleton
@app.route("/main")
def open_main():
    past_projections = Projection.query.filter(func.DATE(Projection.date)<=date.today())
    past_movie_ids =[] 
    for projection in past_projections:
        past_movie_ids.append(projection.movie_id)

    past_movies = []  
    for past_movie_id in past_movie_ids:
        past_movies.append(Movie.query.get(past_movie_id))


    future_projections = Projection.query.filter(func.DATE(Projection.date)>=date.today())
    future_movie_ids =[] 
    for projection in future_projections:
        future_movie_ids.append(projection.movie_id)

    future_movies = []  
    for future_movie_id in future_movie_ids:
        future_movies.append(Movie.query.get(future_movie_id))

    
    #location of the template might have to be specified further in order for the return statement to work (maybe '/additional templates/main_view.html')
    return render_template('main_view.html', user=current_user, past_movies = past_movies, future_movies = future_movies)

#if we open the /movie page, the movie view is loaded into the skeleton
@app.route("/movie/<movie_id>",  methods=['GET', 'POST'])
def open_movie(movie_id):
    movie = Movie.query.filter_by(id = movie_id).first()
    print(movie.img_str)
    return render_template('movie_view.html',  user=current_user, movie = movie)

@app.route("/reservation",  methods=['GET', 'POST'])
@login_required
def open_reservation():
    return render_template('reservation_view.html',  user=current_user)

@app.route("/customer",  methods=['GET', 'POST'])
@login_required
def open_customer():
    return render_template('customer_view.html',  user=current_user)

if __name__ == '__main__':
    app.run(debug=True)
