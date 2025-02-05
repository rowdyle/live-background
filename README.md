worke on windows 10. <br>
worke on 1/2 monitors (didnt check on 3 but it will probly bee ez to do it for more to). <br>
have a power save mode when the background is not visbale.

you need to dawnlowd cv2 and pyqt5:
1. press win + r
2. write cmd
3. paste the commends below:

pip install pyqt5 <br>
pip install opencv-python

<br>
and you nead to change in the backgrond.py the path to the video you want to live, it in the top after the imports its nead full root ("c:/path/to/your.mp4").
<br> <br>
if you want to make it run with out the cli you nead to change the end of the file to .pyw <br>

if you want it to run when you boot follow this steps:
1. press win + r
2. wirte shell:startup
3. paste the py file in this folder
