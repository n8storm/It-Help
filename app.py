
import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///omni_desk.db'
app.config['SECRET_KEY'] = 'omni-ultra-secret-key-2027'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='Client') 
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.String(200), nullable=True) 
    hourly_rate = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=5.0)
    plan = db.Column(db.String(20), default='Free')
    is_paid = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='General')
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(20), default='Open') 
    budget = db.Column(db.Integer, default=20) 
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def get_sla_status(self):
        delta = datetime.now(timezone.utc) - self.created_at
        if delta.days >= 2: return 'Breached'
        return 'Within SLA'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@omni.it', password=generate_password_hash('admin123'), role='Admin', plan='Enterprise', is_paid=True)
        db.session.add(admin)
        db.session.commit()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'Client')
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or Email already exists!')
            return redirect(url_for('signup'))
        new_user = User(username=username, email=email, password=generate_password_hash(password), role=role, plan='Free', is_paid=False)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Welcome to Omni-Service.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    if current_user.role == 'Expert':
        return redirect(url_for('marketplace'))
    tickets = Ticket.query.filter_by(requester_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('employee_dashboard.html', tickets=tickets)

@app.route('/experts')
def experts():
    all_experts = User.query.filter_by(role='Expert').all()
    return render_template('experts.html', experts=all_experts)

@app.route('/marketplace')
@login_required
def marketplace():
    if current_user.role not in ['Expert', 'Admin']:
        abort(403)
    tickets = Ticket.query.filter_by(status='Open').order_by(Ticket.budget.desc(), Ticket.created_at.asc()).all()
    return render_template('marketplace.html', tickets=tickets)

@app.route('/ticket/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    if request.method == 'POST':
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        ticket = Ticket(
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            priority=request.form.get('priority'),
            budget=int(request.form.get('budget', 20)),
            requester_id=current_user.id,
            due_date=due_date
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Request posted to Marketplace!')
        return redirect(url_for('dashboard'))
    return render_template('new_ticket.html')

@app.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.requester_id != current_user.id and current_user.role not in ['Expert', 'Admin']:
        abort(403)
    if request.method == 'POST':
        comment_text = request.form.get('comment')
        if comment_text:
            new_comment = Comment(ticket_id=ticket.id, user_id=current_user.id, text=comment_text)
            db.session.add(new_comment)
        if current_user.role == 'Expert':
            if request.form.get('claim'):
                ticket.status = 'Claimed'
                ticket.owner_id = current_user.id
            if request.form.get('resolve'):
                ticket.status = 'Resolved'
            if request.form.get('pay'):
                ticket.status = 'Paid'
        db.session.commit()
        flash('Ticket updated!')
        return redirect(url_for('ticket_detail', ticket_id=ticket.id))
    comments = Comment.query.filter_by(ticket_id=ticket.id).order_by(Comment.created_at.asc()).all()
    return render_template('ticket_detail.html', ticket=ticket, comments=comments)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.bio = request.form.get('bio')
        current_user.skills = request.form.get('skills')
        current_user.hourly_rate = int(request.form.get('hourly_rate', 0))
        current_user.role = request.form.get('role', 'Client')
        db.session.commit()
        flash('Profile updated!')
        return redirect(url_for('dashboard'))
    return render_template('profile.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
