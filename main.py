from website import create_app
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website.models import Movie, Projection, Screen, UserRole, Reservation, User
from website import db
from datetime import datetime, timedelta
from sqlalchemy import func
from datetime import date
from sqlalchemy.orm import sessionmaker

app = create_app()

# we have here two roots '/' and '/main' if you make a request to any of those you get the main view with todays and nex days projections
@app.route("/")
@app.route("/main")
def open_main():
    today_projections = Projection.query.filter(func.DATE(Projection.date)==datetime.today().strftime("%Y-%m-%d"))
    today_projections_object = []              
    for projection in today_projections:
        current_movie = Movie.query.get(projection.movie_id)

       # then we are trying to have an object with all information of movie and projection 
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
        
    today_projections_list = (list({obj["movie_id"]:obj for obj in today_projections_object}.values()))
    
    future_projections = Projection.query.filter(func.DATE(Projection.date)>datetime.today().strftime("%Y-%m-%d"))
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

     # this step is to show in main view only the unique projections of next days 
    future_projections_list = (list({obj["movie_id"]:obj for obj in future_projections_object}.values()))
    
    current_date = datetime.today().strftime("%d/%m/%Y")
    
    return render_template('main_view.html', user=current_user,  UserRole=UserRole, today_projections=today_projections_list, future_projections_list=future_projections_list, current_date=current_date)

# if we open the '/movie/<moview_id>' page, the movie view is loaded into the skeleto
# by writing '/movie/<moview_id>' into the browser we will get the information about the moview that was clicked in main view 
# and also below movie informations there will be todays projections and next projection where if user is logged in they can make a reservation
@app.route("/movie/<movie_id>",  methods=['GET', 'POST'])
def open_movie(movie_id):
    
    # here we query movie by moview_id that we get from the request  (after clicking see more details about movie)    
    current_movie = Movie.query.get(movie_id)

    # here i get all the projections of the movie that i am looking for  
    projections = Projection.query.filter_by(movie_id = movie_id)

    today_projections = [] 
    future_projections = []
    
    new_reservation_obj = {}  
    new_reservation_obj_today = {}  

    # now i want to go through every projection in order that i split in todays and future projections 
    for projection in projections:

        if projection.date  <= datetime.today():
            
           # so here for each projection i query the current_screen that will be played 
            current_screen = Screen.query.get(projection.screen_id)

           # this object is for gathering information of screen and projection and then this obj will be sent to frontend  
            projection_dict ={
                "screen_id": current_screen.id,
                "screen_number": current_screen.number,
                "screen_capacity": current_screen.capacity,
                "projection_available_slots": projection.available_slots,
                "projection_id": projection.id,
                "projection_date": projection.date
            } 
            today_projections.append(projection_dict)


           # here is the step when you are at the movie view and customer wants to make a reservation by clicking the button
           # after clicking the button there will be a request with method POST because i gave insode the form  

           # we store the  information needed for making a reservation, and here it is splitted into two part one today and one futur, and this one is if projection that is about to be reserved is today!
            no_of_seats = ''
            if request.method == 'POST' and projection_dict['projection_date']  <= datetime.today():
                print(no_of_seats, current_user.id)

                no_of_seats = int(request.form.get('no_seats'))
                print(no_of_seats, current_user.id, 'today')
                new_reservation_obj_today = {
                    "res_label": "today",
                    "user_id": current_user.id,
                    "projection_id": projection.id,
                    "current_capacity": current_screen.capacity,
                    "projection_available_slots": projection.available_slots,
                    "no_of_seats": no_of_seats,
                    "conf_date": datetime.today(),
                    "screen_id": current_screen.id,
                } 


        elif projection.date  >= datetime.today():
           
            current_screen = Screen.query.get(projection.screen_id)
            projection_dict ={
                "screen_id": current_screen.id,
                "screen_number": current_screen.number,
                "screen_capacity": current_screen.capacity,
                "projection_available_slots": projection.available_slots,
                "projection_id": projection.id,
                "projection_date": projection.date
            } 
            future_projections.append(projection_dict)

            no_of_seats = ''
            if request.method == 'POST' and projection_dict['projection_date']  >= datetime.today():

                no_of_seats = int(request.form.get('no_seats'))
                print(no_of_seats, current_user.id,'future')

                new_reservation_obj = {
                    "res_label": "future",
                    "user_id": current_user.id,
                    "projection_id": projection.id,
                    "current_capacity": current_screen.capacity,
                    "projection_available_slots": projection.available_slots,
                    "no_of_seats": no_of_seats,
                    "conf_date": datetime.today(),
                    "screen_id": current_screen.id,
                } 

    # after we get POST request and after we store the information above splitted into 2 groups now its time to actually get that data and store into database! 
    if request.method == 'POST':
        if new_reservation_obj['res_label'] == 'future':
            # save to db if upcomming reservation 
            new_reservation = Reservation(user_id=new_reservation_obj['user_id'] , projection_id=new_reservation_obj['projection_id'], no_of_seats=new_reservation_obj['no_of_seats'], conf_date=new_reservation_obj['conf_date'])
            db.session.add(new_reservation)
            db.session.commit() 
            print(new_reservation_obj['screen_id'])

            # update screen available slots 
            projection_to_be_updated = Projection.query.get(new_reservation_obj['projection_id'])
            projection_to_be_updated.available_slots = new_reservation_obj['projection_available_slots'] - new_reservation_obj['no_of_seats'] 
            db.session.commit()            

            flash('Reservation saved.', category = 'success')
            return redirect(url_for('open_customer'))

        if new_reservation_obj_today['res_label'] == 'today':
            # save to db if upcomming reservation 
            new_reservation = Reservation(user_id=new_reservation_obj_today['user_id'] , projection_id=new_reservation_obj_today['projection_id'], no_of_seats=new_reservation_obj_today['no_of_seats'], conf_date=new_reservation_obj_today['conf_date'])
            db.session.add(new_reservation)
            db.session.commit() 
            print(new_reservation_obj_today['screen_id'])

            # update screen available slots 
            projection_to_be_updated = Projection.query.get(new_reservation_obj_today['projection_id'])
            projection_to_be_updated.available_slots = new_reservation_obj_today['projection_available_slots'] - new_reservation_obj_today['no_of_seats'] 
            db.session.commit()            

            flash('Reservation saved.', category = 'success')
            return redirect(url_for('open_customer'))
        
   
   
    return render_template('movie_view.html', UserRole=UserRole, user=current_user, today_projection=today_projections, future_projections = future_projections, movie = current_movie)

