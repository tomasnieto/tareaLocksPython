import threading
from random import choice, randint
from datetime import datetime
from time import sleep

threadlock = threading.Lock()


archivos = ["BarcoPirata", "CasaTerror",
            "MontañaRusa", "Salida", "TiroBlanco", "ZonaComun"]

# dejar los .txt en blanco para la ejecucion (sino es manual)
for archivo in archivos:
    escribir = open(f"{archivo}.txt", "w")
    escribir.close()


def escribir(nombre, id, fila, ingreso):
    if nombre == "montana rusa":
        nombre_archivo = "MontañaRusa.txt"
    elif nombre == "casita del terror":
        nombre_archivo = "CasaTerror.txt"
    elif nombre == "barco pirata":
        nombre_archivo = "BarcoPirata.txt"
    elif nombre == "tiro al blanco":
        nombre_archivo = "TiroBlanco.txt"
    else:
        return

    archivo = open(nombre_archivo, 'a+')
    archivo.write(f"Persona{id}, {fila}, {ingreso}\n")
    archivo.close()

    return


class Personas (threading.Thread):  # los objetos son las hebras?
    def __init__(self, Atraccion, id):
        super(Personas, self).__init__()
        self.hora_llegada = datetime.now().time()
        self.atraccion_deseada = Atraccion
        self.hora_ingreso_fila = 0
        self.hora_ingreso_juego = 0
        self.hora_salida = 0
        self.id = id

    def run(self):
        while True:
            threadlock.acquire()
            if len(self.atraccion_deseada.fila_actual) < self.atraccion_deseada.cap_fila:
                self.hora_ingreso_fila = datetime.now().time()

                archivo = open('ZonaComun.txt', 'a+')
                archivo.write(
                    f"Persona{self.id}, {self.hora_llegada}, {self.atraccion_deseada}, {self.hora_ingreso_fila}\n")
                archivo.close()

                zona_comun[zona_comun.index(self)] = 0
                threadlock.release()

                self.atraccion_deseada.fila_actual.append(self)
                self.hora_ingreso_juego = datetime.now().time()

                escribir(self.atraccion_deseada.nombre, self.id,
                         self.hora_ingreso_fila, self.hora_ingreso_juego)

                archivo = open('Salida.txt', 'a+')

                while True:
                    threadlock.acquire()
                    if self.atraccion_deseada.en_juego == 0 and self.atraccion_deseada.detencion_emergencia == 0:
                        threadlock.release()
                        continue
                    else:
                        threadlock.release()
                        break

                sleep(self.atraccion_deseada.duracion)
                self.hora_salida = datetime.now().time()
                archivo.write(f"Persona{self.id}, {self.hora_salida}\n")
                archivo.close()

                break
            else:
                threadlock.release()
                continue


class Atraccion(threading.Thread):
    def __init__(self, cap_fila, duracion, cap_juego, nombre):
        super(Atraccion, self).__init__()
        self.nombre = nombre
        self.cap_fila = cap_fila
        self.duracion = duracion
        self.cap_juego = cap_juego
        self.fila_actual = []
        self.en_juego = 0
        self.detencion_emergencia = 0

    def __str__(self):
        return f"{self.nombre}"

    def run(self):
        while True:
            if len(self.fila_actual) >= self.cap_juego:  # hay gente suficiente
                self.en_juego = 1

                # vaciar fila la cantidad que entra al juego
                for i in range(0, self.cap_juego):
                    self.fila_actual.pop(0)

                sleep(self.duracion)
                self.en_juego = 0

            elif all(v == 0 for v in zona_comun):
                self.detencion_emergencia = 1
                break


#                   cap_fila duracion cap_juego
roller_coster = Atraccion(10, 5, 10, "montana rusa")
casa_terror = Atraccion(8, 3, 2, "casita del terror")
barco_pirata = Atraccion(15, 7, 5, "barco pirata")
tiro_blanco = Atraccion(5, 2, 1, "tiro al blanco")

juegos = [roller_coster, casa_terror, barco_pirata, tiro_blanco]

zona_comun = []
for i in range(0, 150):

    zona_comun.append(Personas(choice(juegos), i+1))

for juego in juegos:
    juego.start()
for i in range(0, 150):
    zona_comun[i].start()
