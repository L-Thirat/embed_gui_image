import glob
import os
import shutil

inp_sources = glob.glob('%s*' % 'frame/1/')
sample_sources = glob.glob('%s*' % "static/output/compare/2021/3/12/")

for img, filename in zip(inp_sources, sample_sources):
    img = img.replace("\\", "/")
    if "OK" in filename:
        # os.rename(img, "ok/"+img)
        pass
    else:
        print(img, filename)