@app.route("/reservation/<reservation_id>",  methods=['GET', 'POST'])
@login_required
def open_reservation(reservation_id):
    current_reservation = Reservation.query.get(reservation_id)
    
    current_projection = Projection.query.get(current_reservation.projection_id)
    current_movie = Movie.query.get(current_projection.movie_id)
    current_screen = Screen.query.get(current_projection.screen_id)

    reservation_dict = { 
        "ID": current_reservation.id,
        "movie_title": current_movie.title,
        "movie_img_str": current_movie.img_str,
        "screen_number": current_screen.number,
        "projection_date": current_projection.date,
        "reservation_owner": current_reservation.user.first_name,
        "no_of_seats": current_reservation.no_of_seats,
        "confirmation_date": current_reservation.conf_date 
    }

    return render_template('reservation_view.html',  user=current_user , UserRole=UserRole, reservation = reservation_dict)

@app.route("/projection/<projection_id>",  methods=['GET', 'POST'])
@login_required
def open_projections_reservations(projection_id):
    current_projection = Projection.query.get(projection_id)
    current_movie = Movie.query.get(current_projection.movie_id)
    current_screen = Screen.query.get(current_projection.screen_id)

    reservations = Reservation.query.filter_by(projection_id = projection_id) 

    all_reservations = [] 

    for reservation in reservations:
        current_user = User.query.get(reservation.user_id)

        reservation_obj = {
            "ID": reservation.id,
            "movie_title": current_movie.title,
            "screen_number": current_screen.number,
            "projection_date": current_projection.date,
            "reservation_owner": reservation.user.first_name,
            "no_of_seats": reservation.no_of_seats,
            "confirmation_date": reservation.conf_date 
        } 
        all_reservations.append(reservation_obj)
    

    return render_template('list_all_reservations.html',  user=current_user , UserRole=UserRole, reservations = all_reservations, current_projection=current_projection, current_movie=current_movie)    

