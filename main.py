from website import create_app
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from website.models import Movie, Projection, Screen
from datetime import date
from sqlalchemy import func

app = create_app()

#if we start the main page and nothing else, the main_view template is loaded into the skeleton
@app.route("/main")
def open_main():
    past_projections = Projection.query.filter(func.DATE(Projection.date)<=date.today())
    past_projections_object = [] 
    for projection in past_projections:
        current_movie = Movie.query.get(projection.movie_id)
        projection_dict ={
            "movie_id": current_movie.id,
            "movie_img_str": current_movie.img_str,
            "movie_title": current_movie.title,
            "movie_synopsis": current_movie.synopsis,
            "movie_duration": current_movie.duration,
            "movie_director": current_movie.director,
            "movie_main_cast": current_movie.main_cast,

            "projection_id": projection.id,
            "projection_date": projection.date
        } 
        
        past_projections_object.append(projection_dict)
    past_projections_list = (list({obj["movie_id"]:obj for obj in past_projections_object}.values()))
    print(past_projections_list)



    future_projections = Projection.query.filter(func.DATE(Projection.date)>=date.today())
    future_projections_object = [] 
    for projection in future_projections:
        current_movie = Movie.query.get(projection.movie_id)
        projection_dict ={
            "movie_id": current_movie.id,
            "movie_img_str": current_movie.img_str,
            "movie_title": current_movie.title,
            "movie_synopsis": current_movie.synopsis,
            "movie_duration": current_movie.duration,
            "movie_director": current_movie.director,
            "movie_main_cast": current_movie.main_cast,

            "projection_id": projection.id,
            "projection_date": projection.date
        } 
        future_projections_object.append(projection_dict)
    future_projections_list = (list({obj["movie_id"]:obj for obj in future_projections_object}.values()))
    print(future_projections_list)
    
    #location of the template might have to be specified further in order for the return statement to work (maybe '/additional templates/main_view.html')
    return render_template('main_view.html', user=current_user, past_projections=past_projections_list, future_projections_list=future_projections_list)

#if we open the /movie page, the movie view is loaded into the skeleton
@app.route("/movie/<movie_id>",  methods=['GET', 'POST'])
def open_movie(movie_id):

    projection = Projection.query.filter_by(movie_id = movie_id).first()
    current_movie = Movie.query.get(movie_id)
    current_screen = Screen.query.get(projection.screen_id)
    projection_dict ={
        "screen_id": current_screen.id,
        "screen_number": current_screen.number,
        "screen_capacity": current_screen.capacity,

        "projection_id": projection.id,
        "projection_date": projection.date
    } 
   
    return render_template('movie_view.html',  user=current_user, projection=projection_dict, movie = current_movie)

@app.route("/reservation",  methods=['GET', 'POST'])
@login_required
def open_reservation():
    return render_template('reservation_view.html',  user=current_user)

@app.route("/customer",  methods=['GET', 'POST'])
@login_required
def open_customer():
    reservations = current_user.reservations

    past_reservation_list =[] 

    for reservation in reservations:
        current_projection = Projection.query.get(reservation.projection_id)
        current_movie = Movie.query.get(current_projection.movie_id)
        current_screen = Screen.query.get(current_projection.screen_id)


        past_reservation_dict = { 
            "ID": reservation.id,
            "movie_title": current_movie.title,
            "screen_number": current_screen.number,
            "projection_date": current_projection.date,
            "reservation_owner": reservation.user.first_name,
            # "no_of_seats": reservation.no_of_seats,
            # "confirmation_date": reservation.date 
        }

        past_reservation_list.append(past_reservation_dict)

    future_reservation_list =[] 

    for reservation in reservations:
        current_projection = Projection.query.get(reservation.projection_id)
        current_movie = Movie.query.get(current_projection.movie_id)
        current_screen = Screen.query.get(current_projection.screen_id)


        future_reservation_dict = { 
            "ID": reservation.id,
            "movie_title": current_movie.title,
            "screen_number": current_screen.number,
            "projection_date": current_projection.date,
            "reservation_owner": reservation.user.first_name,
            # "no_of_seats": reservation.no_of_seats,
            # "confirmation_date": reservation.date 
        }

        future_reservation_list.append(future_reservation_dict)

    return render_template('customer_view.html', user=current_user, past_reservations=past_reservation_list, future_reservations=future_reservation_list)

if __name__ == '__main__':
    app.run(debug=True)
