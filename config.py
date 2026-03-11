"""
Configuration for Smart Trip Tracker Application
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-trip-tracker-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///smarttrip.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Security - use pbkdf2 for compatibility
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    
    # Application settings
    ITEMS_PER_PAGE = 10
    MAX_TRIPS_DISPLAY = 100
    
    # Carbon footprint factors (kg CO2 per km)
    CARBON_FACTORS = {
        'car': 0.21,
        'bus': 0.089,
        'train': 0.041,
        'truck': 0.89,
        'taxi': 0.21,
        'bike': 0,
        'flight': 0.255
    }
    
    # Fuel consumption factors (liters per 100km)
    FUEL_CONSUMPTION = {
        'car': 8.5,
        'bus': 25.0,
        'truck': 30.0,
        'taxi': 10.0
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

