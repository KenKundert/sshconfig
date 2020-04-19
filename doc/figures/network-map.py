from svg_schematic import Schematic, Box, Wire, Label, shift_x, shift_y


with Schematic(filename='network-map.svg', line_width=2):
    # work network
    work = Box(w=6.5, h=4.5, stroke_dasharray="4 2")
    Label(C=work.SW, loc='ne', name='work')
    bastion = Box(S=work.S, yoff=-25, w=5.5, h=2, color='lightgray')
    Wire([bastion.E, shift_x(bastion.E, 75)])
    Label(C=bastion.SW, loc='ne', name='bastion')
    www = Box(NE=bastion.N, off=(-12.5, 25), w=2, h=1, color='white', name='www')
    # Wire([www.W, shift_x(www.W, -25)])
    mail = Box(NW=bastion.N, off=(12.5, 25), w=2, h=1, color='white', name='mail')
    # Wire([mail.E, shift_x(mail.E, 25)])
    dump = Box(SW=bastion.NW, yoff=-25, w=2.5, h=1, name='dump')
    # Wire([dump.N, shift_y(dump.N, -25)])
    laptop = Box(SE=bastion.NE, yoff=-25, w=2.5, h=1, name='my laptop', stroke_dasharray="2 2")
    # Wire([laptop.N, shift_y(laptop.N, -25)])
    # Wire([work.E, shift_x(work.E, 50)])

    # home network
    home = Box(N=work.S, yoff=50, w=6.5, h=2, stroke_dasharray="4 2")
    Label(C=home.SW, loc='ne', name='home')
    laptop = Box(SW=home.SW, off=(25, -25), w=2.5, h=1, color='lightgray', name='my laptop', stroke_dasharray="2 2")
    # Wire([laptop.N, shift_y(laptop.N, -25)])
    media = Box(SE=home.SE, off=(-25, -25), w=2.5, h=1, name='media')
    # Wire([media.N, shift_y(media.N, -25)])
    Wire([media.E, shift_x(media.E, 75)])

    # internet
    internet = Wire([shift_x(work.NE, 50), shift_x(home.SE, 50)], line_width=4)
    Label(C=internet.e, loc='s', name='internet')

    # external network
    github = Box(NW=internet.b, off=(50, 25), w=3, h=1, name='github')
    Wire([github.W, shift_x(github.W, -50)])
    cloud = Box(N=github.S, yoff=25, w=3, h=1, name='vps')
    Wire([cloud.W, shift_x(cloud.W, -50)])
    backups = Box(N=cloud.S, yoff=25, w=3, h=1, name='backups')
    Wire([backups.W, shift_x(backups.W, -50)])
    hotspot = Box(N=backups.S, yoff=25, w=3, h=2, stroke_dasharray="4 2")
    # Wire([hotspot.W, shift_x(hotspot.W, -50)])
    Label(C=hotspot.SW, loc='ne', name='a wifi hotspot')
    laptop = Box(C=hotspot.C, w=2, h=1, name='my laptop', stroke_dasharray="2 2")
    # Wire([laptop.N, shift_y(laptop.N, -25)])
