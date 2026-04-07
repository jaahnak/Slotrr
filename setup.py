from setuptools import setup, find_packages

setup(
    name="slotrr",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "supabase",
        "bcrypt",
        "Pillow",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "slotrr=slotrr.main:run"
        ]
    },
    author="Your Name",
    description="Classroom Booking System"
)