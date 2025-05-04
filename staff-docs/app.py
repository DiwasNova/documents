
from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime, timedelta

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

documents = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        staff_name = request.form['staff_name']
        doc_type = request.form['doc_type']
        expiry_date = request.form['expiry_date']
        file = request.files['file']
        
        folder = os.path.join(app.config['UPLOAD_FOLDER'], doc_type)
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, file.filename)
        file.save(file_path)

        documents.append({
            'staff_name': staff_name,
            'doc_type': doc_type,
            'file_path': file_path,
            'expiry_date': expiry_date
        })
        return redirect(url_for('index'))

    today = datetime.today()
    expiring = [doc for doc in documents if datetime.strptime(doc['expiry_date'], '%Y-%m-%d') - today < timedelta(days=60)]

    return render_template('index.html', documents=documents, expiring=expiring)

if __name__ == '__main__':
    app.run(debug=True)
