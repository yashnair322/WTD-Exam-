import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, validators
from flask_wtf import FlaskForm
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Enable CSRF protection
csrf = CSRFProtect(app)

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Contact model
class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Contact {self.name}>'

# Form with validation
class ContactForm(FlaskForm):
    name = StringField('Name', [
        validators.Length(min=2, max=100),
        validators.Regexp(r'^[a-zA-Z\s]+$', message="Name can only contain letters and spaces")
    ])
    email = StringField('Email', [
        validators.Email(message='Please enter a valid email address'),
        validators.Length(max=100)
    ])
    subject = StringField('Subject', [
        validators.Length(max=200),
        validators.Optional()
    ])
    message = TextAreaField('Message', [
        validators.Length(min=10, message='Message must be at least 10 characters long'),
        validators.DataRequired()
    ])

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    if form.validate_on_submit():
        try:
            # Create new contact entry
            new_contact = Contact(
                name=form.name.data,
                email=form.email.data,
                subject=form.subject.data,
                message=form.message.data
            )
            
            # Add to database
            db.session.add(new_contact)
            db.session.commit()
            
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while sending your message. Please try again.', 'danger')
            app.logger.error(f"Error occurred: {str(e)}")
    
    # Pass form errors to template
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return render_template('contact.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
