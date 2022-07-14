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
copy logo480x242_ascii_224.ppm "lcoal kernel patth"/drivers/video/logo/logo_linux_clut224.ppm
```

