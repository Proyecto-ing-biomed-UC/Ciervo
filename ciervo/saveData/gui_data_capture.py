import tkinter as tk
from tkinter import messagebox
import time
import threading
import csv
import subprocess
import os

class DataCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Captura de Datos")
        self.recording = False
        self.start_time = None

        self.label = tk.Label(root, text="Duración de grabación: 0 segundos")
        self.label.pack(pady=20)

        self.start_button = tk.Button(root, text="Iniciar Grabación", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Detener Grabación", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Guardar en CSV", command=self.save_to_csv, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        self.data = []

    def start_recording(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)

        threading.Thread(target=self.run_docker_compose_up).start()

    def stop_recording(self):
        self.recording = False
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)

        self.run_docker_compose_down()


    def update_time(self):
        if self.recording:
            elapsed_time = int(time.time() - self.start_time)
            self.label.config(text=f"Duración de grabación: {elapsed_time} segundos")
            self.root.after(1000, self.update_time)

    def save_to_csv(self):
        file_path_program_save = os.path.join(os.path.dirname(__file__), "saveDataInCSVFormat.py")
        
        subprocess.run(["python3", file_path_program_save])

        if not self.data:
            messagebox.showwarning("Advertencia", "No hay datos para guardar.")
            return

        file_path = "datos_capturados.csv"
        with open(file_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["timestamp", "value"])
            writer.writeheader()
            writer.writerows(self.data)

        messagebox.showinfo("Guardado", f"Datos guardados en {file_path}")

    def run_docker_compose_up(self):
        try:
            subprocess.run(["docker", "compose", "up", "--build"], check=True)
            self.start_recording_after_containers_start()  # Iniciar la grabación solo cuando los contenedores estén listos
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error al iniciar Docker: {e}")

    def start_recording_after_containers_start(self):
        # Verificar que los contenedores estén en ejecución
        while True:
            result = subprocess.run(["docker", "compose", "ps", "--services", "--filter", "status=running"], stdout=subprocess.PIPE, text=True)
            running_services = result.stdout.splitlines()

            if "nanomq" in running_services and "stream" in running_services and "influxdb" in running_services:
                self.recording = True
                self.start_time = time.time()
                self.update_time()
                

            time.sleep(1)  # Esperar 1 segundo antes de volver a comprobar

    def run_docker_compose_down(self):
        try:
            subprocess.run(["docker", "compose", "down"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error al detener Docker: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCaptureApp(root)
    root.mainloop()
