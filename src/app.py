from flask import Flask, render_template, request, redirect, url_for, flash
from application.ontology_service import OntologyService
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  

ontology_path = os.path.join(os.path.dirname(__file__), '../data/graph.owl')
service = OntologyService(ontology_path)
service.load_ontology()

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userName = request.form['userName']
        birthYear = request.form['birthYear']
        email = request.form['email']
        try:
            service.register_user(userName, birthYear, email)
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {str(e)}', 'danger')
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
            flash('Música adicionada com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao adicionar música: {str(e)}', 'danger')
        return redirect(url_for('add_music'))
    return render_template('add_music.html')

if __name__ == "__main__":
    app.run(debug=True)
