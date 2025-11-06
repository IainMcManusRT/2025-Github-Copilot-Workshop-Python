"""
Pomodoro Timer Storage Module - Step 4
Session-based storage for user progress data with error handling
"""

from flask import session
from datetime import date
import json
import os


class PomodoroStorage:
    """Handles storage operations for Pomodoro timer progress."""
    
    def __init__(self):
        """Initialize storage with session-based backend."""
        self.storage_type = "session"
        self.fallback_file = "pomodoro_fallback.json"
    
    def save_progress(self, pomodoros, focus_time):
        """
        Save progress data to Flask session.
        
        Args:
            pomodoros (int): Number of completed Pomodoros
            focus_time (int): Total focus time in minutes
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            today = str(date.today())
            
            # Try session storage first
            try:
                # Initialize session data if not exists
                if 'pomodoro_data' not in session:
                    session['pomodoro_data'] = {}
                
                # Save progress for today
                session['pomodoro_data'][today] = {
                    'pomodoros': pomodoros,
                    'focus_time': focus_time,
                    'last_updated': today
                }
                
                # Force session to be saved
                session.modified = True
                
                print(f"Progress saved to session: {pomodoros} pomodoros, {focus_time} minutes")
                return True
                
            except RuntimeError:
                # Fallback to file storage if no Flask context
                print("No Flask context available, using file fallback")
                return self._save_to_file(pomodoros, focus_time)
                
        except Exception as e:
            print(f"Error saving progress: {str(e)}")
            return False
    
    def load_progress(self):
        """
        Load progress data from Flask session.
        
        Returns:
            dict: Progress data with keys 'pomodoros' and 'focus_time'
                 Returns default values if no data exists
        """
        try:
            today = str(date.today())
            
            # Try session storage first
            try:
                # Check if session data exists
                if 'pomodoro_data' not in session:
                    return self._get_default_progress()
                
                # Get today's data
                today_data = session['pomodoro_data'].get(today, {})
                
                if not today_data:
                    return self._get_default_progress()
                
                progress = {
                    'pomodoros': today_data.get('pomodoros', 0),
                    'focus_time': today_data.get('focus_time', 0),
                    'date': today
                }
                
                print(f"Progress loaded from session: {progress}")
                return progress
                
            except RuntimeError:
                # Fallback to file storage if no Flask context
                print("No Flask context available, using file fallback")
                return self._load_from_file()
                
        except Exception as e:
            print(f"Error loading progress: {str(e)}")
            return self._get_default_progress()
    
    def clear_progress(self):
        """
        Clear progress data from Flask session.
        
        Returns:
            bool: True if clear was successful, False otherwise
        """
        try:
            today = str(date.today())
            
            # Try session storage first
            try:
                if 'pomodoro_data' in session:
                    # Clear today's data
                    if today in session['pomodoro_data']:
                        del session['pomodoro_data'][today]
                        session.modified = True
                        print(f"Progress cleared from session for {today}")
                
                return True
                
            except RuntimeError:
                # Fallback to file storage if no Flask context
                print("No Flask context available, clearing file fallback")
                return self._clear_file()
                
        except Exception as e:
            print(f"Error clearing progress: {str(e)}")
            return False
    
    def _save_to_file(self, pomodoros, focus_time):
        """Fallback file storage for development/testing."""
        try:
            today = str(date.today())
            data = {
                today: {
                    'pomodoros': pomodoros,
                    'focus_time': focus_time,
                    'last_updated': today
                }
            }
            
            with open(self.fallback_file, 'w') as f:
                json.dump(data, f)
            
            print(f"Progress saved to file: {pomodoros} pomodoros, {focus_time} minutes")
            return True
            
        except Exception as e:
            print(f"Error saving to file: {str(e)}")
            return False
    
    def _load_from_file(self):
        """Fallback file loading for development/testing."""
        try:
            today = str(date.today())
            
            if not os.path.exists(self.fallback_file):
                return self._get_default_progress()
            
            with open(self.fallback_file, 'r') as f:
                data = json.load(f)
            
            today_data = data.get(today, {})
            
            if not today_data:
                return self._get_default_progress()
            
            progress = {
                'pomodoros': today_data.get('pomodoros', 0),
                'focus_time': today_data.get('focus_time', 0),
                'date': today
            }
            
            print(f"Progress loaded from file: {progress}")
            return progress
            
        except Exception as e:
            print(f"Error loading from file: {str(e)}")
            return self._get_default_progress()
    
    def _clear_file(self):
        """Clear fallback file."""
        try:
            if os.path.exists(self.fallback_file):
                os.remove(self.fallback_file)
                print("Fallback file cleared")
            return True
        except Exception as e:
            print(f"Error clearing file: {str(e)}")
            return False
    
    def _get_default_progress(self):
        """
        Get default progress values.
        
        Returns:
            dict: Default progress data
        """
        return {
            'pomodoros': 0,
            'focus_time': 0,
            'date': str(date.today())
        }
    
    def get_all_progress(self):
        """
        Get all stored progress data (for debugging/admin purposes).
        
        Returns:
            dict: All progress data from session
        """
        try:
            try:
                return session.get('pomodoro_data', {})
            except RuntimeError:
                # Try file fallback
                if os.path.exists(self.fallback_file):
                    with open(self.fallback_file, 'r') as f:
                        return json.load(f)
                return {}
        except Exception as e:
            print(f"Error getting all progress: {str(e)}")
            return {}
    
    def increment_pomodoro(self):
        """
        Increment the pomodoro count by 1 and add 25 minutes to focus time.
        
        Returns:
            dict: Updated progress data
        """
        try:
            current_progress = self.load_progress()
            new_pomodoros = current_progress['pomodoros'] + 1
            new_focus_time = current_progress['focus_time'] + 25  # 25 minutes per Pomodoro
            
            self.save_progress(new_pomodoros, new_focus_time)
            
            return {
                'pomodoros': new_pomodoros,
                'focus_time': new_focus_time,
                'date': str(date.today())
            }
            
        except Exception as e:
            print(f"Error incrementing pomodoro: {str(e)}")
            return self._get_default_progress()


# Create a global instance for easy import
storage = PomodoroStorage()


# Utility functions for backward compatibility
def save_progress(pomodoros, focus_time):
    """Save progress using global storage instance."""
    return storage.save_progress(pomodoros, focus_time)


def load_progress():
    """Load progress using global storage instance."""
    return storage.load_progress()


def clear_progress():
    """Clear progress using global storage instance."""
    return storage.clear_progress()


# Test functions (for development/debugging)
def test_storage():
    """Test all storage functions."""
    print("Testing Pomodoro Storage...")
    
    # Test default values
    progress = load_progress()
    print(f"Default progress: {progress}")
    
    # Test saving
    save_result = save_progress(3, 75)
    print(f"Save result: {save_result}")
    
    # Test loading
    progress = load_progress()
    print(f"Loaded progress: {progress}")
    
    # Test increment
    new_progress = storage.increment_pomodoro()
    print(f"After increment: {new_progress}")
    
    # Test clearing
    clear_result = clear_progress()
    print(f"Clear result: {clear_result}")
    
    # Test after clear
    progress = load_progress()
    print(f"Progress after clear: {progress}")
    
    print("Storage tests completed!")


if __name__ == "__main__":
    # Run tests if module is executed directly
    test_storage()
