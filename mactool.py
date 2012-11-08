#!/usr/bin/env python
import sys
import os
from urllib import urlopen
from random import randrange,seed
from pickle import dump, load

_OUI_URL = "http://standards.ieee.org/regauth/oui/oui.txt"
_MACFILE = os.path.expanduser("~/.macvendors.txt")
_MACPIKL = os.path.expanduser("~/.macvendors.pkl")


_V_VMWARE = '00:0c:29'

def rand_hex(num):
    return [hex(randrange(0,255)).split("x")[1].zfill(2) for n in range(0,num)]

def rand_vmware():
    l = _V_VMWARE.split(":")
    l.extend(rand_hex(3))
    return ':'.join(l)

rand_global = lambda: ':'.join(rand_hex(6))

def format_line(line):
    s = line.split()
    return s[0], ' '.join(x.lower().capitalize() for x in s[2:])

def download_oui():
    #f = file(filename,"r")
    f = urlopen(_OUI_URL)
    o = file(_MACFILE,"w+")
    lines = (format_line(l) for l in f if "(hex)" in l)
    o.writelines( ','.join(x)+"\n" for x in lines)
    o.close()
    print "OUI File downloaded to %s" % _MACFILE

    macvendors = file(_MACFILE,'r')
    format_entry = lambda x: ( x[0].replace('-',':'), x[1] )
    vendordict = dict(
        format_entry(e.strip().split(',',1)) for e in macvendors
    )
    dump(vendordict, file(_MACPIKL,'wb'))
    print "OUI dict pickled to %s" % _MACPIKL

OUI = None
def load_oui():
    global OUI
    OUI = load(open(_MACPIKL))

mac_to_prefix = lambda s: ':'.join( s.split(':')[:3] ).upper()

def mac_to_vendor(mac):
    return OUI[mac_to_prefix(mac)]

def find_vendor(vendor):
    return ( (k,v) for k,v in OUI.iteritems() if vendor in v)

def mac_from_prefix(prefix):
    p = prefix.replace("-",":")[:8]
    l = p.split(":")
    if len(l) is not 3:
        raise Exception("Bad prefix")
    l.extend(rand_hex(3))
    return (':'.join(l)).upper()

def mac_from_vendor(vendor):
    l = [k for k,v in find_vendor(vendor)]
    return mac_from_prefix(l[randrange(0,len(l))]) # TODO

if __name__=="__main__":
    _VERSION = 0.2
    seed()

    from optparse import OptionParser
    arg = OptionParser(version="%prog 0.1")
    arg.add_option("-d","--download",
            dest="download",
            action="store_true",
            help="Download latest MAC list")
    arg.add_option("-m","--mac",
            dest="mac",
            help="MAC Address to Convert to Vendor String")
    arg.add_option("-v","--vendor",
            dest="vendor",
            help="Vendor to search for prefixes")
    arg.add_option("-r","--random",
            dest="rand",
    action="store_true",
            help="Generate random MAC")
    arg.add_option("-a",
            dest="stdall",
            action="store_true",
            help="Convert all arom stdin")
    arg.add_option("-R",
            dest="stdregex",
            action="store_true",
            help="Regex all from stdin")

    (options, args) = arg.parse_args()
    if(options.download):
        download_oui()

    load_oui()

    if(options.vendor and options.rand):
        print mac_from_vendor(options.vendor)
    elif(options.vendor):
        for result in find_vendor(options.vendor):
            print result

    if(options.mac and options.rand):
        print mac_from_prefix(options.mac)
    elif(options.mac):
        print mac_to_vendor(options.mac)

    if(options.stdall):
        ilines = sys.stdin.readlines()
        for x in ilines:
            print "%s -> %s" % (x.strip(), mac_to_vendor(x))

    if(options.stdregex):
        import re
        rgx = re.compile(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', re.I)
        ilines = sys.stdin.readlines()
        for x in ilines:
            search = rgx.search(x)
            #.group() # TODO: multiple matches per line
            if search:
                match = search.group()
                try:
                    vendor = mac_to_vendor(match)
                except KeyError, e:
                    vendor = "\\\0"
                x = x.replace(match, "%s  %-20s" % (match, vendor))
            print x,


