import numpy as np
import cv2
from matplotlib import pyplot as plt


for i in range(10):
    vid = cv2.VideoCapture(i)
    if vid.isOpened():
        break

while True:
    ret, img = vid.read()
    # img = cv2.imread("WIN_20201210_10_12_37_Pro.jpg")
    #img = np.zeros((200,200), np.uint8)
    #cv.rectangle(img, (0, 100), (200, 200), (255), -1)
    #cv.rectangle(img, (0, 50), (100, 100), (127), -1)
    b, g, r = cv2.split(img)
    cv2.imshow("img", img)
    cv2.imshow("b", b)
    cv2.imshow("g", g)
    cv2.imshow("r", r)
    print(b.sum()/(len(b)*len(b[0])))
    print(g.sum()/(len(g)*len(g[0])))
    print(r.sum()/(len(r)*len(r[0])))
    plt.hist(b.ravel(), 256, [0, 256])
    plt.hist(g.ravel(), 256, [0, 256])
    plt.hist(r.ravel(), 256, [0, 256])

    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    plt.plot(hist)
    plt.show()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
vid.release()
cv2.destroyAllWindows()