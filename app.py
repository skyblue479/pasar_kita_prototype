from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "sic2026_super_secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pasarkita.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS (OOP Concept) ---
class Fabric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    available_kg = db.Column(db.Float, nullable=False)

class RequestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    makcik_name = db.Column(db.String(100), nullable=False)
    fabric_id = db.Column(db.Integer, db.ForeignKey('fabric.id'), nullable=False)
    requested_kg = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    
    fabric = db.relationship('Fabric', backref=db.backref('requests', lazy=True))

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

# 1. Admin Dashboard (Pasar Kita)
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        # Admin tambah stok fabrik baru
        name = request.form.get('name')
        kg = float(request.form.get('available_kg'))
        new_fabric = Fabric(name=name, available_kg=kg)
        db.session.add(new_fabric)
        db.session.commit()
        flash('Stok fabrik berjaya ditambah!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    fabrics = Fabric.query.all()
    requests = RequestLog.query.all()
    return render_template('admin.html', fabrics=fabrics, requests=requests)

# 2. B40 Dashboard (Makcik Interface)
@app.route('/b40', methods=['GET', 'POST'])
def b40_dashboard():
    if request.method == 'POST':
        # Makcik request fabrik
        makcik_name = request.form.get('makcik_name')
        fabric_id = request.form.get('fabric_id')
        req_kg = float(request.form.get('requested_kg'))
        
        # Semak stok
        fabric = Fabric.query.get(fabric_id)
        if fabric and fabric.available_kg >= req_kg:
            # Tolak stok terus dari gudang (Smart Matching)
            fabric.available_kg -= req_kg
            new_req = RequestLog(makcik_name=makcik_name, fabric_id=fabric.id, requested_kg=req_kg)
            db.session.add(new_req)
            db.session.commit()
            flash(f'Request {req_kg}kg {fabric.name} berjaya! Lori akan hantar.', 'success')
        else:
            flash('Stok tak cukup atau error.', 'danger')
        return redirect(url_for('b40_dashboard'))
    
    # Hanya tunjuk fabrik yang ada stok (> 0kg)
    available_fabrics = Fabric.query.filter(Fabric.available_kg > 0).all()
    return render_template('b40.html', fabrics=available_fabrics)

# --- INITIALIZE DATABASE DENGAN DATA DEMO ---
with app.app_context():
    db.create_all()
    # Letak dummy data kalau kosong
    if not Fabric.query.first():
        db.session.add(Fabric(name="Kain Perca Cotton (Putih)", available_kg=150.0))
        db.session.add(Fabric(name="Denim Terpakai", available_kg=45.0))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
