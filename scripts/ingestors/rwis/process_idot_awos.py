"""Process AWOS METAR file"""
from __future__ import print_function
import re
import tempfile
import os
import datetime
import urllib2
import subprocess

import pyiem.util as util

INCOMING = "/mesonet/data/incoming"


def fetch_files():
    """Fetch files """
    props = util.get_properties()

    fn = "%s/iaawos_metar.txt" % (INCOMING, )
    data = urllib2.urlopen(("ftp://rwis:%s@165.206.203.34/METAR.txt"
                            "") % (props['rwis_ftp_password'],),
                           timeout=30).read()
    fp = open(fn, 'w')
    fp.write(data)
    fp.close()

    return fn


def main():
    """Go Main"""
    fn = fetch_files()
    utc = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    data = {}
    for line in open(fn):
        match = re.match("METAR K(?P<id>[A-Z1-9]{3})", line)
        if not match:
            continue
        gd = match.groupdict()
        data[gd['id']] = line

    fd, path = tempfile.mkstemp()
    os.write(fd, "\001\r\r\n")
    os.write(fd, ("SAUS00 KISU %s\r\r\n"
                  ) % (datetime.datetime.utcnow().strftime("%d%H%M"), ))
    os.write(fd, "METAR\r\r\n")
    for sid in data:
        os.write(fd, '%s=\r\r\n' % (data[sid].strip().replace("METAR ", ""), ))
    os.write(fd, "\003")
    os.close(fd)
    proc = subprocess.Popen(("/home/ldm/bin/pqinsert -i -p 'data c %s "
                             "LOCDSMMETAR.dat LOCDSMMETAR.dat txt' %s"
                             ) % (utc, path), shell=True,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    os.waitpid(proc.pid, 0)
    os.remove(path)


if __name__ == '__main__':
    main()
