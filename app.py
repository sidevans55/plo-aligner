from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime
import json

# Import the CPF comparison logic
from cpf_comparison import CPFComparator

app = Flask(__name__)

# Environment Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '5fea2ab7e8bffbdd07b445603f4d37dd4dfe1945da2ee04851f877bc75486f9b')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///plo_platform.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class Institution(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    plo_submissions = db.relationship('PLOSubmission', backref='institution', lazy=True)

class PLOSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    submission_name = db.Column(db.String(100), nullable=False)
    plos_data = db.Column(db.Text, nullable=False)  # JSON string of PLOs
    comparison_results = db.Column(db.Text)  # JSON string of results
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Institution, int(user_id))

# Initialize CPF Comparator
cpf_comparator = CPFComparator()

# Make enumerate available in templates
with app.app_context():
    app.jinja_env.globals.update(enumerate=enumerate)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if Institution.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        institution = Institution(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(institution)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        institution = Institution.query.filter_by(email=email).first()
        
        if institution and check_password_hash(institution.password_hash, password):
            login_user(institution)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    submissions = PLOSubmission.query.filter_by(institution_id=current_user.id).order_by(PLOSubmission.submitted_at.desc()).all()
    return render_template('dashboard.html', submissions=submissions)

@app.route('/compare', methods=['GET', 'POST'])
@login_required
def compare_plos():
    if request.method == 'POST':
        submission_name = request.form['submission_name']
        plos_text = request.form['plos_text']
        
        # Parse PLOs from text (one per line)
        plos_list = [plo.strip() for plo in plos_text.split('\n') if plo.strip()]
        
        if not plos_list:
            flash('Please enter at least one PLO')
            return redirect(url_for('compare_plos'))
        
        # Perform comparison
        results = cpf_comparator.compare_plos(plos_list)
        
        # Save submission
        submission = PLOSubmission(
            institution_id=current_user.id,
            submission_name=submission_name,
            plos_data=json.dumps(plos_list),
            comparison_results=json.dumps(results),
            status='completed'
        )
        db.session.add(submission)
        db.session.commit()
        
        return render_template('results.html', results=results, submission_name=submission_name)
    
    return render_template('compare.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        # Check file extension
        allowed_extensions = {'.csv', '.xlsx', '.xls', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            flash(f'Please upload a supported file type: {", ".join(allowed_extensions)}')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read file and extract PLOs
            try:
                plos_list = []
                
                if file_ext == '.csv':
                    df = pd.read_csv(filepath)
                    # Try common column names for PLOs
                    plo_columns = ['PLO', 'Learning Outcome', 'Outcome', 'PLO Text', 'Description']
                    plo_col = None
                    for col in plo_columns:
                        if col in df.columns:
                            plo_col = col
                            break
                    
                    if plo_col:
                        plos_list = df[plo_col].dropna().astype(str).tolist()
                    else:
                        # Use first column if no PLO column found
                        plos_list = df.iloc[:, 0].dropna().astype(str).tolist()
                
                elif file_ext in ['.xlsx', '.xls']:
                    df = pd.read_excel(filepath)
                    # Try common column names for PLOs
                    plo_columns = ['PLO', 'Learning Outcome', 'Outcome', 'PLO Text', 'Description']
                    plo_col = None
                    for col in plo_columns:
                        if col in df.columns:
                            plo_col = col
                            break
                    
                    if plo_col:
                        plos_list = df[plo_col].dropna().astype(str).tolist()
                    else:
                        # Use first column if no PLO column found
                        plos_list = df.iloc[:, 0].dropna().astype(str).tolist()
                
                elif file_ext == '.txt':
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Split by lines and filter out empty lines
                        plos_list = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Filter out empty strings and clean up
                plos_list = [plo.strip() for plo in plos_list if plo.strip() and plo.strip() != 'nan']
                
                if not plos_list:
                    flash('No valid PLOs found in the uploaded file. Please check the file format.')
                    os.remove(filepath)
                    return redirect(request.url)
                
                # Perform comparison
                results = cpf_comparator.compare_plos(plos_list)
                
                # Save submission
                submission = PLOSubmission(
                    institution_id=current_user.id,
                    submission_name=f"Upload: {filename}",
                    plos_data=json.dumps(plos_list),
                    comparison_results=json.dumps(results),
                    status='completed'
                )
                db.session.add(submission)
                db.session.commit()
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return render_template('results.html', results=results, submission_name=f"Upload: {filename}")
                
            except Exception as e:
                # Clean up file on error
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error processing file: {str(e)}. Please ensure the file contains valid PLO data.')
                return redirect(request.url)
        else:
            flash('Please upload a valid file')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/submission/<int:submission_id>')
@login_required
def view_submission(submission_id):
    submission = PLOSubmission.query.get_or_404(submission_id)
    
    # Ensure user can only view their own submissions
    if submission.institution_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    results = json.loads(submission.comparison_results)
    plos_data = json.loads(submission.plos_data)
    
    return render_template('submission_detail.html', 
                         submission=submission, 
                         results=results, 
                         plos_data=plos_data)

@app.route('/api/compare', methods=['POST'])
def api_compare():
    data = request.get_json()
    plos = data.get('plos', [])
    
    if not plos:
        return jsonify({'error': 'No PLOs provided'}), 400
    
    results = cpf_comparator.compare_plos(plos)
    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Run on all network interfaces for local network sharing
    app.run(debug=True, host='0.0.0.0', port=5000)

# For Vercel deployment
app.debug = False 