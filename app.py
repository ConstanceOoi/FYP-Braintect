import io
import os
from main import app
from flask import Flask, flash, make_response, request, redirect, send_file, url_for, render_template
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from PIL import Image as PILImage
import numpy as np
import tensorflow as tf

# Establish connection with database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/braintect'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialise the allowed extension for the scans upload
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Path to the model
MODEL_PATH = 'model/effnet15ES.h5'

# Database table 
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(120), nullable=False)

# Func - check if file is png, jpeg, or jpg
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Func - predict the scan n return the result
def predict_image_class(image_array, model):
    labels = ["Glioma Tumor", "Meningioma Tumor", "No Tumor", "Pituitary Tumor"]
    # Add a batch dimension
    prediction = model.predict(np.expand_dims(image_array, axis=0))
    predicted_class = np.argmax(prediction)
    predicted_class = labels[predicted_class]
    return predicted_class

# load the model
loaded_model = tf.keras.models.load_model(MODEL_PATH)

@app.route('/')
def upload_form():
	return render_template('index.html')

# route to handle home page
@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		mimetype = file.mimetype
		temp_folder = "tmp/"
		file_path = os.path.join(temp_folder, filename)
		file.save(file_path)
		with open(file_path, 'rb') as f:
			img = Image(filename=filename, data=f.read(), mimetype=mimetype)
		db.session.add(img)
		db.session.commit()
		# open n resize the uploaded img
		image = PILImage.open(io.BytesIO(img.data))
		image = image.resize((150, 150))
		# convert img to RGB mode if it's not
		if image.mode != 'RGB':
			image = image.convert('RGB')
		# convert to np array 
		image_array = np.array(image)
		# send for analysis n prediction
		result = predict_image_class(image_array, loaded_model)
		# get the url to display scan
		image_url = url_for('display_image', filename=filename)
		flash('Image successfully uploaded and saved to database')
		# render the result template with the image, results
		return render_template('result.html', filename=filename, result=result, image_url=image_url)
	else:
		flash('Allowed image types are -> png, jpg, jpeg')
		return redirect(request.url)	

# Display the scan
@app.route('/display/<filename>')
def display_image(filename):
	# retrieve img from the db using filename
    image = Image.query.filter_by(filename=filename).first_or_404()
	# create a response with image n appropriate headers
    response = make_response(image.data)
    response.headers['Content-Type'] = image.mimetype
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

# Entry point for Flask app
if __name__ == "__main__":
	# create db table
	with app.app_context():
		db.create_all()
	app.run(debug=True)