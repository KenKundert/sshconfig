from svg_schematic import Schematic, Box, Wire, Label, midpoint, shift_y

with Schematic(filename='proxy2.svg', line_width=2):
    client = Box(w=5, h=2, name='SSH Client')
    proxy = Box(W=client.E, xoff=100, w=5, h=2, name='Remote Proxy', value='MMM.MMM.MMM.MMM:PPP')
    server = Box(W=proxy.E, xoff=100, w=5, h=2, name='SSH Server', value='localhost:22')
    Wire([client.E, proxy.W])
    Wire([proxy.E, server.W])
    Label(C=proxy.W, kind='arrow|', loc='W')
    Label(C=server.W, kind='arrow|', loc='W')
    fw = midpoint(client.E, proxy.W)
    FW = Wire([shift_y(fw, 50), shift_y(fw, -50)], stroke_dasharray="4 4")
    Label(C=FW.b, kind='none', loc='S', name='FW')
    Label(C=FW.b, yoff=20, kind='none', loc='S', name='blocks 22')
