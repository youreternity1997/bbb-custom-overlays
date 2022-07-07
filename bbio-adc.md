### Python ADC sample

```javascript
import Adafruit_BBIO.ADC as ADC

ADC.setup()
value = ADC.read("P9_40")
voltage = value * 1.8 #1.8V
print voltage
```



### Python test code

```
>>> import Adafruit_BBIO.ADC as ADC
>>> ADC.setup()
>>> value = ADC.read("AIN1")
>>> voltage = value * 1.8
>>> print voltage
1.60131869316
>>> value = ADC.read("AIN1")
>>> voltage = value * 1.8
>>> print voltage
1.06813191175
>>> value = ADC.read("AIN1")
>>> voltage = value * 1.8
>>> print voltage
1.06945059299
>>> value = ADC.read("AIN1")
>>> voltage = value * 1.8
>>> print voltage
0.534065955877
>>> ADC.setup()
>>> 
>>> value = ADC.read("AIN1")
>>> voltage = value * 1.8
>>> print voltage
1.60087913275
>>> value = ADC.read("P9_40")
>>> voltage = value * 1.8
>>> print voltage
1.60043957233
>>> value = ADC.read_raw("P9_40")
>>> print value
3640.0
>>> 
```

