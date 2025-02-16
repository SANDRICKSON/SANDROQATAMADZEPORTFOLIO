from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message as MailMessage
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import timedelta  # დამატება

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Sandricksoni729'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Flask-Mail კონფიგურაცია
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Gmail-ის სერვერი
app.config['MAIL_PORT'] = 587 
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sandricksoni@gmail.com'  # შენი ელ.ფოსტა
app.config['MAIL_PASSWORD'] = 'isiv iqey coyf vstd'  # შენი პაროლი (ან აპლიკაციის პაროლი)
app.config['MAIL_DEFAULT_SENDER'] = 'sandricksoni@gmail.com'

mail = Mail(app)  # Flask-Mail ობიექტი



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

# 🔹 ვერმინაციის ფუნქცია
def send_verification_email(user_email):
    s = Serializer(app.config['SECRET_KEY'])  # Remove expires_in
    token = s.dumps({'email': user_email})  # აღარ საჭიროა .decode('utf-8')

    
    # ვადა (1 საათი)
    verification_link = url_for('verify_email', token=token, _external=True)

    msg = MailMessage(
        subject="📧 Email Verification",
        recipients=[user_email],
        body=f"სალამი მეგობარო!\n\nდიდი მადლობა რომ დაინტერესდი ჩემი პორტფოლიოთი და ნაშრომებით. ნებისმიერი კითხვა შეგიძლია მოიწერო, თუმცა მანამდე გაიარე ვერიფიკაცია.\n\n{verification_link}\n\nპატივისცემით,\nსანდრო ქათამაძე - ახალგაზრდა დეველოპერი"
    )
    mail.send(msg)  

@app.route('/verify_email/<token>')
def verify_email(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)  # ვადა 1 საათი
    except:
        return "The verification link is invalid or has expired."
    
    email = data['email']
    flash(f'Email {email} successfully verified!', 'success')
    
    # აქ შეიძლება მოახდინო მომხმარებლის აქტივაციის პროცესი
    return redirect(url_for('contact'))

@app.route('/contact', methods=['GET', 'POST']) 
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # ელ.ფოსტის ვერიფიკაციის გაგზავნა
        send_verification_email(form.email.data)
        
        flash('Verification email sent! Please verify your email before submitting the message.', 'info')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html',)

# 🔹 მიღებული შეტყობინებების ნახვა
@app.route('/messages')
def view_messages():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', messages=messages)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
