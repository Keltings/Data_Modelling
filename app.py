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
from models import Venue, Show, Artist

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

  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  for area in areas:
      venues_in_area = db.session.query(Venue.id, Venue.name).filter(Venue.city == area[0]).filter(Venue.state == area[1])
      data.append({
        "city": area[0],
        "state": area[1],
        "venues": venues_in_area
      })  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # find all venues matching a word and should be case insesitive
  venue_searched = request.form.get('search_term', '')
  venue_queried = Venue.query.filter(Venue.name.ilike('%' + venue_searched + '%'))
  response={
    "count": venue_queried.count(),
    "data": venue_queried
  }
  return render_template('pages/search_venues.html', results=response, search_term=venue_searched)



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # get all venues by the venue_id
  queried_venue = Venue.query.filter_by(id=venue_id).first()
  #also get all shows using the venue id as a filter
  queried_show = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).all()
  new_shows = []
  past_shows = []

#future shows
  for show in queried_show:
    if show.start_time > datetime.now():
      new_shows.append({"artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).all().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).all().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })

#past shows 
  for show in queried_show:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    if show.start_time < datetime.now():
      past_shows.append({
               "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": format_datetime(str(show.start_time)),
                })
  
  if queried_venue:
    venue={
      "id": queried_venue.id,
      "name":queried_venue.name,
      "genres": queried_venue.genres,
      "address": queried_venue.address,
      "city": queried_venue.city,
      "state": queried_venue.state,
      "phone": queried_venue.phone,
      "website": queried_venue.website_link,
      "facebook_link": queried_venue.facebook_link,
      "looking_talent": queried_venue.looking_talent,
      "seeking_description": queried_venue.seeking_description,
      "image_link": queried_venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": new_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(new_shows),
  }
  
    return render_template('pages/show_venue.html', venue=venue)
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
  form = VenueForm(request.form)
  
  #venue = Venue.query.filter_by(id=venue_id).first()
  

  venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link  = form.website_link.data,
        looking_talent= form.looking_talent.data,
        seeking_description = form.seeking_description.data,
        genres = request.form.getlist('genres'),
  
      ) 
  
    
  try:
    if form.validate():  
      db.session.add(venue)
      db.session.commit()
    # TODO: on unsuccessful db insert, flash an error instead.

      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully listed!')
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')  
  except:
      error=True
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
      print(sys.exc_info())
  finally:
      db.session.close()
      
  
  return render_template('pages/home.html', form=form)



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

   response = {
    "count": artist_queried,
    "data": artist_searched
  }
   return render_template('pages/search_artists.html', results=response, search_term=artist_searched)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # get all venues by the venue_id
  queried_artist = Artist.query.filter_by(id=artist_id).first()
  #also get all shows using the venue id as a filter
  queried_show = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).all()
  new_shows = []
  new_shows = []
  past_shows = []

  for show in queried_show:
      venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()

      if (show.start_time < datetime.now()):
            #print(past_shows, file=sys.stderr)
          past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": format_datetime(str(show.start_time))
            })
      else:
          print({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": format_datetime(str(show.start_time))
            }, file=sys.stderr)
          new_shows.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": format_datetime(str(show.start_time))
            })

  artist = {
        "id": queried_artist.id,
        "name": queried_artist.name,
        "genres": queried_artist.genres,
        "city": queried_artist.city,
        "state": queried_artist.state,
        "phone": queried_artist.phone,
        "website": queried_artist.website,
        "facebook_link": queried_artist.facebook_link,
        "seeking_venue": queried_artist.seeking_venue,
        "seeking_description": queried_artist.looking_description,
        "image_link": queried_artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": new_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(new_shows),
    }
  return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  queried_artist = Artist.query.filter_by(id=artist_id).first()

  if queried_artist:
    artist={
     "id": queried_artist.id,
      "name": queried_artist.name,
      "genres": queried_artist.genres,
      "city": queried_artist.city,
      "state": queried_artist.state,
      "phone": queried_artist.phone,
      "website": queried_artist.website,
      "facebook_link": queried_artist.facebook_link,
      "seeking_venue": queried_artist.seeking_venue,
      "seeking_description": queried_artist.looking_description,
      "image_link": queried_artist.image_link
    }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  
  form = ArtistForm()
  #get the data
  queried = Artist.query.filter_by(id=artist_id).first()
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
      # on successful db insert, flash success
      flash('Venue ' + artist.name+ ' was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
      error=True
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()
  
    return render_template('pages/home.html')

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()
  queried_venue = Venue.query.filter_by(id=venue_id).first()
  
  return render_template('forms/edit_venue.html', form=form, venue=queried_venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  form =  VenueForm()
  # get the data
  queried = Venue.query.filter_by(id=venue_id).first()
  if form.validate():
    try:
      venue = Venue(
        name = request.form.name,
        city = request.form.city,
        state = request.form.state,
        address = request.form.address,
        phone = request.form.phone,
        image_link = request.form.image_link,
        facebook_link = request.form.facebook_link,
        website_link = request.form.website_link,
        looking_talent = request.form.looking_talent,
        seeking_description = request.form.seeking_description,
        genres = request.form.genres

      )
      db.session.add(venue)
      db.session.commit()
    except:
      error=True
      db.session.rollback()
    finally:
      db.session.close()     
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

  error = False
  #get the data
  form = ArtistForm(request.form)
  
  artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = request.form.getlist('genres'),
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website  = form.website.data,
        seeking_venue= form.seeking_venue.data,
        looking_description = form.looking_description.data,
        
  
      )
  
  try:   
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.

    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    error=True
    db.session.rollback()
    flash('An error occurred. Venue ' + artist.name + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  
  return render_template('pages/home.html', form=form)


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
              'artist_name': Artist.query.filter_by(id=show.artist_id).first().name,
              'artist_image_link': Artist.query.filter_by(id=show.artist_id).first().image_link,
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
