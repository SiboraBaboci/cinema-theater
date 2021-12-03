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
    projections = Projection.query.filter(func.DATE(Projection.date)<=date.today())
    print(projections[0])
    past_movie_id =[] 
    for projection in projections:
        past_movie_id.append(projection.movie_id)
    
    past_movies = Movie.query.filter(Movie.id.in_(past_movie_id))
    print(past_movies[0])
    #location of the template might have to be specified further in order for the return statement to work (maybe '/additional templates/main_view.html')
    return render_template('main_view.html', user=current_user, movies = past_movies)

#if we open the /movie page, the movie view is loaded into the skeleton
@app.route("/movie",  methods=['GET', 'POST'])
def open_movie():
    return render_template('movie_view.html',  user=current_user)

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
