# fkafka
fkafka is used to deal with massive amount of log data from kafka.

Before putting the guid info into the nebular, we need a script to help us find what is important.

So I wrote this script.

```
python fkafka.py -f <your log file>

-f: input file
-t: display time
-m: display md5 value
```
