"""
Create Admin User Script
Run this to create a new admin or promote an existing user
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_admin():
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 50)
        print("🔐 ADMIN USER CREATION")
        print("=" * 50)
        
        username = input("\nEnter admin username: ").strip()
        
        # Check if user exists
        existing = User.query.filter_by(username=username).first()
        
        if existing:
            # Promote existing user
            existing.role = 'admin'
            db.session.commit()
            print(f"\n✅ User '{username}' has been promoted to ADMIN!")
        else:
            # Create new admin
            email = input("Enter admin email: ").strip()
            password = input("Enter admin password: ").strip()
            
            admin = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print(f"\n✅ Admin user '{username}' created successfully!")
        
        # Show all admins
        admins = User.query.filter_by(role='admin').all()
        print(f"\n📋 Current admins: {', '.join([a.username for a in admins])}")
        print("=" * 50)


if __name__ == '__main__':
    create_admin()
