# Setup Python env
python3 -m venv venv
source venv/bin/activate
pip3 install rshell

# Run rshell
sudo chmod 777 /dev/ttyACM0
rshell -p /dev/ttyACM0 --buffer-size=2048
