from app import create_app

app = create_app()

# This allows for direct execution of this file
if __name__ == "__main__":
    # Run the app when this file is executed directly
    app.run(host='0.0.0.0', port=10000)
