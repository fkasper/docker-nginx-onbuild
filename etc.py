#!/usr/bin/env python

from optparse import OptionParser
import etcd
import socket

def get_values_from_etcd(options, args):
    hostname = args[0]
    try:
        client = etcd.Client(host=options.etcd_host, port=options.etcd_port, protocol=options.etcd_protocol)
    except:
        print "Error!"
    print client.read('/xcms/legacy/wordpress/database/%s/%s' % (args[0], args[1] )).value

def main():
    parser = OptionParser(usage="usage: %prog [options] hostname query",
                          version="%prog 1.0")
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

    get_values_from_etcd(options, args)


if __name__ == "__main__":
    main()

