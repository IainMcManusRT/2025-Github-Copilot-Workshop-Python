import os

class Config:
    """Basic configuration for the Pomodoro Timer application."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pomodoro-timer-secret-key-2025'
    
    # Timer configuration
    DEFAULT_POMODORO_DURATION = 25  # minutes
    DEFAULT_SHORT_BREAK = 5         # minutes
    DEFAULT_LONG_BREAK = 15         # minutes
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))

# Use this configuration by default
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-change-me'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
