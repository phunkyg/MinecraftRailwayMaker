import subprocess
import time
import threading
import sys
import signal
WD = '/opt/test_server'
SERVERCMD = '. {}/start.sh'.format(WD)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_fb(msg):
    print(bcolors.WARNING + str(msg) + bcolors.ENDC)

class Reader(threading.Thread):
    """Thread class to poll for output"""
    def __init__(self, proc):
        """set up the thread"""
        super(Reader, self).__init__()
        self.daemon = True
        self.name = 'thread_reader'
        self.proc = proc
        self.keep_running = True
        self.waiting = False

    def run(self):
        """process output reader loop"""
        pcon = False
        while self.keep_running and not self.proc.poll():
            out = self.proc.stdout.readline()
            if out != '':
                pr = out.decode("utf-8")
                sys.stdout.write(pr)
                sys.stdout.flush()
                if pr[27:43] == "Player connected":
                    pcon = True

                if self.waiting and pcon:
                    self.waiting = False                    
        print_fb('Reader is terminating')
    
    def wait(self):
        self.waiting = True
        while self.waiting or self.waiting is None:
            time.sleep(0.1)

    def stopme(self):
        self.keep_running = False

p = subprocess.Popen(
    SERVERCMD,
    cwd = WD,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True)

r = Reader(p)
r.start()


cmds = []

with open('./generated_commands.txt', 'rU') as f:
  for line in f:
     cmds.append(bytes(line, 'utf-8'))

#cmds.append(b"stop")

print_fb('started... waiting...')
r.wait()
print_fb('Played connection detected...')
time.sleep(16)


for cmd in cmds:
    print(bcolors.OKBLUE + cmd.decode("utf-8") + bcolors.ENDC)
    p.stdin.write(cmd)
    # if cmd[-1] != b"\n":
    #     p.stdin.write(b"\n")
    p.stdin.flush()
    r.wait()
    if cmd[:2] == b"tp":
        time.sleep(5)

inp = ""
while inp != "stop\n":
    inp = input('/') + "\n"
    #print_fb(inp)
    p.stdin.write(bytes(inp, 'utf-8'))
    p.stdin.flush()
    r.wait()


#print_fb('waiting for server to quit')


p.wait()
r.stopme()
print_fb('finished')

