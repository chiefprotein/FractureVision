from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, send_file
from datetime import datetime
from report_org import generate_report
from natsort import natsorted
from flask_sqlalchemy import SQLAlchemy
import logging
import secrets
import os
import random
import SimpleITK as sitk
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads/CT_Scans'
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.String(5), unique=True, nullable=False)
    doctor_name = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    patients = db.relationship('Patient', backref='doctor', lazy=True)

    def __repr__(self):
        return f'<Doctor {self.username}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    ct_scan = db.Column(db.String(120), nullable=False)
    doctor_id = db.Column(db.String(5), db.ForeignKey('doctor.doctor_id'), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        doctor = Doctor.query.filter_by(username=username, password=password).first()
        if doctor:
            session['username'] = username
            session['doctor_id'] = doctor.doctor_id
            session['doctor_name'] = doctor.doctor_name
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['doctor_name']
            username = request.form['username']
            password = request.form['password']
            
            # Check if the username already exists
            existing_doctor = Doctor.query.filter_by(username=username).first()
            if existing_doctor:
                flash('Username already exists. Please choose a different username.')
                return redirect(url_for('register'))
            
            # Generate a unique doctor ID
            doctor_id = "D" + str(random.randint(1000, 9999))
            while Doctor.query.filter_by(doctor_id=doctor_id).first() is not None:
                doctor_id = "D" + str(random.randint(1000, 9999))
            
            doctor = Doctor(username=username, password=password, doctor_id=doctor_id, doctor_name = name)
            db.session.add(doctor)
            db.session.commit()
            flash('Doctor successfully registered! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('register'))
    else:
        return render_template('register.html')


@app.route('/home')
def home():
    username = session.get('username')
    name = session.get('doctor_name')
    doctor_id = session.get('doctor_id')
    if not username:
        return redirect(url_for('login'))
    patients = Patient.query.filter_by(doctor_id=doctor_id).all()
    return render_template('home.html', username=username, doctor_id=doctor_id, patients=patients, doctor_name = name)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('doctor_id', None)
    session.pop('doctor_name', None)
    return redirect(url_for('login'))

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        diagnosis = request.form['diagnosis']
        ct_scan = request.files['ct_scan']
        doctor_id = session.get('doctor_id')
        # Calculate age from dob
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if ct_scan:
            filename = ct_scan.filename
            patient = Patient(first_name=first_name, middle_name=middle_name, last_name=last_name, gender=gender, dob=dob, age=age, diagnosis=diagnosis, ct_scan=filename, doctor_id=doctor_id)
            db.session.add(patient)
            db.session.commit()

            patient_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"CT{patient.id}")
            os.makedirs(patient_folder, exist_ok=True)

            patient_slices_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"CT{patient.id}", "Slices")
            os.makedirs(patient_slices_folder, exist_ok=True)
            
            file_path = os.path.join(patient_folder, filename)
            ct_scan.save(file_path)

            flash('Patient added successfully!')

            ct_scan = sitk.ReadImage(file_path)
            ct_scan_array = sitk.GetArrayFromImage(ct_scan)
            for i in range(ct_scan_array.shape[0]):
                ct_slice = ct_scan_array[i, :, :]
                ct_output_filename = os.path.join(patient_slices_folder, f"ct_slice_{i}.png")
                plt.imsave(ct_output_filename, ct_slice, cmap='gray')

            return redirect(url_for('home'))
    return render_template('add_patient.html')

@app.route('/view_patients')
def view_patients():
    doctor_id = session.get('doctor_id')
    patients = Patient.query.filter_by(doctor_id=doctor_id).all()
    return render_template('view_patients.html', patients=patients)

@app.route('/display/<int:patient_id>')
def display(patient_id):
    patient_folder = os.path.join("uploads", "CT_Scans", f"CT{patient_id}", "Slices")
    if os.path.exists(patient_folder) and os.path.isdir(patient_folder):
        image_paths = natsorted(
            [os.path.join(patient_folder, file).replace("\\", "/")  # Replace backslashes
             for file in os.listdir(patient_folder)
             if file.lower().endswith(('.png', '.jpg', '.jpeg'))])
    return render_template('display.html', image_paths=image_paths)

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if patient:
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully!')
    else:
        flash('Patient not found.')
    return redirect(url_for('view_patients'))

@app.route('/users')
def users():
    all_users = Doctor.query.all()
    return render_template('users.html', users=all_users)

@app.route('/display/uploads/<path:filename>')
def display_image(filename):
    return send_from_directory("uploads", filename)

@app.route('/generate_report/<int:patient_id>', methods=['GET'])
def generate_report_route(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        flash('Patient not found.')
        return redirect(url_for('view_patients'))
    
    doctor = Doctor.query.filter_by(doctor_id=patient.doctor_id).first()
    if not doctor:
        flash('Doctor not found.')
        return redirect(url_for('view_patients'))

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], patient.ct_scan)
    heatmap_path = os.path.join(app.config['UPLOAD_FOLDER'], 'gradcam.jpg')  # Assuming the heatmap is generated and saved as 'gradcam.jpg'
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'report.pdf')
    generate_report(image_path, heatmap_path, output_path, patient, doctor)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)