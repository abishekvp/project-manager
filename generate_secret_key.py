"""
Secret key generator for Django deployment.
Run this once to generate a secure SECRET_KEY.
"""

from django.core.management.utils import get_random_secret_key

print("Generated SECRET_KEY:")
print(get_random_secret_key())
print("\nCopy and paste this into your Render environment variables as SECRET_KEY")
