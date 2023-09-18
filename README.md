# Python React Travel Agency with Rapyd API Integration

### Overview
Build a robust travel agency web application that empowers users to register, log in, explore listed trips, and book their desired journeys with ease. Seamlessly integrate Rapyd's payment processing capabilities into your Python and React application to offer secure and efficient payment solutions for travelers.

### Prerequisites
Before diving into this project, ensure that you have the following prerequisites in place:

- Python (Flask)
- React
- Ngrok
  
### Getting Started
To kickstart your journey with this travel agency application, you'll need a [Rapyd account](https://dashboard.rapyd.net/). If you don't have one yet, you can easily sign up at the Rapyd Dashboard.

### Exposing Port for Rapyd Integration
Integrating Rapyd into your application requires external access to your development server. Since Rapyd doesn't accept requests from localhost, you'll need to expose your server to the outside world. For secure testing and interaction with Rapyd APIs, you can utilize a tool like ngrok. Ngrok generates a temporary web address and redirects traffic to your local machine, allowing you to fully experience Rapyd's features within your development environment.

### Running the Application
Clone this repository to your local machine.

```bash
git clone https://github.com/gitnyasha/Building-a-Travel-Agency-Website-with-the-Rapyd-Payment-Gateway-Python-Flask-and-React.git
```

Navigate to the project directory.

```bash
cd python-react-rapyd
```

### Configure Ngrok
Install ngrok by following the instructions provided on ngrok's website.

After installation, expose port 5000 (the default Flask port) using the following command:

```bash
ngrok http 5000
```

Copy the ngrok URL generated, e.g., http://abcdef123456.ngrok.io.

### Configure Your Application

1. In your Python Flask application, open python-backend/app.py.

2. Find the line that defines the Flask app's CORS settings and add your ngrok URL as an allowed origin:

```python
CORS(app, resources={r"/api/*": {"origins": "http://abcdef123456.ngrok.io"}})
```
1. Save the file.
   
### Launch the Flask Server

1. Set up a virtual environment for your Flask app (if not done already).

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

Install Flask and other necessary dependencies.

```bash
pip install Flask
pip install flask-cors
```

Start the Flask server.

```bash
python python-backend/app.py
```

Access the Python backend API by visiting http://localhost:5000 or your ngrok-generated URL.

### Launch the React Frontend
Navigate to the react-frontend directory.

```bash
cd react-frontend
```

Install the required Node.js packages.

```bash
npm install
```

Start the React development server.

```bash
npm start
```

Access the React frontend by visiting http://localhost:3000.

### Rapyd API Keys

1. Log in to your Rapyd account.
2. Ensure that you are in "sandbox" mode (you can switch modes at the bottom left of the Rapyd panel).
3. Navigate to the "Developers" tab and locate your API keys. Copy these keys for use in your Python Flask backend.

### Explore the Integration

With the entire setup in place, you can now explore and test the travel agency application's features, including user registration, login, trip browsing, and booking—all while enjoying the secure payment processing capabilities offered by Rapyd.

### Get Support
For additional support, questions, or community engagement, feel free to visit the Rapyd Community.

Happy coding, and may your travel agency app flourish with seamless payments!
