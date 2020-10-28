import urllib
import cv2
import numpy as np



# //////////////////// QRCODE Reader //////////////////////////// #
# from pyzbar.pyzbar import decode
# from PIL import Image
# import cv2
# import ast
# import webbrowser
#
# cap = cv2.VideoCapture(0)
# while True:
#     ret,frame = cap.read()
#     # decode(Image.open('pyzbar/tests/code128.png'))
#     cv2.imshow('frame',frame)
#     if cv2.waitKey(20) & 0xFF == ord('q'):
#         break
#     if decode(frame):
#         # print(decode(frame))
#         byte_str = decode(frame)[0].data
#         dict_str = byte_str.decode("UTF-8")
#         mydata = ast.literal_eval(dict_str)
#         print(mydata)
#         url = mydata["url"]
#         user = mydata["user"]
#         password = mydata["password"]
#         conv_url = "http://admin:admin@" + url[9:] + "/video"
#         print(conv_url)
#         webbrowser.open_new(conv_url)
#         break
#
# cap.release()
# cv2.destroyAllWindows()

# ///////////////////// RTSP connect /////////////////// #

# # import rtsp
# # client = rtsp.Client(rtsp_server_uri = 'rtsp://172.18.1.248:8554/live')
# # client.read().show()
# # client.close()
#
#
# import pafy
# import cv2
#
# # url = 'http://172.18.1.248:8081/video'
# # vPafy = pafy.new(url)
# # play = vPafy.getbest(preftype="webm")
# #
# # #start the video
# # cap = cv2.VideoCapture(play.url)
# cap = cv2.VideoCapture('rtsp://admin:admin@172.18.1.248:8554/live')
# while True:
#     ret,frame = cap.read()
#     """
#     your code here
#     """
#     # print(frame.shape())
#     cv2.imshow('frame',frame)
#     if cv2.waitKey(20) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()