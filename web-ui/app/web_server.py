import requests
from flask import Flask, request, render_template
import os
import yaml
import threading


class WebServer:

    def __init__(self, config_file:str):

        # Server Thread
        self.server_thread = None

        # Save the configuration file
        self.config_file = config_file

        # Get the main communication directory
        main_app_path = ""

        # Construct the file path
        template_dir = os.path.join(main_app_path, 'templates')

        # Set a default configuration
        self.configuration_dict = {
            "web": {
                "host": "0.0.0.0",
                "port": 7071,
                "api_base_url": "http://127.0.0.1:7070/api/v1/iot/inventory"
            }
        }

        # Read Configuration from target Configuration File Path
        self.read_configuration_file()

        # Create the Flask app
        self.app = Flask(__name__, template_folder=template_dir)

        # Add URL rules to the Flask app mapping the URL to the function
        self.app.add_url_rule('/device/<string:device_id>/telemetry', 'telemetry', self.telemetry)

    def read_configuration_file(self):
        """ Read Configuration File for the Web Server
         :return:
        """

        # Get the main communication directory
        main_app_path = ""

        # Construct the file path
        file_path = os.path.join(main_app_path, self.config_file)

        with open(file_path, 'r') as file:
            self.configuration_dict = yaml.safe_load(file)

        print("Read Configuration from file ({}): {}".format(self.config_file, self.configuration_dict))

    def telemetry(self, device_id):
        """ Get telemetry data for a specific device and render the telemetry.html template"""
        telemetry_data = self.http_get_device_telemetry(device_id)
        print(telemetry_data)
        return render_template('telemetry.html', telemetry_data=telemetry_data, device_id=device_id)

    def http_get_device_telemetry(self, device_id):
        """ Get all locations from the remote server over HTTP"""

        # Get the base URL from the configuration
        base_http_url = self.configuration_dict['web']['api_base_url']
        target_url = f'{base_http_url}/device/{device_id}/telemetry'

        # Send the GET request
        response_string = requests.get(target_url)

        # Return the JSON response
        return response_string.json()

    def devices(self, location_id):
        """ Get all devices for a specific location and render the devices.html template"""
        device_list = self.http_get_device_list(location_id)
        return render_template('devices.html', devices=device_list, location_id=location_id)

    def http_get_device_list(self, location_id):
        """ Get all devices for the target location_id from the remote server over HTTP"""

        # Get the base URL from the configuration
        base_http_url = self.configuration_dict['web']['api_base_url']
        target_url = f'{base_http_url}/location/{location_id}/device'

        # Send the GET request
        response_string = requests.get(target_url)

        # Return the JSON response
        return response_string.json()


    def run_server(self):
        """ Run the Flask Web Server"""
        self.app.run(host=self.configuration_dict['web']['host'], port=self.configuration_dict['web']['port'])

    def start(self):
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()

    def stop(self):
        """ Stop the REST API Server (Flask Method)
        In this code, request.environ.get('werkzeug.server.shutdown')
        retrieves the shutdown function from the environment.
        If the function is not found, it raises a RuntimeError,
        indicating that the server is not running with Werkzeug.
        If the function is found, it is called to shut down the server."""

        # Shutdown the server
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')

        # Call the shutdown function
        func()

        # Wait for the server thread to join
        self.server_thread.join()