from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'traffic_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///violations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Violation(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    violation_type = db.Column(db.String(100), nullable=False)
    location       = db.Column(db.String(200), nullable=False)
    date           = db.Column(db.Date, nullable=False)
    fine_amount    = db.Column(db.Float, nullable=False)
    status         = db.Column(db.String(10), default='Unpaid')
    qr_code_path   = db.Column(db.String(200))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    total      = Violation.query.count()
    unpaid     = Violation.query.filter_by(status='Unpaid').count()
    paid       = Violation.query.filter_by(status='Paid').count()
    recent     = Violation.query.order_by(Violation.created_at.desc()).limit(5).all()
    total_fine = db.session.query(db.func.sum(Violation.fine_amount)).scalar() or 0
    return render_template('index.html', total=total, unpaid=unpaid, paid=paid,
                           recent=recent, total_fine=total_fine)

@app.route('/add', methods=['GET', 'POST'])
def add_violation():
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number'].upper().strip()
        violation_type = request.form['violation_type']
        location       = request.form['location']
        fine_amount    = float(request.form['fine_amount'])
        date           = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

        v = Violation(vehicle_number=vehicle_number, violation_type=violation_type,
                      location=location, date=date, fine_amount=fine_amount)
        db.session.add(v)
        db.session.flush()

        qr_url      = url_for('status', violation_id=v.id, _external=True)
        qr_filename = f'qr_{v.id}.png'
        qr_path     = os.path.join(app.root_path, 'static', 'qrcodes', qr_filename)
        qrcode.make(qr_url).save(qr_path)
        v.qr_code_path = f'qrcodes/{qr_filename}'

        db.session.commit()
        flash('Violation logged successfully!', 'success')
        return redirect(url_for('challan', violation_id=v.id))

    violation_types = ['Overspeeding','No Helmet','No Seatbelt','Red Light Jump',
                       'Wrong Side Driving','Drunk Driving','No License',
                       'Expired Insurance','Mobile Phone Use','Illegal Parking']
    return render_template('add_violation.html', violation_types=violation_types,
                           today=datetime.today().strftime('%Y-%m-%d'))

@app.route('/history')
def history():
    query          = Violation.query
    vehicle_search = request.args.get('vehicle', '').upper().strip()
    status_filter  = request.args.get('status', '')
    type_filter    = request.args.get('type', '')
    date_from      = request.args.get('date_from', '')
    date_to        = request.args.get('date_to', '')

    if vehicle_search:
        query = query.filter(Violation.vehicle_number.contains(vehicle_search))
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(violation_type=type_filter)
    if date_from:
        query = query.filter(Violation.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Violation.date <= datetime.strptime(date_to, '%Y-%m-%d').date())

    violations      = query.order_by(Violation.created_at.desc()).all()
    violation_types = [v[0] for v in db.session.query(Violation.violation_type).distinct().all()]
    return render_template('history.html', violations=violations,
                           violation_types=violation_types,
                           vehicle_search=vehicle_search,
                           status_filter=status_filter, type_filter=type_filter)

@app.route('/challan/<int:violation_id>')
def challan(violation_id):
    v = Violation.query.get_or_404(violation_id)
    return render_template('challan.html', v=v)

@app.route('/status/<int:violation_id>')
def status(violation_id):
    v = Violation.query.get_or_404(violation_id)
    return render_template('status.html', v=v)

@app.route('/pay/<int:violation_id>', methods=['POST'])
def pay(violation_id):
    v = Violation.query.get_or_404(violation_id)
    v.status = 'Paid'
    db.session.commit()
    flash(f'Payment recorded for {v.vehicle_number}!', 'success')
    return redirect(url_for('challan', violation_id=v.id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
