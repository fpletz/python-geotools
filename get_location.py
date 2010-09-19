#!/usr/bin/python2.7

import geotools as geo

def main():
    wifis = geo.get_wifis()
    loc = geo.get_location(wifis)
    geo.print_location(loc)
    
if __name__ == '__main__':
    main()
