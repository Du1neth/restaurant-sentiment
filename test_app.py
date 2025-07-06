#!/usr/bin/env python3
"""
Test script for the SentimentEats Flask application
"""

from app import app, db, User, Company, Report
import tempfile
import os

def test_application():
    """Test the Flask application basic functionality"""
    
    # Use a temporary database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Test database models
        print("✅ Database models created successfully")
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(test_user)
        db.session.commit()
        print("✅ Test user created successfully")
        
        # Create test company
        test_company = Company(
            name='Test Restaurant',
            location='Test City',
            description='A test restaurant for development',
            user_id=test_user.id
        )
        db.session.add(test_company)
        db.session.commit()
        print("✅ Test company created successfully")
        
        # Create test report
        test_report = Report(
            company_id=test_company.id,
            overall_rating=4.5,
            overall_sentiment='positive',
            sources_analyzed=10,
            report_data='{"test": "data"}',
            status='completed'
        )
        db.session.add(test_report)
        db.session.commit()
        print("✅ Test report created successfully")
        
        # Test queries
        users = User.query.all()
        companies = Company.query.all()
        reports = Report.query.all()
        
        print(f"✅ Found {len(users)} users, {len(companies)} companies, {len(reports)} reports")
        
        # Test Flask routes
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Home page loads successfully")
            
            # Test login page
            response = client.get('/login')
            assert response.status_code == 200
            print("✅ Login page loads successfully")
            
            # Test signup page
            response = client.get('/signup')
            assert response.status_code == 200
            print("✅ Signup page loads successfully")
            
            print("\n🎉 All tests passed! The application is working correctly.")
            print("\nTo run the web application:")
            print("1. Set up your .env file with API keys")
            print("2. Run: python app.py")
            print("3. Visit: http://localhost:5000")

if __name__ == '__main__':
    test_application()