# this is when a customer clicks at my reservation he is redirected to customer view to see his/her past and upcomming reservations
@app.route("/customer",  methods=['GET', 'POST'])
@login_required
def open_customer():
    # from the current user that is loogedin get all reservations 
    reservations = current_user.reservations

    # split from all reservations into past and future list by going through for loop  
    reservation_list_past = [] 
    reservation_list_future = [] 
    for res in reservations:
        current_projection = Projection.query.get(res.projection_id)
        if current_projection.date <= datetime.today():
            reservation_list_past.append(res)
        elif current_projection.date >= datetime.today():    
            reservation_list_future.append(res)  
                  
    # we will append every dict object with the information into this list[] and then give as parameter to render_template (then you can reach from frontend)      
    past_reservation_list = [] 

    # now for past (has to be changed to today) reservations you have to query current_projection , current_movie and current_screen inorder to get the information needed to display on this view
    for reservation in reservation_list_past:
        current_projection = Projection.query.get(reservation.projection_id)
        current_movie = Movie.query.get(current_projection.movie_id)
        current_screen = Screen.query.get(current_projection.screen_id)

        # this object (dict) contains all information needed to be displayed into customer view  
        past_reservation_dict = { 
            "ID": reservation.id,
            "movie_title": current_movie.title,
            "screen_number": current_screen.number,
            "projection_date": current_projection.date,
            "reservation_owner": reservation.user.first_name,
            "no_of_seats": reservation.no_of_seats,
            "confirmation_date": reservation.conf_date 
        }

        past_reservation_list.append(past_reservation_dict)

    # we will append every dict object with the information into this list[] and then give as parameter to render_template (then you can reach from frontend)      
    future_reservation_list = [] 

    # now for future reservations you have to query current_projection , current_movie and current_screen inorder to get the information needed to display on this view
    for reservation in reservation_list_future:
        current_projection = Projection.query.get(reservation.projection_id)
        current_movie = Movie.query.get(current_projection.movie_id)
        current_screen = Screen.query.get(current_projection.screen_id)

        # this object (dict) contains all information needed to be displayed into customer view  
        future_reservation_dict = { 
            "ID": reservation.id,
            "movie_title": current_movie.title,
            "screen_number": current_screen.number,
            "projection_date": current_projection.date,
            "reservation_owner": reservation.user.first_name,
            "no_of_seats": reservation.no_of_seats,
            "confirmation_date": reservation.conf_date 
        }

        future_reservation_list.append(future_reservation_dict)

    return render_template('customer_view.html', user=current_user, UserRole=UserRole, past_reservations=past_reservation_list, future_reservations=future_reservation_list)

@app.route("/changeProjection",  methods=['GET', 'POST'])
@login_required
#manager role required
def open_changeProjection():
    if request.method == 'POST':
        # movie = request.form.get("movie_field")
        # current_movie = Movie.query.get(movie)
        # current_movie = Movie.query.get(projection.movie_id)
        # current_movie = Movie.query.filter(Movie.title == movie).id
        # movie_id = current_movie.id
        movie_query = Movie.query.filter_by(title=request.form.get("movie_field")).first()
        movie_id = movie_query.id
        screen_id = int(request.form.get("screen_field"))
        day = request.form.get("date_field")
        time = request.form.get("time_field")
        date = str(day)+" "+str(time)
        slots_query = Screen.query.filter_by(id=request.form.get("screen_field")).first()
        available_slots = slots_query.capacity
        new_projection = Projection(movie_id=movie_id, screen_id=screen_id, date=date, available_slots = available_slots)
        db.session.add(new_projection)
        db.session.commit()
        return redirect(url_for("open_changeProjection"))
    else:
        future_projections = Projection.query.filter(func.DATE(Projection.date)<datetime.today().strftime("%Y-%m-%d"))
        future_projections_object = []  
        unique_movie_list = []
        unique_movie_id_list = [] 
        date_list = []        
        for projection in future_projections:
            current_movie = Movie.query.get(projection.movie_id)
            projection_dict ={
                "projection_id": projection.id,
                "movie_id": projection.movie_id,
                "movie_title": current_movie.title,
                "screen_id": projection.screen_id,
                "date": projection.date,
                "slots": projection.available_slots
            }   
            future_projections_object.append(projection_dict)
            #for the if statement it would make more senes to iterate over all movies in the database 
            if current_movie.title not in unique_movie_list:
                unique_movie_list.append(current_movie.title)
            if current_movie.title not in unique_movie_id_list:
                unique_movie_id_list.append(current_movie.id)

        for i in range(30):
            date_list.append((datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d"))

        future_projections_list = (list({obj["projection_id"]:obj for obj in future_projections_object}.values()))
        return render_template('add_movie_view.html', user=current_user, UserRole=UserRole, future_projections=future_projections_list, unique_movie_list=unique_movie_list, date_list=date_list, unique_movie_id_list=unique_movie_id_list)

    @app.route("/changeProjection",  methods=['POST'])
    @login_required
    #manager role required
    def post_changeProjection():
        # movie = request.form.get("movie_field")
        # current_movie = Movie.query.get(movie)
        # current_movie = Movie.query.get(projection.movie_id)
        # current_movie = Movie.query.filter(Movie.title == movie).id
        # movie_id = current_movie.id
        movie_query = Movie.query.filter_by(title=movie_field).first()
        movie_id = movie_query.id
        screen_id = request.form.get("screen_field")
        day = request.form.get("date_field")
        time = request.form.get("time_field")
        date = str(day)+" "+str(time)
        available_slots = Screen.query.filter_by(id=screen_id).distinct
        new_projection = Projection(movie_id=movie_id, screen_id=screen_id, date=date, available_slots=available_slots)
        db.session.add(new_projection)
        db.session.commit()
        return redirect(url_for("open_changeProjection"))


if __name__ == '__main__':
    app.run(debug=True)
