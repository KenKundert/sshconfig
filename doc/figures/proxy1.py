from svg_schematic import Schematic, Box, Wire, Label, midpoint, shift_y

with Schematic(filename='proxy1.svg', line_width=2, background='none'):
    client = Box(w=5, h=2, name='SSH Client')
    server = Box(W=client.E, xoff=150, w=5, h=2, name='SSH Server', value='NNN.NNN.NNN.NNN:PPP')
    Wire([client.E, server.W])
    Label(C=server.W, kind='arrow|', loc='W')
    fw = midpoint(client.E, server.W)
    FW = Wire([shift_y(fw, 100), shift_y(fw, -100)], stroke_dasharray="4 4")
    Label(C=FW.b, kind='none', loc='S', name='firewall')
    Label(C=FW.b, yoff=20, kind='none', loc='S', name='blocks port 22')
