#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from dataclasses import dataclass
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:#Datascience1@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String())
    looking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String())
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True)

    #debugging statements when printing the objects
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=True)
    looking_description = db.Column(db.String())
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#db.create_all()
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    def __repr__(self):
        return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  #query all the venues in the db
  venues = Venue.query.all()
  areas = set()
  

  

  for area in areas:
    list_of_venues = []
    for venue in venues:
    # add the town +state as a tuples
      areas.add((venues.city, venue.state))
      new_shows = [show for show in venue.shows if show.start_time > datetime.now]
      if (venue.city == areas[0]) and (venue.state == areas[1]):
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
      list_of_venues.append({
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows": new_shows
        })  

    data.append({
      "city": areas[0],
      "state": areas[1],
      "venues": list_of_venues
    })


  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # find all venues matching a word and should be case insesitive
  venue_searched = request.form.get('search_term', '')
  venue_queried = Venue.query.filter(Venue.name.ilike('%' + venue_searched + '%')).count()
  response={
    "count": venue_queried,
    "data": venue_queried
  }
  return render_template('pages/search_venues.html', results=response, search_term=venue_searched)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # get all venues by the venue_id
  venues = Venue.query.filter_by(id=venue_id).first()
  #also get all shows using the venue id as a filter
  shows = Show.query.filter_by(venue_id=venue_id).all()
  new_shows = []
  past_shows = []

#future shows
  for show in shows:
    if show.start_time > datetime.now():
      new_shows.append({"artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).all().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).all().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })


#past shows 
  for show in shows:
    if show.start_time < datetime.now():
      past_shows.append({
               "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).all().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).all().image_link,
                "start_time": format_datetime(str(show.start_time))
                })
  if venues:
    data={
      "id": venues.id,
      "name":venues.name,
      "genres": venues.genres,
      "address": venues.address,
      "city": venues.city,
      "state": venues.state,
      "phone": venues.phone,
      "website": venues.website,
      "facebook_link": venues.facebook_link,
      "looking_talent": venues.looking_talent,
      "seeking_description": venues.seeking_description,
      "image_link": venues.image_link,
      "past_shows": past_shows,
      "upcoming_shows": new_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(new_shows),
  }
  
    return render_template('pages/show_venue.html', venue=data)
  return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  #get the data
  form = VenueForm()
  #venue = Venue.query.filter_by(id=venue_id).first()
  if form.validate():

    try:

      venue = Venue(
        name= request.form['name'],
        city = request.form['city'],
        state= request.form['state'],
        address= request.form['address'],
        phone= request.form['phone'],
        image_link= request.form['image_link'],
        facebook_link= request.form['facebook_link'],
        website_link= request.form['website_link'],
        looking_talent = request.form['looking_talent '],
        seeking_description = request.form['seeking_description '],
        genres= request.form.getlist('genres'),
      
    ) 
      db.session.add(venue)
      db.session.commit()
    except:
      error=True
      db.session.rollback()
      flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()
  

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
      db.session.rollback()
      flash('Venue Could not be Deleted')
  finally:
      db.session.close()
   

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists = Artist.query.all()

  for artist in artists:
    new_show = db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(new_show)
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
   artist_searched = request.form.get('search_term', '')
   artist_queried = Artist.query.filter(Venue.name.ilike('%' + artist_searched + '%')).count()
   artist_data = []
   for artist in artists:

    new_show = db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()
    artist_data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(new_show)
    })
  
   response = {
    "count": len(artists),
    "data": artist_data
  }
   return render_template('pages/search_artists.html', results=response, search_term=artist_searched)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # get all venues by the venue_id
  artists = Artist.query.filter_by(id=artist_id).first()
  #also get all shows using the venue id as a filter
  shows = Show.query.filter_by(artist_id=artist_id).all()
  new_shows = []
  past_shows = []

