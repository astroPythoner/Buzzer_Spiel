import pygine
from serial.tools import list_ports

def get(allow_Dummy=False):
    menu = pygine.Menu_creator("ports")
    menu.add_space("Verbinde den Arduino mit dem PC und starte das Programm neu",title_size=18)
    ports = [pygine.Menu_creator.get_value(port.name,port) for port in list_ports.comports()]
    ports.append(pygine.Menu_creator.get_value("Tastatur (← →)","DUMMY"))
    menu.add_vertical_selection("Anschluss auswählen",ports,1,1,[0],(255, 255, 255),35,(255, 255, 255),20,(150, 200, 175),20)
    return menu

