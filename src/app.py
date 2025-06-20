from flask import Flask, render_template, request, redirect, url_for, flash, session
from application.ontology_service import OntologyService
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  

ontology_path = os.path.join(os.path.dirname(__file__), '../data/graph.owl')
service = OntologyService(ontology_path)
service.load_ontology()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('rate_music'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userName = request.form['userName']
        birthYear = request.form['birthYear']
        email = request.form['email']
        try:
            service.register_user(userName, birthYear, email)
            flash('User registered successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            if 'already exists' in str(e):
                session['user'] = {'userName': userName, 'email': email}
                flash('User already exists. Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Error registering user: {str(e)}', 'danger')
    return render_template('register.html')

@app.route('/add-music', methods=['GET', 'POST'])
def add_music():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        singer = request.form['singer']
        genre = request.form['genre']
        try:
            service.add_music(title, year, singer, genre)
            flash('Song added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding song: {str(e)}', 'danger')
        return redirect(url_for('add_music'))
    return render_template('add_music.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form['userName']
        email = request.form['email']
        user = service.get_user(userName, email)
        if user:
            session['user'] = {'userName': userName, 'email': email}
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or email.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))

@app.route('/rate-music', methods=['GET', 'POST'])
@login_required
def rate_music():
    # Get query params for limit, search, order_by, order_dir
    limit = request.args.get('limit', default=10, type=int)
    search = request.args.get('search', default='', type=str)
    order_by = request.args.get('order_by', default='title', type=str)
    order_dir = request.args.get('order_dir', default='asc', type=str)
    user = session.get('user')
    user_name = user['userName'] if user else None
    musics = service.list_musics(limit=limit, search=search, order_by=order_by, order_dir=order_dir, user_name=user_name)
    for m in musics:
        if 'user_rating' not in m:
            m['user_rating'] = service.get_user_rating(user_name, m['title']) if user_name else None
    if request.method == 'POST':
        music_title = request.form['submit_rating']
        rating_value = request.form.get(f'rating_{music_title}')
        if rating_value:
            user = session['user']
            try:
                service.add_rating(user['userName'], music_title, int(rating_value))
                flash(f'Rating {rating_value} registered for {music_title}!', 'success')
            except Exception as e:
                flash(f'Error registering rating: {str(e)}', 'danger')
        else:
            flash('Please select a rating.', 'warning')
        return redirect(url_for('rate_music', limit=limit, search=search, order_by=order_by, order_dir=order_dir))
    return render_template('rate_music.html', musics=musics, limit=limit, search=search, order_by=order_by, order_dir=order_dir)

if __name__ == "__main__":
    app.run(debug=True)
