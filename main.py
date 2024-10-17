"""
This is the main file that runs the application.
"""

from app import App

if __name__ == "__main__":
    app = App("database.db")
    app.load_model(True)
    app.serve()
