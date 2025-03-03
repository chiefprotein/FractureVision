from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PIL import Image
import os
from reportlab.lib.colors import HexColor
from datetime import datetime

def generate_report(input_image_path, heatmap_image_path, output_path, patient, doctor):
    c = canvas.Canvas(output_path)

    top_section_height = 200

    # Full page color
    bg = HexColor("#ffffff")
    c.setFillColor(bg)
    c.rect(0, 0, 600, 900, stroke=0, fill=1)

    bg_color = HexColor("#5e7dac")

    # Set the background color for the top section
    c.setFillColor(bg_color)
    c.roundRect(10, 5, 575, 15, 5, stroke=0, fill=1)
    c.roundRect(-30, 950 - top_section_height, 5000000, 595, top_section_height, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 36)  # Bold Helvetica with size 36
    c.setFillColor(colors.white)  # Set a color (e.g., dark red)
    c.drawString(220, 785, "REPORT")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(430, 802, "FractureVision")
    c.drawString(440, 785, "Hospital")

    c.drawImage("H.jpg", 520, 769, height=50, width=50)

    c.setFillColor(colors.white)  # Set the custom color
    c.setFont("Helvetica-Bold", 12)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(175, 8, f"Report generated on: {current_time}")

    # Patient details box
    c.setFillColor(bg_color)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(50, 700, "Patient Details:")
    c.setFillColor(colors.black)
    c.rect(50, 420, 500, 230, stroke=1, fill=0)

    c.setFont("Helvetica", 20)
    patient_details = [
        ("First Name:", patient.first_name),
        ("Middle Name:", patient.middle_name),
        ("Last Name:", patient.last_name),
        ("Gender:", patient.gender),
        ("Date of Birth:", patient.dob.strftime('%Y-%m-%d')),
        ("Age:", patient.age),
        ("Diagnosis:", patient.diagnosis)
    ]

    y_position = 620
    for label, value in patient_details:
        c.drawString(60, y_position, label)
        c.drawString(200, y_position, str(value))
        y_position -= 30

    # Doctor details box
    c.setFillColor(bg_color)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(50, 300, "Doctor Details:")
    c.setFillColor(colors.black)
    c.rect(50, 160, 500, 85, stroke=1, fill=0)

    c.setFont("Helvetica", 20)
    doctor_details = [
        ("Doctor ID:", doctor.doctor_id),
        ("Doctor Name:", doctor.doctor_name)
    ]

    y_position = 210
    for label, value in doctor_details:
        c.drawString(60, y_position, label)
        c.drawString(200, y_position, str(value))
        y_position -= 30

    c.showPage()
    c.setFillColor(bg)
    c.rect(0, 0, 600, 900, stroke=0, fill=1)

    c.setFillColor(bg_color)
    c.roundRect(10, 5, 575, 15, 5, stroke=0, fill=1)
    c.roundRect(-30, 950 - top_section_height, 5000000, 595, top_section_height, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(colors.white)
    c.drawString(220, 785, "REPORT")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(430, 802, "FractureVision")
    c.drawString(440, 785, "Hospital")

    c.drawImage("H.jpg", 520, 769, height=50, width=50)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(175, 8, f"Report generated on: {current_time}")

    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(bg_color)
    c.roundRect(50, 705, 200, 20, 5, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.drawString(99, 710, "INPUT IMAGE")

    c.drawImage(input_image_path, 50, 500, height=200, width=200)

    c.setFillColor(bg_color)
    c.roundRect(350, 705, 200, 20, 5, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.drawString(364, 710, "GENERATED HEATMAP")
    c.drawImage(heatmap_image_path, 350, 500, height=200, width=200)

    c.setFillColor(bg_color)
    c.roundRect(50, 445, 200, 37, 5, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(150, 453, "RESULTS")

    c.setFillColor(bg_color)
    c.roundRect(50, 200, 340, 37, 5, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(220, 207, "HEATMAP SCALE")
    
    # Ensure the path to heatmap_scale.png is correct
    heatmap_scale_path = os.path.join(os.path.dirname(__file__), 'heatmap_scale.png')
    c.drawImage(heatmap_scale_path, 100, 100, height=40, width=400)

    c.save()