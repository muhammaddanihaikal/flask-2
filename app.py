from flask import Flask, jsonify
from flask_restx import Resource, Api, reqparse
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import werkzeug
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import send_file
import json
app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///record.db"

db = SQLAlchemy()
db.init_app(app)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(100), nullable=False)
    file = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)

@api.route('/createdb')
class CreateDB(Resource):
    def get(self):
        with app.app_context():
            db.create_all()
            return "Database Created Successfully!"



@api.route('/record')
class RecordAll(Resource):
    @api.expect()
    def get(self):
        records = db.session.execute(db.select(Record).order_by(Record.id)).scalars()
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'method': record.method,
                'file': record.file,
                'time': record.time,
            })
        return json.dumps(data)

#form upload image
uploadParser = api.parser()
# uploadParser.add_argument('file', location='files', type=FileStorage, required=True)

@api.route('/image')
class ImageAPI(Resource):
    @api.expect(uploadParser)
    def post(self):
        args = uploadParser.parse_args()
        file = args['file']
        file.save("./gambar/gambar1.png")

        method = 'POST'
        date_now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        record = Record(
            method=method,
            file=file.filename,
            # file='gambar1.png',
            time=date_now
        )
        db.session.add(record)
        db.session.commit()

        #buat AI
        # return send_file(file.filename)
        return {'method': method,
                'file': 'gambar1.png',
                'time': date_now
                }
    def get(self):
        path = './gambar/gambar1.png'
        method = 'GET'
        date_now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        record = Record(
            method=method,
            file=path,
            time=date_now
        )
        db.session.add(record)
        db.session.commit()

        # return send_file(filename, mimetype='image/jpg')
        return {'method': method,
                'file': path,
                'time': date_now
                }

@api.route('/api/upload2')
class UploadImage(Resource):
    @api.expect(uploadParser)
    def post(self):
        args = uploadParser.parse_args()
        image_b64 = args['image']
        image_data = image_b64.split(',')[1]
        image_binary = image_data.encode()
        filename = 'image.jpg'

        with open(filename, 'wb') as f:
            f.write(image_binary)

        return {'message': 'Image uploaded successfully'}, 200
uploadParser.add_argument('image', type=FileStorage, location='files')
@api.route('/api/upload')
class Upload(Resource):
    @api.expect(uploadParser)
    def post(self):
        args = uploadParser.parse_args()
        image = args['image']

        if image:
            filename = secure_filename(image.filename)
            image.save(filename)
            return {'message': 'Image saved successfully'}
        else:
            return {'error': 'No image provided'}

@api.route('/upload')
class Upload2(Resource):
    @api.expect(uploadParser)
    def post(self):
        args = uploadParser.parse_args()
        imagefile = args['image']
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        imagefile.save("./gambar/gambar1.png")
        return jsonify({
            "message": "Image Uploaded Successfully"
        })

if __name__ == '__main__':
    app.run(debug=True)