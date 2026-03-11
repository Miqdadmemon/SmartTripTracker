"""
Database Models for Smart Trip Tracker
"""
import hashlib
import secrets
from datetime import datetime
from flask_login import UserMixin
from extensions import db


def hash_password(password):
    """Simple password hashing using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password, password_hash):
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = password_hash.split('$')
        return pwd_hash == hashlib.sha256((password + salt).encode()).hexdigest()
    except:
        return False


class User(UserMixin, db.Model):
    """
    User model for authentication and authorization
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    deliveries = db.relationship('Delivery', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Verify the user's password"""
        return verify_password(password, self.password_hash)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Trip(db.Model):
    """
    Trip model for storing transportation trip information
    """
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    start_location = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    mode_of_transport = db.Column(db.String(50), nullable=False)
    distance = db.Column(db.Float, nullable=False)  # in km
    travel_cost = db.Column(db.Float, default=0)
    fuel_consumption = db.Column(db.Float, nullable=True)  # in liters
    carbon_footprint = db.Column(db.Float, nullable=True)  # in kg CO2
    status = db.Column(db.String(20), default='planned')  # planned, ongoing, completed
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Transport mode options
    TRANSPORT_MODES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('truck', 'Truck'),
        ('taxi', 'Taxi'),
        ('bike', 'Bicycle'),
        ('flight', 'Flight'),
        ('walk', 'Walking')
    ]
    
    STATUS_OPTIONS = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed')
    ]
    
    def calculate_carbon_footprint(self):
        """Calculate carbon footprint based on transport mode and distance"""
        carbon_factors = {
            'car': 0.21, 'bus': 0.089, 'train': 0.041,
            'truck': 0.89, 'taxi': 0.21, 'bike': 0,
            'flight': 0.255, 'walk': 0
        }
        factor = carbon_factors.get(self.mode_of_transport, 0.21)
        self.carbon_footprint = round(self.distance * factor, 2)
    
    def calculate_fuel_consumption(self):
        """Calculate estimated fuel consumption"""
        fuel_rates = {
            'car': 8.5, 'bus': 25.0, 'truck': 30.0, 'taxi': 10.0
        }
        rate = fuel_rates.get(self.mode_of_transport)
        if rate:
            self.fuel_consumption = round((self.distance / 100) * rate, 2)
    
    def __repr__(self):
        return f'<Trip {self.id}: {self.start_location} to {self.destination}>'


class Delivery(db.Model):
    """
    Delivery model for logistics package tracking
    """
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    sender_name = db.Column(db.String(100), nullable=False)
    receiver_name = db.Column(db.String(100), nullable=False)
    sender_address = db.Column(db.Text, nullable=False)
    receiver_address = db.Column(db.Text, nullable=False)
    package_description = db.Column(db.Text, nullable=True)
    weight = db.Column(db.Float, nullable=True)  # in kg
    status = db.Column(db.String(50), default='pending')
    current_location = db.Column(db.String(200), nullable=True)
    estimated_delivery = db.Column(db.DateTime, nullable=True)
    actual_delivery = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status options
    STATUS_OPTIONS = [
        ('pending', 'Pending'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    
    @staticmethod
    def generate_tracking_number():
        """Generate a unique tracking number"""
        import random
        import string
        prefix = 'STT'
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f'{prefix}-{random_str}'
    
    def __repr__(self):
        return f'<Delivery {self.tracking_number}>'


# User loader function - will be registered in app.py
def load_user(user_id):
    """Flask-Login user loader function"""
    return User.query.get(int(user_id))

