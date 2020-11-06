from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy


# Const variables for PSQL connection
DATABASE_NAME = 'dbimdb'
USER = 'postgres'
PASSWORD = 'tak123'
HOST = 'localhost'

# flask app config
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER}:{PASSWORD}@{HOST}/{DATABASE_NAME}'
db = SQLAlchemy(app)

###################################################################
# Database models (models were created by using "sqlacodegen" lib)
###################################################################


# Name model
class Name(db.Model):
    __tablename__ = 'name'

    nconst = db.Column(db.Text, primary_key=True)
    primaryname = db.Column(db.Text)
    birthyear = db.Column(db.Text)
    deathyear = db.Column(db.Text)
    primaryprofession = db.Column(db.Text)
    knownfortitles = db.Column(db.Text)


# Title model
class Title(db.Model):
    __tablename__ = 'title'

    tconst = db.Column(db.Text, primary_key=True)
    titletype = db.Column(db.Text)
    primarytitle = db.Column(db.Text)
    originaltitle = db.Column(db.Text)
    isadult = db.Column(db.Text)
    startyear = db.Column(db.Text)
    endyear = db.Column(db.Text)
    runtimeminutes = db.Column(db.Text)
    genres = db.Column(db.Text)


########################
# app routes
########################


# "/" main route
@app.route('/', methods=['GET', "POST"])
def home():
    if request.method == 'GET':
        return render_template("main_base.html")

    elif request.method == 'POST':

        # variable task is value from select bar
        task = request.form.get("types")
        # variable value is value from input box
        value = request.form.get('phrase')

        # redirect to search endpoint
        return redirect(f'/{task}/{value}/0')


# app.rout example /year/1999/30
@app.route('/year/<year>/<nr1>', methods=['GET'])
def search_year(year, nr1):
    if request.method == 'GET':

        # website counter - counts on witch website are you on
        # (for example - /year/1999/2 is data base values from 20 - 29 etc.)
        website_counter = int(nr1) * 10

        # Returns 10 data base rows with startYear == year, order them in alphabetical order
        # order_by - orders them in alphabetical order
        # offset - start taking values from certain point
        # limit - limits values (shows only 10 values)
        all_moves_in_certain_year = Title.query.filter_by(startyear=year)\
            .order_by(Title.primarytitle.name)\
            .offset(website_counter)\
            .limit(10)\
            .all()

        # list for all actors that played in movie (from above)
        all_actors_list = []

        # for loop that search for all actors that act in movies in certain year
        for movie in all_moves_in_certain_year:
            pom = movie.tconst
            # Returns all data base rows with if knownForTitles contains title from list all_moves_in_certain_year
            # order_by - orders them in alphabetical order
            # offset - start taking values from certain point
            # limit - limits values (shows only 10 values)
            actor_list = Name.query\
                .filter(Name.knownfortitles.contains(str(pom)))\
                .order_by(Name.primaryname.name)\
                .all()
            all_actors_list.append(actor_list)

        # zip 2 lists for template bellow
        zipped = zip(all_actors_list, all_moves_in_certain_year)

        # return template
        return render_template('year.html', movies=zipped)

    else:

        return render_template('home.html')

# app.rout example /year/Comedy/20
@app.route('/genre/<genre>/<nr1>', methods=['GET'])
def search_genre(genre, nr1):
    if request.method == 'GET':

        # website counter - counts on witch website are you on
        # (for example - /genre/Comedy/2 is data base values from 20 - 29 etc.)
        website_counter = int(nr1) * 10

        # Returns 10 table rows on condition if 'genres' contains that 'genre'
        # order_by - orders them in alphabetical order
        # offset - start taking values from certain point
        # limit - limits values (shows only 10 values)
        movie_titles = Title.query\
            .filter(Title.genres.contains(genre))\
            .order_by(Title.primarytitle.name) \
            .offset(website_counter)\
            .limit(10)\
            .all()

        # list for all actors that played in movie (from above)
        all_actors = []

        for movie in movie_titles:

            pom = movie.tconst

            # look for actors that are connected for certain movie title
            actor_list = Name.query\
                .filter(Name.knownfortitles.contains(str(pom)))\
                .all()

            # add actors to all actor list
            all_actors.append(actor_list)

        # zip for template render
        zipped = zip(all_actors, movie_titles)

        return render_template('genre.html', movies=zipped)

    else:

        return render_template('home.html')

# app.rout example actor/arnold/1
@app.route('/actor/<phrase>/<nr1>', methods=['GET'])
def search(phrase, nr1):
    if request.method == 'GET':

        # website counter - counts on witch website are you on
        # (for example - /actor/Cris/2 is data base values from 20 - 29 etc.)
        website_counter = int(nr1) * 10

        # Returns 10 table rows on condition if 'primaryname' contains that 'phrase'
        # order_by - orders them in alphabetical order
        # offset - start taking values from certain point
        # limit - limits values (shows only 10 values)
        looking_for_actors_list = Name.query.filter(Name.primaryname.contains(str(phrase)))\
            .order_by(Name.primaryname.name) \
            .offset(website_counter) \
            .limit(10)\
            .all()

        # list of all matching titles
        all_titles_list = []

        # list of matching titles for certain actor
        title_list = []

        # for loop splits known for titles witch look like this "tt9329323,tt23124215.."
        for actor in looking_for_actors_list:
            all_titles_list = str(actor.knownfortitles).split(',')

            # for loop search second database for matching values for one actor
            for title in all_titles_list:
                actor_list = Title.query.filter(Title.tconst.contains(title)).first()
                title_list.append(actor_list)

            # append search result to all_title_list and clear title list for next search
            all_titles_list.append(title_list)
            title_list = []

        # zip lists
        zipped = zip(all_titles_list, looking_for_actors_list)

        return render_template('actor.html', movies=zipped)

    else:

        return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
