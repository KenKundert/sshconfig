from svg_schematic import Schematic, Box, Wire, Label, midpoint, shift_y

with Schematic(filename='proxy3.svg', line_width=2, background='none'):
    client = Box(w=5, h=2, name='SSH Client')
    lproxy = Box(W=client.E, xoff=50, w=5, h=2, name='Pass Through Proxy', value='MMM.MMM.MMM.MMM:LPP')
    rproxy = Box(W=lproxy.E, xoff=150, w=5, h=2, name='Remote Proxy', value='NNN.NNN.NNN.NNN:RPP')
    server = Box(W=rproxy.E, xoff=50, w=5, h=2, name='SSH Server', value='localhost:22')
    Box(W=rproxy.W, xoff=-50, w=12.5, h=3, stroke_dasharray="4 4")
    Wire([client.E, lproxy.W])
    Wire([shift_y(client.E, -12), shift_y(lproxy.W, -12)], stroke_dasharray="4 8")
    Wire([shift_y(client.E, 12), shift_y(lproxy.W, 12)], stroke_dasharray="4 8")
    Wire([lproxy.E, rproxy.W])
    Wire([shift_y(lproxy.E, -12), shift_y(rproxy.W, -12)], stroke_dasharray="4 8")
    tunnel = Wire([shift_y(lproxy.E, 12), shift_y(rproxy.W, 12)], stroke_dasharray="4 8")
    Label(C=tunnel.m, kind='none', loc='S', name='TLS tunnel')
    Wire([rproxy.E, server.W])
    Label(C=rproxy.W, kind='arrow|', loc='W')
    Label(C=server.W, kind='arrow|', loc='W')
    fw_n = Wire([lproxy.N, shift_y(lproxy.N, -50)], stroke_dasharray="4 4")
    fw_s = Wire([lproxy.S, shift_y(lproxy.S, 50)], stroke_dasharray="4 4")
    Label(C=fw_s.e, kind='none', loc='S', name='firewall')
    Label(C=fw_s.e, yoff=20, kind='none', loc='S', name='blocks all ports')
