### BeagleBoard.org

- #### Download [Latest Firmware Images](https://beagleboard.org/latest-images)

- #### Flash sd-card 4/32 GB 

```
xz -d bone-debian-10.3-iot-armhf-2020-04-06-4gb.img.xz
sudo dd if=bone-debian-10.3-iot-armhf-2020-04-06-4gb.img of=/dev/sdX bs=4096 status=progress
```



### BBB build kernel and kernel modules from scratch

* #### [Linux Kernel](https://forum.digikey.com/t/debian-getting-started-with-the-beaglebone-black/12967#install-kernel-and-root-file-system-13)

  * [Set uname_r in /boot/uEnv.txt](https://forum.digikey.com/t/debian-getting-started-with-the-beaglebone-black/12967#set-uname_r-in-bootuenvtxt-15)
  * [Copy Kernel Image](https://forum.digikey.com/t/debian-getting-started-with-the-beaglebone-black/12967#copy-kernel-image-16)
  * [Copy Kernel Device Tree Binaries](https://forum.digikey.com/t/debian-getting-started-with-the-beaglebone-black/12967#copy-kernel-device-tree-binaries-17)
  * [Copy Kernel Modules](https://forum.digikey.com/t/debian-getting-started-with-the-beaglebone-black/12967#copy-kernel-modules-18)

* #### [Install Kernel](https://forum.digikey.com/t/debian-getting-started-with-the-beaglebone-black/12967#install-kernel-and-root-file-system-13)



### Add touchscreen driver, and rebuild the kernel and module

```
unzip touchscreen_ilitek_ts_i2c.zip -d <local kernel path>/ti_kernelbuildscripts/KERNEL
cd <local kernel path>/ti_kernelbuildscripts>
./tools/rebuild.sh

Select -> Device Drivers
	       -> Input Devices
		      -> TouchScreen
```

![](/home/karlt/Pictures/kernel_ilitek.png)



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
