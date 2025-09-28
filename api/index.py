import sys
import os

# Add the parent directory to the Python path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# This is the entry point for Vercel
# Vercel will automatically call this as a serverless function
