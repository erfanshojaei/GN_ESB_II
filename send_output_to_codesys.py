import sys
from opcua import Client
import logging

# Set up logging to capture errors and info messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to send the terminal output to CODESYS
def send_output_to_codesys(output_message):
    try:
        # Connect to the OPC UA server
        server_url = "opc.tcp://DESKTOP-761BEPG:4840"  # Ensure this URL is correct
        client = Client(server_url)

        # Connect to the server
        client.connect()

        # Debugging: Print server information
        print(f"Connected to OPC UA server at {server_url}")

        # Access the desired node in CODESYS
        node = client.get_node('ns=4;s=|var|CODESYS Control Win V3 x64.Application.PythonIntegration.python_terminal_output')

        # Set the node value (this is the output message you want to send to CODESYS)
        node.set_value(output_message)
        logging.info(f"Sent output to CODESYS: {output_message}")
        print(f"Sent output to CODESYS: {output_message}")

    except Exception as e:
        # Handle any exceptions that occur during the process
        logging.error(f"Failed to send output to CODESYS: {e}")
        print(f"Failed to send output to CODESYS: {e}")

    finally:
        # Disconnect from the OPC UA server
        client.disconnect()
        print("Disconnected from OPC UA server.")

# Redirecting stdout to send output to CODESYS
class OutputRedirector:
    def write(self, message):
        # Send the message to CODESYS
        send_output_to_codesys(message)

    def flush(self):
        # Required to prevent issues with buffering
        pass

# Set up redirection for stdout (so print messages go to CODESYS)
sys.stdout = OutputRedirector()

# Example usage: Now all print statements will be sent to CODESYS
print("This message will be sent to CODESYS.")
print("Another message for CODESYS.")
