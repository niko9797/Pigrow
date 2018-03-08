#!/usr/bin/python
import devices

sensor1 = devices.Sensor("pepe", 1, "DHT22", "usr/niko" )


print("#####################")


print("Nombre del sensor: " + sensor1.name)
print("Pin asignado: " + str(sensor1.pin))
print("Tipo del sensor: " + sensor1.sensorType)
print("Ruta del archivo: " + sensor1.path)
