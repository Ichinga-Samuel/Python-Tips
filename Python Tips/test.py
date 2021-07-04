import subprocess
import os

import os
stream = os.popen("""typeperf "\System\Processes" "\Process(_Total)\% Processor Time" "\Memory\Available MBytes""""")
max = 395
n = 0
while True:
    b = stream.readline()
    print(b)
    try:
        t = b.split(',')[2]
        t = t.strip('"')
        t = float(t)
        if t > max:
            n += 1
        if n >= 5:
            print('hey')
    except:
        continue
