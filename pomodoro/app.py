from flask import Flask, render_template, session
from config import DevelopmentConfig
from storage import storage, test_storage

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    @app.route('/')
    def index():
        """Main route to serve the Pomodoro timer application."""
        return render_template('index.html')
    
    @app.route('/test-storage')
    def test_storage_route():
        """Test route to verify storage functionality."""
        # Test storage functions
        try:
            # Load current progress
            progress = storage.load_progress()
            
            # Save some test data
            storage.save_progress(2, 50)
            
            # Load again to verify
            updated_progress = storage.load_progress()
            
            # Increment once
            incremented = storage.increment_pomodoro()
            
            result = {
                'initial_progress': progress,
                'after_save': updated_progress, 
                'after_increment': incremented,
                'status': 'Storage working correctly!'
            }
            
            return result
            
        except Exception as e:
            return {'error': str(e), 'status': 'Storage test failed'}
    
    @app.route('/clear-storage')
    def clear_storage_route():
        """Route to clear all progress data."""
        try:
            storage.clear_progress()
            return {'status': 'Storage cleared successfully'}
        except Exception as e:
            return {'error': str(e), 'status': 'Failed to clear storage'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
