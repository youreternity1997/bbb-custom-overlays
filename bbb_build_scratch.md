### BeagleBoard.org

- #### Download [Latest Firmware Images](https://beagleboard.org/latest-images)

- #### Flash sd-card 4/32 GB 

```
xz -d bone-debian-10.3-iot-armhf-2020-04-06-4gb.img.xz
sudo dd if=bone-debian-10.3-iot-armhf-2020-04-06-4gb.img of=/dev/sdX bs=4096 status=progress
```



### (Option) BBB build from scratch

* #### [Linux Kernel](https://forum.digikey.com/t/debian-getting-started-with-the-beaglebone-black/12967#install-kernel-and-root-file-system-13)

* #### [Install Kernel](https://forum.digikey.com/t/debian-getting-started-with-the-beaglebone-black/12967#install-kernel-and-root-file-system-13)



### Install BBIO on Debian

```
sudo apt-get update
sudo apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y
sudo pip install Adafruit_BBIO
```



### Install tkinter, matplotlib and other packages .. takes over 30 mins

```
sudo apt-get install python3-tk
pip3 install matplotlib
pip3 install pyserial
pip3 install opencv-python
sudo apt-get install python-opencv
pip3 install zxing
```
