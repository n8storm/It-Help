
import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///it_desk.db'
app.config['SECRET_KEY'] = 'it-professional-secret-key'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='Employee')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='General')
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(20), default='Open')
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
        admin = User(username='admin', password=generate_password_hash('admin123'), role='IT')
        user = User(username='employee', password=generate_password_hash('user123'), role='Employee')
        db.session.add_all([admin, user])
        db.session.commit()

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
    if current_user.role == 'IT':
        return redirect(url_for('admin_queue'))
    tickets = Ticket.query.filter_by(requester_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('employee_dashboard.html', tickets=tickets)

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
            requester_id=current_user.id,
            due_date=due_date
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket submitted successfully!')
        return redirect(url_for('dashboard'))
    return render_template('new_ticket.html')

@app.route('/admin/queue')
@login_required
def admin_queue():
    if current_user.role != 'IT': abort(403)
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    query = Ticket.query
    if status_filter: query = query.filter_by(status=status_filter)
    if priority_filter: query = query.filter_by(priority=priority_filter)
    tickets = query.order_by(Ticket.priority.desc(), Ticket.created_at.asc()).all()
    return render_template('admin_queue.html', tickets=tickets)

@app.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.requester_id != current_user.id and current_user.role != 'IT':
        abort(403)
    if request.method == 'POST':
        comment_text = request.form.get('comment')
        if comment_text:
            new_comment = Comment(ticket_id=ticket.id, user_id=current_user.id, text=comment_text)
            db.session.add(new_comment)
        if current_user.role == 'IT':
            ticket.status = request.form.get('status')
            ticket.priority = request.form.get('priority')
            ticket.owner_id = current_user.id if request.form.get('claim') else ticket.owner_id
        db.session.commit()
        flash('Ticket updated!')
        return redirect(url_for('ticket_detail', ticket_id=ticket.id))
    comments = Comment.query.filter_by(ticket_id=ticket.id).order_by(Comment.created_at.asc()).all()
    return render_template('ticket_detail.html', ticket=ticket, comments=comments)

if __name__ == '__main__':
    if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
