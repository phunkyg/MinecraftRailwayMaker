import subprocess
import time
import threading
import sys
import signal
WD = '/opt/test_server'
SERVERCMD = '. {}/start.sh'.format(WD)



class Reader(threading.Thread):
    """Thread class to poll for output"""
    def __init__(self, proc):
        """set up the thread"""
        super(Reader, self).__init__()
        self.daemon = True
        self.name = 'thread_reader'
        self.proc = proc
        self.keep_running = True

    def run(self):
        """process output reader loop"""
        while self.keep_running and not self.proc.poll():
            out = self.proc.stdout.readline()
            if out != '':
                pr = out.decode("utf-8")
                sys.stdout.write(pr)
                sys.stdout.flush()
        print('Reader is terminating')

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

print('started... waiting...')
time.sleep(20)
print('starting send')

cmds = [
    b"tp @p 0 4 0",
    b"tp @p 100 4 0",
    b"tp @p 200 4 0",
    b"tp @p 300 4 0",
    b"tp @p 400 4 0",
    b"stop"
]

for cmd in cmds:
    print('sending')
    p.stdin.write(cmd+ b"\n")
    p.stdin.flush()
    time.sleep(4)

print('waiting for server to quit')
p.wait()
#r.stopme()
print('finished')

