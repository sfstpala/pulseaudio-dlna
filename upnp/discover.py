#!/usr/bin/python

# This file is part of pulseaudio-dlna.

# pulseaudio-dlna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pulseaudio-dlna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pulseaudio-dlna.  If not, see <http://www.gnu.org/licenses/>.

import socket as s
import renderer
import contextlib


class UpnpMediaRendererDiscover(object):

    SSDP_ADDRESS = '239.255.255.250'
    SSDP_PORT = 1900

    MSEARCH = 'M-SEARCH * HTTP/1.1\r\n' + \
              'HOST: {}:{}\r\n'.format(SSDP_ADDRESS, SSDP_PORT) + \
              'MAN: "ssdp:discover"\r\n' + \
              'MX: 2\r\n' + \
              'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n'

    def __init__(self, iface):
        self.iface = iface
        self.renderers = []

    def search(self, ttl=2, timeout=2):
        s.setdefaulttimeout(timeout)
        sock = s.socket(s.AF_INET, s.SOCK_DGRAM, s.IPPROTO_UDP)
        sock.setsockopt(s.IPPROTO_IP, s.IP_MULTICAST_TTL, ttl)
        sock.sendto(self.MSEARCH, (self.SSDP_ADDRESS, self.SSDP_PORT))

        buffer_size = 1024
        while True:
            try:
                header, address = sock.recvfrom(buffer_size)
                self._header_received(header, address)
            except s.timeout:
                break
        sock.close()

    def _header_received(self, header, address):
        upnp_device = renderer.UpnpMediaRendererFactory.from_header(
            header,
            renderer.CoinedUpnpMediaRenderer)
        if upnp_device not in self.renderers:
            self.renderers.append(upnp_device)
