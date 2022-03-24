from pycreate2 import Create2
import socketserver

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    port = "/dev/ttyUSB0"  # where is your serial port?
    bot = Create2(port)
    left_motor = 100  # Speed in mm/s
    right_motor = 100  # Speed in mm/s
    previous_i = ''

    def setup(self):
        # Start the Create 2
        self.bot.start()

        # Put the Create2 into 'safe' mode so we can drive it
        # This will still provide some protection
        self.bot.safe()
        self.request.sendall(b'f-forward r-right l-left b-backwards h-hault q-quicker s-slower e-end')


    def handle(self):
        while True:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            self.data = self.data.decode("utf-8")

            if self.data == 'f':
                self.bot.drive_direct(self.right_motor, self.left_motor)
                self.previous_i = 'f'
                self.request.sendall(b'Forward')
                
            elif self.data == 'r':
                self.bot.drive_direct(-self.right_motor, self.left_motor)
                self.previous_i = 'r'
                self.request.sendall(b'Right')
                
            elif self.data == 'l':
                self.bot.drive_direct(self.right_motor, -self.left_motor)
                self.previous_i = 'l'
                self.request.sendall(b'Left')
                
            elif self.data == 'b':
                self.bot.drive_direct(-self.right_motor, -self.left_motor)
                self.previous_i = 'b'
                self.request.sendall(b'Backwards')
                
            elif self.data == 'q':
                self.right_motor = int(self.right_motor * 2)
                self.left_motor = int(self.left_motor * 2)
                self.request.sendall(b'Quicker')
                if self.previous_i == 'f':
                    self.bot.drive_direct(self.right_motor, self.left_motor)
                elif self.previous_i == 'r':
                    self.bot.drive_direct(-self.right_motor, self.left_motor)
                elif self.previous_i == 'l':
                    self.bot.drive_direct(self.right_motor, -self.left_motor)
                elif self.previous_i == 'b':
                    self.bot.drive_direct(-self.right_motor, -self.left_motor)
                
            elif self.data == 's':
                self.right_motor = int(self.right_motor / 2)
                self.left_motor = int(self.left_motor / 2)
                self.request.sendall(b'Slower')
                if self.previous_i == 'f':
                    self.bot.drive_direct(self.right_motor, self.left_motor)
                elif self.previous_i == 'r':
                    self.bot.drive_direct(-self.right_motor, self.left_motor)
                elif self.previous_i == 'l':
                    self.bot.drive_direct(self.right_motor, -self.left_motor)
                elif self.previous_i == 'b':
                    self.bot.drive_direct(-self.right_motor, -self.left_motor)
                    
            elif self.data == 'h':
                self.bot.drive_direct(0, 0)
                self.request.sendall(b'Hault')
                
            elif self.data == 'e':
                self.bot.drive_stop()
                self.request.sendall(b'End')
            
            else:
                self.request.sendall(b'Invalid Command')


if __name__ == '__main__':
    HOST, PORT = '0.0.0.0', 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C

        server.serve_forever()
