from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message as MailMessage
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Sandricksoni729'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Flask-Mail კონფიგურაცია
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sandricksoni@gmail.com'
app.config['MAIL_PASSWORD'] = 'isiv iqey coyf vstd'
app.config['MAIL_DEFAULT_SENDER'] = 'sandricksoni@gmail.com'

mail = Mail(app)

@app.route('/')
def home():
    return render_template('index.html')

# 🔹 ვერიფიცირებული ელფოსტების მოდელი
class VerifiedEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)


# 🔹 მესიჯების მოდელი
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())


# 🔹 კონტაქტის ფორმა
class ContactForm(FlaskForm):
    name = StringField('სახელი', validators=[DataRequired()])
    email = StringField('ელ.ფოსტა', validators=[DataRequired(), Email()])
    message = TextAreaField('შეტყობინება', validators=[DataRequired()])
    submit = SubmitField('გაგზავნა')


# 🔹 ვერიფიკაციის ფუნქცია
def send_verification_email(user_email):
    s = Serializer(app.config['SECRET_KEY'])
    token = s.dumps({'email': user_email})

    verification_link = url_for('verify_email', token=token, _external=True)

    msg = MailMessage(
        subject="📧 Email Verification",
        recipients=[user_email],
        body=f"გთხოვთ დაადასტუროთ თქვენი ელფოსტა:\n\n{verification_link}\n\n"
    )
    mail.send(msg)


@app.route('/verify_email/<token>')
def verify_email(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)  # 1 საათი
    except:
        flash("Verification link is invalid or expired.", "danger")
        return redirect(url_for('contact'))

    email = data['email']

    # თუ ელფოსტა უკვე ვერიფიცირებულია, ვაბრუნებთ შეტყობინებას
    if VerifiedEmail.query.filter_by(email=email).first():
        flash('Email already verified!', 'success')
    else:
        # ვინახავთ ვერიფიცირებულ ელფოსტას ბაზაში
        new_verified_email = VerifiedEmail(email=email)
        db.session.add(new_verified_email)
        db.session.commit()
        flash('Email successfully verified!', 'success')

    return redirect(url_for('contact'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        email = form.email.data

        # 1️⃣ **შევამოწმოთ ელფოსტის ვერიფიკაცია**
        verified = VerifiedEmail.query.filter_by(email=email).first()
        if not verified:
            send_verification_email(email)
            flash('Verification email sent! Please verify before submitting the message.', 'info')
            return redirect(url_for('contact'))

        # 2️⃣ **თუ უკვე ვერიფიცირებულია, ვამატებთ მესიჯს ბაზაში**
        new_message = Message(name=form.name.data, email=email, message=form.message.data)
        db.session.add(new_message)
        db.session.commit()
        flash('Message successfully sent!', 'success')

        return redirect(url_for('contact'))

    return render_template('contact.html', form=form)


@app.route('/messages')
def view_messages():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', messages=messages)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
