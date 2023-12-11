import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial.tools.list_ports
from itertools import count
import sys, time, datetime, serial, csv

start = datetime.datetime.now()


x = []
list_of_pressuredata = []
list_of_temp_data = []
framelimit = 24*60*60*5 #gibt die Frameanzahl an. Entspricht mit dem intervall von 200 (5mal pro Sekunde) genau der oben angegebenen Minutenanzahl

#initialisation vom Graphen
fig, (ax1,ax2) = plt.subplots(2,1)
line1, = ax1.plot([], [], lw=2)
line2, = ax2.plot([], [], lw=2, color='r')
line = [line1, line2]
SerialInst = serial.Serial("COM4",9600) # Genau checken zu welchem COM man das Arduino verbunden hat

#funktion, die jedes Frame der Animation erzeugt. Falls es einen Fehler gibt bei der Datenergreifung gibt es null aus. Nach der Frameanzahl wird das Fenster neu angezeigt.
def animate(frame):


        error = False #error check um die Daten die nicht gemessen werden konnten nicht abzubilden
        if frame < 3 : #ist nur da, da ich gemerkt habe, dass der Code Probleme hat die Daten der ersten paar Iterationen zu lesn
                error = True
        print(frame)
        global list_of_temp_data
        global list_of_pressuredata
        global x
        global start

        if frame % 4 == 0:                      #nötiger Check, da der USB zu viele alte Werte im cache speichert, sodass der Code nur alte Werte entnimmt, die "gelaggt" erscheinen. 
                SerialInst.reset_input_buffer() #Heisst auch, dass jede 2sek eine halbe Sekunde nicht gemessen wird.
                error = False              

        packet = SerialInst.readline()
        readout = packet.decode("utf")


        #print(readout) <-- kann hilfreich sein um die naechsten zwei Zeilen zu verstehen
        if error == False:
                try:
                        pressuredata = readout.split("Temperature = ")[0].split("Water pressure = ")[1] #benutzt nur um die Werte herauszulesen, kommt stark auf den Serial Output des Arduinos an
                        temp_data = readout.split("Temperature = ")[1]
                        print("Pressure: %s" % (pressuredata) )
                        print("Temperature: %s" %(temp_data)) 
                        x.append(frame+1) 
                except Exception as e:
                                error = True
                                print(e)

        #code um den Wasserdruckwert zu plotten
        if error == False:
                try:
                        float(pressuredata)
                        list_of_pressuredata.append(float(pressuredata))  
                except Exception as e:
                        error = True
                        print(e)

        #code um den Temperaturwert zu plotten
        if error == False:
                try:
                        float(temp_data)
                        list_of_temp_data.append(float(temp_data))
                except Exception as e:
                        error = True
                        print(e)

        #check um nach der desginierten Zeit neuzustarten
        if frame == framelimit - 1:
                print("check")
                on_close("close_event")
                start = datetime.datetime.now()
                list_of_pressuredata = []
                list_of_temp_data = []
                x = []

        #loescht den vorherigen plot
        ax1.cla()
        ax2.cla()
        #plottet den neuen plot
        try:
                ax1.plot(x,list_of_temp_data)
                ax2.plot(x,list_of_pressuredata)
        except Exception as e: 
                print(e)
        #plottet die axenlabels
        ax1.set_ylabel("Temperatur in C")
        ax2.set_xlabel("t in Sekunden")
        ax2.set_ylabel("Druck in KPa")  



# Funktion, die beim Schliessen des Fensters oder bei einer bestimmsten Frameanzahl (eingespeichert ist jede 24h) die Daten an Excel speichert 
def on_close(event):
        # Specify the CSV file path
        now = datetime.datetime.now()
        
        def read_and_save_file(path, data_to_append):
                csv_file = path
                # Open the CSV file in append mode
                with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        # Append the data to the CSV file
                        for d in data_to_append:
                                writer.writerow([d])
                        writer.writerow([f"Zeit: Von {start.year},{start.hour}:{start.minute:02d} bis {now.year},{now.hour}:{now.minute} "  , str("  Max: " + str(max(data_to_append))), "  Average: " + str(sum(data_to_append)/len(data_to_append))])
                # Make sure to close the file when you're done
                file.close()

        read_and_save_file("arduino/data_pressuredata_waterpressure.csv",list_of_pressuredata)
        read_and_save_file("arduino/data_pressuredata_temperature.csv",list_of_temp_data)


fig.canvas.mpl_connect("close_event", on_close) #gibt an, was nach dem Schliessen des Graphen passieren soll
ani = FuncAnimation(fig,animate,interval = 200, frames = framelimit) #Die Rechnung hier ist: Interval * Frames / 1000 ist die Dauer der Animation in Sekunden
plt.show()