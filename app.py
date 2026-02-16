from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

# Define a route for the home page
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Run the application (for development only)
if __name__ == "__main__":
    app.run(debug=True)

