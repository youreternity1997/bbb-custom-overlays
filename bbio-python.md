### Install Adafruit BBIO and Python

```sql
sudo apt-get update
sudo apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y
```

### Test your installation

```php
sudo python -c "import Adafruit_BBIO.GPIO as GPIO; print GPIO"

#you should see this or similar:
<module 'Adafruit_BBIO.GPIO' from '/usr/local/lib/python2.7/dist-packages/Adafruit_BBIO/GPIO.so'>
```