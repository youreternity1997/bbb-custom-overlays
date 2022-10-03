### Install image graphic packages

```
sudo apt-get install gimp
sudo apt-get install imagemagick
```



### Convert JPG to PNG

```
convert Logo.jpg -colors 224 -resize 480x272 logo480x242_224.png
```



### Open PNG, File -> Export as ppm

```
gimp logo480x242_224.png
```

![](/home/karlt/Pictures/Screenshot from 2022-07-14 13-50-11.png)



### Converting the picture to ASCII format

```
ppmquant 224 logo480x242_224.ppm > logo480x242_224_02.ppm
pnmnoraw logo480x242_224_02.ppm > logo480x242_ascii_224.ppm
```



### Copy .ppm to kernel then rebuild kernel

```
cp logo480x242_ascii_224.ppm "lcoal kernel patth"/drivers/video/logo/logo_linux_clut224.ppm
```


### Rebuild kernel
Kernel location : /home/ti-linux-kernel-dev/
Rebuild kernel
```
sudo /home/ti-linux-kernel-dev/tools/rebuild.sh
```
Then, choose the "save" button. Keep rebuild to 12 hours.


### Set uname_r in /boot/uEnv.txt
```
sudo sh -c "echo 'uname_r=${kernel_version}' >> /boot/uEnv.txt"
```

### Move the file from deploy (/home/ti-linux-kernel-dev/deploy/)
```
sudo cp -v /home/ti-linux-kernel-dev/deploy/${kernel_version}.zImage  /boot/vmlinuz-${kernel_version}
```
### Copy Kernel Device Tree Binaries
```
sudo mkdir -p /boot/dtbs/${kernel_version}/
sudo tar xfv /home/ti-linux-kernel-dev/deploy/${kernel_version}-dtbs.tar.gz -C /boot/dtbs/${kernel_version}/
```

### Copy Kernel Modules
```
sudo tar xfv /home/ti-linux-kernel-dev/deploy/${kernel_version}-modules.tar.gz -C  /
```
