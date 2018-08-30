MIRO is designed to run using systemd services. We recommend Ubuntu 18.04.


How to Install:

Make sure postgres and nginx are installed:
```
sudo apt-get install postgresql
sudo apt-get install nginx
```

MIRO Browser requires python3 and pip for that version of python. Install the required packages:
```
pip install -r requirements
```

To then install and run MIRO:

```
./install_validator.sh
./install_browser.sh
```
