from svg_schematic import Schematic, Box, Wire, Label, midpoint, shift_y

with Schematic(filename='proxy3.svg', line_width=2):
    client = Box(w=5, h=2, name='SSH Client')
    lproxy = Box(W=client.E, xoff=100, w=5, h=2, name='Local Proxy', value='localhost:PPPP')
    rproxy = Box(W=lproxy.E, xoff=100, w=5, h=2, name='Remote Proxy', value='MMM.MMM.MMM.MMM:PPP')
    server = Box(W=rproxy.E, xoff=100, w=5, h=2, name='SSH Server', value='localhost:22')
    Wire([client.E, lproxy.W])
    Wire([lproxy.E, rproxy.W])
    Wire([rproxy.E, server.W])
    Label(C=lproxy.W, kind='arrow|', loc='W')
    Label(C=rproxy.W, kind='arrow|', loc='W')
    Label(C=server.W, kind='arrow|', loc='W')
    fw = midpoint(lproxy.E, rproxy.W)
    FW = Wire([shift_y(fw, 50), shift_y(fw, -50)], stroke_dasharray="4 4")
    Label(C=FW.b, kind='none', loc='S', name='FW')
    Label(C=FW.b, yoff=20, kind='none', loc='S', name='blocks 22')
