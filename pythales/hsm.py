#!/usr/bin/env python

import getopt
import sys
import socket
import struct 

from tracetools.tracetools import trace

class Message:
    def __init__(self, data=None, header=None):
        if data:
            self.length = struct.unpack_from("!H", data[:2])[0]
            if(self.length != len(data) - 2):
                raise ValueError('Expected message of length {0} but actual received message length is {1}'.format(self.length, len(data) - 2))
    
            if header:
                for h, d in zip(header, data[2:]):
                    if h != d:
                        raise ValueError('Invalid header')
            if header:
                self.data = data[2 + len(header) : ]
            else:
                self.data = data[2:]
    
    def get_length(self):
        """
        """
        return self.length

    def get_data(self):
        """
        """
        return self.data



class HSM:
    def __init__(self, port=None, header=None):
        self.firmware_version = '0007-E000'

        if port:
            self.port = port
        else:
            self.port = 1500

        if header:
            self.header = bytes(header, 'utf-8')
        else:
            self.header = b''

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('', self.port))   
            self.sock.listen(5)
            print('Listening on port {}'.format(self.port))
        except OSError as msg:
            print('Error starting server: {}'.format(msg))
            sys.exit()

        while True:
            conn, addr = self.sock.accept()
            print ('Connected client: ' + addr[0] + ':' + str(addr[1]))

            while True:
                try:
                    data = conn.recv(4096)
                    trace('<< {} bytes received: '.format(len(data)), data)
                        
                    Len = struct.unpack_from("!H", data[:2])[0]
                    if(Len != len(data) - 2):
                        print("Invalid length {0} - {1}".format(Len, len(data) - 2))
                        continue

                    request = Message(data, header=self.header)

                    response = struct.pack("!H", len(response)) + self.get_response(request.get_data())
                    conn.send(response)
                    trace('>> {} bytes sent:'.format(len(response)), response)
    
                except KeyboardInterrupt:
                    print('Exit')
                    s.close()
                    sys.exit()
    

    def get_diagnostics_data(self):
        lmk_check_value = '1234567890ABCDEF'
        return lmk_check_value + self.firmware_version



    def get_response(self, request):
        rqst_command_code = request[:2]
        resp_command_code = None
        error_code = b'00'
        resp_data = ''

        if rqst_command_code == b'NC':
            resp_command_code = b'ND'
            resp_data = self.get_diagnostics_data()
        else:
            resp_command_code = b'ZZ'
            error_code = b'00'

        return resp_command_code + error_code + bytes(resp_data, 'utf-8')


def show_help(name):
    """
    Show help and basic usage
    """
    print('Usage: python3 {} [OPTIONS]... '.format(name))
    print('Thales HSM command simulator')
    print('  -p, --port=[PORT]\t\tTCP port to listen, 1500 by default')
    print('  -h, --header=[HEADER]\t\tmessage header, empty by default')

if __name__ == '__main__':
    port = None
    header = ''

    optlist, args = getopt.getopt(sys.argv[1:], 'h:p:', ['header=', 'port='])
    for opt, arg in optlist:
        if opt in ('-h', '--header'):
            header = arg
        elif opt in ('-p', '--port'):
            try:
                port = int(arg)
            except ValueError:
                print('Invalid TCP port: {}'.format(arg))
                sys.exit()
        else:
            show_help(sys.argv[0])
            sys.exit()

    hsm = HSM(port, header)
    hsm.run()


    
