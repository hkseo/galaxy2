class Joystick(QObject):

''' all of chris' joystick code '''

    ARM_ADDRESS = chr(0x10)  # since pyserial likes to get them as strings.
    SENSOR_ADDRESS = chr(0x11)
    DRIVE_ADDRESS = chr(0x12)

    def __init__(self):
        QObject.__init__(self)
        pygame.init()
        self.j = pygame.joystick.Joystick(0)
        self.j.init()
        pygame.joystick.init()

        self.ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
        self.pser = PacketSerial(self.ser)
        self.starttime = time.time()
        self.update_rate = 10
        self.timer = QTimer(self)

        self.joystick_controls_arm = False

    def start_joystick(self):
		self.timer.setInterval(0)
		self.connect(self.timer, SIGNAL('timeout()'), self.main)
		self.timer.start()

    def end_joystick(self):
        self.timer.stop()

    def main(self):
        for event in pygame.event.get(): # User did something
            pass   # ignore events.
        
        if (self.joystick_controls_arm): # send joystick commands to the arm 
            if(abs(self.j.get_axis(1)) < 0.1): 
                self.pser.write((self.ARM_ADDRESS, '0', '\x00', '\x00')) # don't let drift affect the arm
            elif(self.j.get_axis(1) > 0):
                self.pser.write((self.ARM_ADDRESS, '2', '\x00', '\x00'))
            else:
                self.pser.write((self.ARM_ADDRESS, '1', '\x00', '\x00')) 
        else:  # joystick controls drive system
            '''vertical_axis = self.j.get_axis(1)#vertical_axis input
            horizontal_axis = self.j.get_axis(0)# horizontal_axis input
            lever = -(self.j.get_axis(2)-1)/2 #the shiftable joystick in the bottom "+" and "-" to control the speed, scaled to the desired high to low position

            if(vertical_axis*100<0):#when the vertical axis is pushed up
                forward_backward=93+vertical_axis*63*lever
                forward_backward=int(forward_backward)
            elif(vertical_axis*100>0):#when the vertical axis is pushed down
                forward_backward=93+vertical_axis*57*lever
                forward_backward=int(forward_backward)
               
            if(horizontal_axis*100<0):#when pushed left
                left_right=93+horizontal_axis*63*lever
                left_right=int(left_right)        
            elif(horizontal_axis*100>0):#when pushed right
                left_right=93+horizontal_axis*67*lever
                left_right=int(left_right)
               
            if(vertical_axis==0):
                forward_backward=93 #rest values- no motion
            if(horizontal_axis==0):
                left_right=93 #rest values- no motion '''
            forward_backward = int(self.j.get_axis(1) * 100 + 100)
            left_right = int(self.j.get_axis(2) * 100 + 100)
            self.pser.write((self.DRIVE_ADDRESS, chr(left_right), chr(forward_backward), '\x07'))
            self.pser.write((self.DRIVE_ADDRESS, chr(left_right), chr(forward_backward), '\x07'))
            
        # Switch between arm and drive system 
        if self.j.get_button(9):
            self.joystick_controls_arm = not self.joystick_controls_arm
            print("Switched joystick control of arm/ drive")
            # TODO: Stop all motion when switching between systems

        #data = self.pser.read()
        #data2 = self.pser.read()
        #print("Sensor data: ", data, data2)

        #time.sleep(0.1)
        if time.time() - self.starttime > 5:
            self.ser.flushInput() 
            self.ser.flushOutput()
            self.starttime = time.time()