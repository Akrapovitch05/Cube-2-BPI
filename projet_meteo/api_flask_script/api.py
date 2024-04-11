from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Float, create_engine
import paho.mqtt.client as mqtt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration of the database
DB_USERNAME = 'root'
DB_PASSWORD = 'root'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'
DB_NAME = 'temperature_db'

# Configuration of the SQLAlchemy connection
DB_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definition of the table model to store temperature data
class TemperatureData(db.Model):
    __tablename__ = 'temperature_data'
    id = Column(Integer, primary_key=True)
    temperature = Column(Float)
    humidity = Column(Float)

# Function to create tables in the database
def create_tables():
    engine = create_engine(DB_URL)
    TemperatureData.__table__.create(bind=engine, checkfirst=True)

# Define namespaces
api = Api(app, version='1.0', title='Raspberry Pi Zero API',
          description='API for interacting with the Raspberry Pi Zero')
ns = api.namespace('raspberrypi', description='Endpoints for the Raspberry Pi Zero')

# Configure the MQTT client
mqtt_client = mqtt.Client()

body_model = api.model('BodyModel', {
    'temperature': fields.Float(required=True, description='temperature'),
    'humidity': fields.Float(required=True, description='humidity')
})

@ns.route('/temperature')
class Temperature(Resource):
    def get(self):
        """
        Retrieve temperature and humidity data from the database.
        """
        # Replace this with your logic to retrieve temperature and humidity data from the database
        # Example:
        temperature_data = TemperatureData.query.order_by(TemperatureData.id.desc()).first()
        if temperature_data:
            temperature = temperature_data.temperature
            humidity = temperature_data.humidity
            return jsonify({'temperature': temperature, 'humidity': humidity})
        else:
            return jsonify({'error': 'No data available'}), 404
        
    @api.expect(body_model)
    def post(self):
        """
        Receive temperature and humidity data from the ESP and store it in the database.
        """
        data = request.json
        temperature = data.get('temperature')
        humidity = data.get('humidity')

        # Store temperature and humidity data in the database
        temperature_data = TemperatureData(temperature=temperature, humidity=humidity)
        db.session.add(temperature_data)
        db.session.commit()

        return {'message': 'Temperature and humidity data received and saved successfully'}, 201

if __name__ == '__main__':
    # Create tables in the database
    create_tables()

    # Start the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)