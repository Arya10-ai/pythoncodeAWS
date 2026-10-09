```python
import os
from flask import Flask, render_template, request
import boto3
import pymysql

app = Flask(__name__)

bucket_name = os.environ.get("S3_BUCKET_NAME")

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME", "studentdb")
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    course = request.form['course']
    photo = request.files['photo']

    s3 = boto3.client('s3')
    s3.upload_fileobj(photo, bucket_name, photo.filename)

    photo_url = f"s3://{bucket_name}/{photo.filename}"

    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql = """
                INSERT INTO students
                (name, email, course, photo_url)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                sql, (name, email, course, photo_url)
            )
        db.commit()
    finally:
        db.close()

    return "Student Registered Successfully"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```