#future shows
  for show in shows:
    if show.start_time > datetime.now():
      new_shows.append({"venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(id=show.vene_id).all().name,
                    "venue_image_link": Venue.query.filter_by(id=show.venue_id).all().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })


#past shows 
  for show in shows:
    if show.start_time < datetime.now():
      past_shows.append({
               "venue_id": show.artist_id,
                "venue_name": Venue.query.filter_by(id=show.artist_id).all().name,
                "venue_image_link": Venue.query.filter_by(id=show.venue_id).all().image_link,
                "venue_time": format_datetime(str(show.start_time))
                })
  if artists:
    data={
      "id": artists.id,
      "name":artists.name,
      "city": artists.city,
      "state": artists.state,
      "phone": artists.phone,
      "genres": artists.genres,
      "address": artists.address,
      "image_link": artists.image_link,
      "facebook_link": artists.facebook_link,
      "website": artists.website,
      "looking_talent": artists.looking_talent,
      "seeking_description": artists.seeking_description,
      "past_shows": past_shows,
      "upcoming_shows": new_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(new_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  queried = Artist.query.filter_by(id=artist_id).first()

  if queried:
    artist={
     "id": artist.id,
      "name": artist.name,
      "genres": [genre.name for genre in artist.genres],
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.looking_description,
      "image_link": artist.image_link
    }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  #get the data
  queried = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm()
  if form.validate():

    try:

      artist = Artist(
        name= request.form['name'],
        genres= request.form.getlist('genres'),
        city = request.form['city'],
        state= request.form['state'],
        phone= request.form['phone'],
        website_link= request.form['website_link'],
        facebook_link= request.form['facebook_link'],
        image_link= request.form['image_link'],
        seeking_venue= request.form['seeking_venue'],
        seeking_description = request.form['looking_description']
    ) 
      
      db.session.add(artist)
      db.session.commit()
    except:
      error=True
      db.session.rollback()
      flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()
  

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm()
  body = {}
  error=False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = form.form['website']
    seeking_venue = request.form['seeking_venue']
    looking_description = request.form['looking_description']
    
    artist = Artist(
      name=name, city=city, state=state, phone=phone, genres=genres,
      image_link=image_link, facebook_link=facebook_link,website=website,
      seeking_venue=seeking_venue, looking_description=looking_description
    )
    
    db.session.add(artist)
    db.session.commit()
    body['id'] = artist.id
    body['name'] = artist.name
    body['city'] = artist.city
    body['state'] = artist.state
    body['phone'] = artist.phone
    body['genres'] = artist.genres
    body['image_link'] = artist.image_link
    body['facebook_link'] = artist.facebook_link
    body['website'] = artist.website
    body['seeking_venue'] = artist.seeking_venue
    body['looking_description'] = artist.looking_description
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    error=True
    db.session.rollback()
    flash(flash('An error occurred. Artist ' + artist.name + ' could not be listed.'))
    print(sys.exc_info())

  finally:
    db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  # initialize an empty list
  show_list = []
  # iterate through all the shows in the database
  for show in shows:
    details = {'venue_id': show.venue_id ,
              'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
              'artist_id': show.artist_id,
              'artist_name': Artist.query.filter_by(id-show.artist_id).first().name,
              'artist_image_link': Artist.query.fillter_by(id-show.artist_id).first().image_link,
              'start_time': format_datetime(str(show.start_time))
              }
    # append it to the empty list          
    show_list.append(details)          
  # returns show page with show metadata
  return render_template('pages/shows.html', shows=show_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  body = {}
  error=False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    
    db.session.add(show)
    db.session.commit()
    body['id'] = show.id
    body['artist_id'] = show.artist_id
    body['venue_id'] = show.venue_id
    body['start_time'] = show.start_time
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
      error=True
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
      print(sys.exc_info())
  finally:
        db.session.close()
  
  # TODO: on unsuccessful db insert, flash an error instead.
   
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
