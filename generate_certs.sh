#!/bin/bash

# Configuration
DAYS=365
KEY_SIZE=4096
CERT_NAME="server.crt"
KEY_NAME="server.key"
COMBINED_NAME="server.pem"

echo "--- WDP Certificate Generator ---"

# Check if openssl is installed
if ! command -v openssl &> /dev/null
then
    echo "Error: openssl not found. Please install it with 'sudo apt install openssl'."
    exit 1
fi

# Generate the key and certificate
openssl req -x509 -newkey rsa:$KEY_SIZE -keyout $KEY_NAME -out $CERT_NAME -days $DAYS -nodes -subj "/C=BR/ST=SP/L=SaoPaulo/O=WDP/OU=Secure/CN=localhost"

# Create the combined PEM file for Python's SSLContext
cat $CERT_NAME $KEY_NAME > $COMBINED_NAME

# Set permissions
chmod 600 $KEY_NAME $COMBINED_NAME

echo "---------------------------------"
echo "Success! Certificates generated:"
echo "- $CERT_NAME (Public certificate)"
echo "- $KEY_NAME (Private key)"
echo "- $COMBINED_NAME (Combined for Server)"
echo "---------------------------------"
