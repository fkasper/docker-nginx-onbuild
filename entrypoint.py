#!/usr/bin/env python

from optparse import OptionParser
import etcd
import socket
import subprocess
from pwd import getpwnam
import os
import signal
import sys
import select
import os.path

def setup_discovery(options, args):
    hostname = args[0]
    if hostname.startswith("www."):
        hostname = hostname.replace("www.", "")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com",80))

        inetaddr = s.getsockname()[0]
    except:
        print "Network error!"
    finally:
        s.close()
    try:
        client = etcd.Client(host=options.etcd_host, port=options.etcd_port, protocol=options.etcd_protocol)
    except Exception as e:
        print "error: %s" % str(e)

    additionalBackendsFile = '/app/backends'
    if os.path.isfile(additionalBackendsFile):
        with open(additionalBackendsFile) as f:
            content = f.readlines()
            for line in content:
                r = line.rstrip('\n').split(" ")
                client.write('/vulcand/backends/%s/backend' % r[1], '{"Type": "http"}')
                client.write('/vulcand/backends/%s/servers/%s' % (r[1], options.server_reg_name), '{"URL": "http://%s:%s"}' % (inetaddr, r[0]))
    else:
        client.write('/vulcand/backends/%s/backend' % hostname, '{"Type": "http"}')
        client.write('/vulcand/backends/%s/servers/%s' % (hostname, options.server_reg_name), '{"URL": "http://%s:%d"}' % (inetaddr, options.discovery_port))

    additionalFrontendsFile = '/app/additionalPaths'
    if os.path.isfile(additionalFrontendsFile):
        with open(additionalFrontendsFile) as f:
            content = f.readlines()
            for line in content:
                c = line.rstrip('\n').split(" ")
                print str(c)
                client.write('/vulcand/frontends/%s-%s/frontend' % (hostname, c[1]), '{"Type": "http", "BackendId": "%s", "Route": "Host(`%s`) && %s"}' % (c[0], hostname, c[2]))
    

def start_service(args, opts):
    os.environ['ETCD_URL'] = opts.etcd_host
    os.environ['REG_NAME'] = args[0]
    uid = getpwnam('www-data').pw_uid
    path = "/app"
    for root, dirs, files in os.walk(path):
      for momo in dirs:
        os.chown(os.path.join(root, momo), uid, -1)
      for momo in files:
        os.chown(os.path.join(root, momo), uid, -1)

    p = subprocess.Popen(args[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        reads = [p.stdout.fileno(), p.stderr.fileno()]
        ret = select.select(reads, [], [])

        for fd in ret[0]:
            if fd == p.stdout.fileno():
                read = p.stdout.readline()
                sys.stdout.write('stdout: ' + read)
            if fd == p.stderr.fileno():
                read = p.stderr.readline()
                sys.stderr.write('stderr: ' + read)

        if p.poll() != None:
            break
    print "returncode of subprocess:"
    print p.returncode

def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-d", "--discovery-port",
                      action="store",
                      dest="discovery_port",
                      default=80,
                      help="Sets the Port for the Service")
    parser.add_option("-s", "--server-reg-name",
                      action="store",
                      dest="server_reg_name",
                      default="srv1",
                      help="Sets the Server Registration anme")
    parser.add_option("-e", "--etcd-host",
                      action="store", # optional because action defaults to "store"
                      dest="etcd_host",
                      default="etcd.xcms.com",
                      help="Set the ETCD Host",)
    parser.add_option("-p", "--etcd-port",
                      action="store", # optional because action defaults to "store"
                      dest="etcd_port",
                      type="int",
                      default=4001,
                      help="Set the ETCD Port",)
    parser.add_option("-P", "--etcd-protocol",
                      action="store", # optional because action defaults to "store"
                      dest="etcd_protocol",
                      default="http",
                      help="Set the ETCD Protocol",)
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("wrong number of arguments. Expected at least 1")

    setup_discovery(options, args)
    start_service(args, options)


if __name__ == "__main__":
    main()
