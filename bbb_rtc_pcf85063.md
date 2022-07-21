### RTC1 PCF85063 Debug

Register 04h = c4h the Bit 7 = 1

Oscillator has stopped or has been interrupted refer to [datasheet page 21](https://www.nxp.com/docs/en/data-sheet/PCF85063A.pdf)

```
debian@arm:~$ sudo i2cdump -y -f -r 0-15 2 0x51
[sudo] password for debian: 
No size specified (using byte-data access)
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f    0123456789abcdef
00: 00 00 00 00 c4 02 00 01 06 01 00 80 80 80 80 80    ....??.???.?????
```

The Bit 7 cause the problem hwclock read rtc1 time failure

```
debian@arm:~$ sudo hwclock -r -f /dev/rtc1
hwclock: ioctl(RTC_RD_TIME) to /dev/rtc1 to read the time failed: Invalid argument
```

Clear Bit 7 then use hwclock read rtc1 time

```
debian@arm:~$ sudo i2cset -y -f 2 0x51 0x4 0x0
debian@arm:~$ sudo hwclock -r -f /dev/rtc1
2000-01-01 00:23:06.838799+08:00
```



### RTC0 Function Check

```
debian@arm:~$ sudo hwclock -r -f /dev/rtc0
2000-01-01 00:28:59.250631+08:00
```



### Workaround

[Refer to article](https://app.bountysource.com/issues/65269943-pcf8523-hwclock-ioctl-rtc_rd_time-to-dev-rtc-to-read-the-time-failed-invalid-argument)



### Sync Time TBD

timedatectl

