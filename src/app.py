from flask import Flask, render_template, request, redirect, url_for, flash, session
from application.ontology_service import OntologyService
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  

ontology_path = os.path.join(os.path.dirname(__file__), '../data/data.rdf')
service = OntologyService(ontology_path)
service.load_ontology()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['userName']
        email = request.form['email']
        
        user = service.get_user(username, email)
        if user:
            session['user'] = username
            return redirect(url_for('list_musics'))
        else:
            flash('Invalid username or email.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['userName']
        birth_year = request.form['birthYear']
        email = request.form['email']
        
        try:
            service.register_user(username, birth_year, email)
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'error')
    
    return render_template('register.html')

@app.route('/musics')
@login_required
def musics():
    return redirect(url_for('list_musics'))

@app.route('/list_musics')
@login_required
def list_musics():
    search = request.args.get('search', '')
    order_by = request.args.get('order_by', 'title')
    order_dir = request.args.get('order_dir', 'asc')
    limit = request.args.get('limit', '10')
    
    try:
        limit = int(limit)
    except ValueError:
        limit = 10
    
    musics = service.list_musics(limit=limit, search=search, order_by=order_by, order_dir=order_dir, user_name=session['user'])
    
    for music in musics:
        user_rating = service.get_user_rating(session['user'], music['title'])
        music['user_rating'] = user_rating
    
    return render_template('rate_music.html', musics=musics, user=session['user'])

@app.route('/rate', methods=['POST'])
@login_required
def rate_music():
    submit_rating = request.form.get('submit_rating')
    if not submit_rating:
        flash('No rating selected.', 'error')
        return redirect(url_for('list_musics'))
    
    music_title = submit_rating
    rating_key = f'rating_{music_title}'
    genre_key = f'genre_{music_title}'
    stars_str = request.form.get(rating_key)
    genre = request.form.get(genre_key)
    
    if not stars_str:
        flash('Please select a rating.', 'error')
        return redirect(url_for('list_musics'))
    
    if not genre:
        flash('Genre information is missing.', 'error')
        return redirect(url_for('list_musics'))
    
    try:
        stars = int(stars_str)
        if stars < 1 or stars > 5:
            flash('Rating must be between 1 and 5.', 'error')
            return redirect(url_for('list_musics'))
    except ValueError:
        flash('Invalid rating value.', 'error')
        return redirect(url_for('list_musics'))
    
    try:
        service.add_rating(session['user'], music_title, genre, stars)
        flash(f'Rating added for {music_title}!', 'success')
    except Exception as e:
        flash(str(e), 'error')
    
    return redirect(url_for('list_musics'))

@app.route('/recommendations')
@login_required
def recommendations():
    limit = request.args.get('limit', '10')
    search = request.args.get('search', '')
    try:
        limit = int(limit)
    except ValueError:
        limit = 10
    
    recommended_musics = service.list_recommended_musics(session['user'], 1000)
    if search:
        filtered_musics = []
        for music in recommended_musics:
            if search.lower() in music['title'].lower():
                filtered_musics.append(music)
        recommended_musics = filtered_musics

    recommended_musics = recommended_musics[:limit]
    
    return render_template('recommended.html', 
                         musics=recommended_musics, 
                         user=session['user'], 
                         limit=limit,
                         search=search)

@app.route('/add_music', methods=['GET', 'POST'])
@login_required
def add_music():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        singer = request.form['singer']
        genre = request.form['genre']
        
        try:
            service.add_music(title, year, singer, genre)
            flash('Music added successfully!', 'success')
            return redirect(url_for('list_musics'))
        except Exception as e:
            flash(str(e), 'error')
    
    return render_template('add_music.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
