from enum import unique
import enum
from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func

#this is a one to many relationship (one user has many notes) 
#so the foreign key shown below is only for one to many relationships.


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(5000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class UserRole(enum.Enum):
    customer = 1
    manager = 2

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_str = db.Column(db.String(5000),nullable=False)
    title = db.Column(db.String(5000),nullable=False)
    synopsis = db.Column(db.Text(4294000000), nullable=False)
    duration = db.Column(db.Integer, nullable=False)#in minutes 
    director = db.Column(db.String(5000), nullable=False)
    main_cast = db.Column(db.String(5000), nullable=False)

class Screen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer,nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(1000))
    role = db.Column(db.Enum(UserRole), nullable=False)
    reservations = db.relationship(
        "Reservation", backref="user",lazy=True)
    notes = db.relationship('Note') 

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    projection_id = db.Column(db.Integer, db.ForeignKey("projection.id"), nullable=False)
    no_of_seats = db.Column(db.Integer, nullable=False)
    conf_date = db.Column(db.DateTime, nullable=False)

class Projection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    screen_id = db.Column(db.Integer, db.ForeignKey("screen.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    

    # insert into movie (img_str,title,synopsis,duration,director,main_cast) values ('./static/img/matrix.jpg','matrix','best movie',140,'sibora','sibo'); 
    # delete from movie where movie.title = 'Dune'; 
    # insert into screen (number,capacity) values (100, 50);
    # insert into projection (movie_id,screen_id, date) values (2,2,'2021-11-25 20:30:00'); 
    # update movie set img_str = "../static/img/noTimeToDie.jpg" where movie.title="No Time To Die"; 

    # insert into reservation (user_id,projection_id) values (1, 1);

