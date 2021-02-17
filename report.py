import glob
from collections import Counter

sample_source = "frame/1/"
files = glob.glob('%s*' % sample_source)
image_times = []

for file in files:
    t = file[25:27]
    image_times.append(t)

print(Counter(image_times))
print(len(set(image_times)))
