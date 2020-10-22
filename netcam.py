#Author Techtic at Onlinewarriorspodcast.com
from flask import Flask, render_template_string, request,render_template_string,render_template, Response # Importing the Flask modules 
import RPi.GPIO as GPIO     # Importing the GPIO library 
import time
import io
import threading
import picamera

#############Credit Mequel Grinberg#######

class Camera(object):
    thread = None
    frame  = None
    last_access = 0
    
    def initialize(self):
        if Camera.thread is None:
            
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()
            
            while self.frame is None:
                time.sleep(0)
    
    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame
    
    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            
            camera.resolution = (320, 240)
            camera.hflip = True
            camera.vflip = False
            camera.framerate=24
            
            #camera.start_preview()
            time.sleep(1)
            
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                use_video_port=True):
                
                stream.seek(0)
                cls.frame=stream.read()
                
                stream.seek(0)
                stream.truncate()
                
                if time.time()-cls.last_access>10:
                    break
        cls.thread=None
            
##############################

servo_pin = 19 
GPIO.setmode(GPIO.BCM)      

GPIO.setup(servo_pin, GPIO.OUT)     
p = GPIO.PWM(servo_pin, 50)  
p.start(0)

servo_pin2 = 13 

GPIO.setup(servo_pin2, GPIO.OUT)     
p2 = GPIO.PWM(servo_pin2, 50)  
p2.start(0)

app = Flask(__name__)
#HTML Code 
#

TPL = '''
<html>

    <head><title>Web Page Controlled Camera</title></head>
    <body onload="getval()">
    
    
    <script>
function storeval() {

var slider = document.getElementById("slider");
localStorage.setItem("LastPos1" ,slider.value);

var slider2 = document.getElementById("slider2");
localStorage.setItem("LastPos2" ,slider2.value);
}
</script>

<script>
function getval(){

var x = document.getElementById("slider").value = localStorage.getItem("LastPos1");
var y = document.getElementById("slider2").value = localStorage.getItem("LastPos2");
}
</script>

    <h1><img src="{{ url_for('video_feed')}}" width="100%" /></h1>
     <div>
        <form method="POST" action="test">
            <h2> Use the slider to pan camera</h2>

            <p>Slider   <input id = "slider" type="range" min="2.2" max="12.5" name="slider" style = "width:90%" />

            
            <p>Slider   <input id = "slider2" type="range" min="2.2" max="12.5" name="slider2" style = "width:90%"/> </p>
            
            
            <p><input type="submit" value="submit" style ="height: 100px;width:100px;font-size:25px" onclick="storeval()"/>
            </p>
            <p id="demo"></p> 
       </form>
       </div>
       



</body>
</html>

'''
@app.route("/")
def home():
    return render_template_string(TPL)

def gen(camera):
    while True:
        frame=camera.get_frame()
        
            #frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +frame +b'\r\n')
        

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/test", methods=["POST"])
def test():
    slider = request.form["slider"]
    p.ChangeDutyCycle(float(slider))
    time.sleep(1)
    p.start(0)
    slider2 = request.form["slider2"]
    p2.ChangeDutyCycle(float(slider2))
    time.sleep(1)
    p2.start(0)

    return render_template_string(TPL)
# Run the app on the local development server
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,threaded = True)

