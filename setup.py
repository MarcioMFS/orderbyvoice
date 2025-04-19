from setuptools import setup, find_packages

setup(
    name="orderbyvoice",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==2.3.3',
        'Flask-CORS==4.0.0',
        'python-dotenv==1.0.0',
        'gTTS==2.3.2',
        'openai==1.3.0',
        'pydub==0.25.1',
        'SpeechRecognition==3.10.0',
        'Werkzeug==2.3.7',
        'SQLAlchemy==2.0.20',
        'Flask-SQLAlchemy==3.0.5',
        'pytest==7.4.2',
        'black==23.9.1',
        'flake8==6.1.0',
        'python-magic==0.4.27'
    ],
) 