### Default set UART4 in uboot_overlay_addr1 in /boot/uEnv.txt

```
###Overide capes with eeprom
uboot_overlay_addr0=/lib/firmware/BB-RAYSTAR-TOUCHPAD-00A0.dtbo
uboot_overlay_addr1=/lib/firmware/BB-UART4-00A0.dtbo
```



### (Option) Power on/off GPS

```
# power-on GPS
sudo config-pin p9.12 1
# power-off GPS
sudo config-pin p9.12 0
```



### Test GPS via UART4

```
debian@arm:~$ sudo minicom -D /dev/ttyS4 -b 9600 -s
In Serial port setup -> Hardware Flow Control -> No

$GNRMC,,V,,,,,,,,,,N,V*37                                                    
$GNVTG,,,,,,,,,N*2E                                                          
$GNGGA,,,,,,0,00,99.99,,,,,,*56                                              
$GNGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99,1*33                                
$GNGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99,3*31                                
$GNGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99,4*36                                
$GPGSV,1,1,00,0*65                                                           
$GAGSV,1,1,00,0*74                                                           
$GBGSV,1,1,00,0*77                                                           
$GNGLL,,,,,,V,N*7A                                                           
$GNRMC,,V,,,,,,,,,,N,V*37                                                    
$GNVTG,,,,,,,,,N*2E                                                          
$GNGGA,,,,,,0,00,99.99,,,,,,*56                                              
$GNGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99,1*33
$GNGSA,A,1,,,,,,,,,,,,,99
```

