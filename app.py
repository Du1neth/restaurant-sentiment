from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
import sys
from pathlib import Path
from functools import wraps
import sqlite3

# Add src to path for importing our existing modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_scraper import RestaurantReviewScraper
from gemini_analyzer import GeminiAnalyzer

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant_sentiment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    companies = db.relationship('Company', backref='owner', lazy=True)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reports = db.relationship('Report', backref='company', lazy=True)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    overall_rating = db.Column(db.Float)
    overall_sentiment = db.Column(db.String(50))
    sources_analyzed = db.Column(db.Integer)
    report_data = db.Column(db.Text)  # JSON string of full analysis
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed

# Helper decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('signup.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    companies = Company.query.filter_by(user_id=session['user_id']).all()
    
    # Get recent reports for each company
    company_reports = {}
    for company in companies:
        reports = Report.query.filter_by(company_id=company.id).order_by(Report.created_at.desc()).limit(3).all()
        company_reports[company.id] = reports
    
    return render_template('dashboard.html', user=user, companies=companies, company_reports=company_reports)

@app.route('/add_company', methods=['GET', 'POST'])
@login_required
def add_company():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        
        company = Company(
            name=name,
            location=location,
            description=description,
            user_id=session['user_id']
        )
        db.session.add(company)
        db.session.commit()
        
        flash('Company added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_company.html')

@app.route('/company/<int:company_id>')
@login_required
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    
    # Check if user owns this company
    if company.user_id != session['user_id']:
        flash('You do not have permission to view this company.', 'error')
        return redirect(url_for('dashboard'))
    
    reports = Report.query.filter_by(company_id=company_id).order_by(Report.created_at.desc()).all()
    
    return render_template('company_detail.html', company=company, reports=reports)

@app.route('/generate_report/<int:company_id>', methods=['POST'])
@login_required
def generate_report(company_id):
    company = Company.query.get_or_404(company_id)
    
    # Check if user owns this company
    if company.user_id != session['user_id']:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Create a new report entry
    report = Report(
        company_id=company_id,
        status='processing'
    )
    db.session.add(report)
    db.session.commit()
    
    try:
        # Load environment variables
        load_env_file()
        
        # Initialize scraper and analyzer
        scraper = RestaurantReviewScraper()
        analyzer = GeminiAnalyzer()
        
        # Extract content
        extracted_content = scraper.scrape_restaurant_reviews(
            restaurant_name=company.name,
            location=company.location or "",
            target_extractions=5
        )
        
        if not extracted_content:
            report.status = 'failed'
            db.session.commit()
            return jsonify({'error': 'No content could be extracted'}), 400
        
        # Analyze content
        analysis = analyzer.analyze_restaurant_content(company.name, extracted_content)
        
        # Update report with results
        report.overall_rating = analysis.overall_rating
        report.overall_sentiment = analysis.overall_sentiment
        report.sources_analyzed = len(extracted_content)
        report.report_data = json.dumps(analysis.model_dump())
        report.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'report_id': report.id,
            'message': 'Report generated successfully!'
        })
        
    except Exception as e:
        report.status = 'failed'
        db.session.commit()
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500

@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if user owns this report
    if report.company.user_id != session['user_id']:
        flash('You do not have permission to view this report.', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse report data
    report_data = json.loads(report.report_data) if report.report_data else {}
    
    return render_template('report_detail.html', report=report, report_data=report_data)

@app.route('/api/report_status/<int:report_id>')
@login_required
def report_status(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if user owns this report
    if report.company.user_id != session['user_id']:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify({
        'status': report.status,
        'id': report.id,
        'created_at': report.created_at.isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)