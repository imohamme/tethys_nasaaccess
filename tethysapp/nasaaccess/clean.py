import os
import shutil
import time

# make sure to have the outputs folder as a custom settings
path = ""
now = time.time()
for filename in os.listdir(path):

    if os.path.getmtime(os.path.join(path, filename)) < now - 5 * 86400:
        if os.path.isdir(os.path.join(path, filename)):
            print(filename)
            shutil.rmtree(os.path.join(path, filename))
