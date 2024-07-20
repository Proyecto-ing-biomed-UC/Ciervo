# Setup Raspberry pi 4

## OS 
Descargar la imagen de Raspberry Pi OS Lite desde la página oficial de Raspberry Pi (https://www.raspberrypi.com/software/). Selecionar las versión: Raspberry Pi OS Lite (64-bit). Esta versión no incluye la interfaz gráfica de usuario, lo que la hace más ligera y adecuada para servidores.

Configurar la red y habilitar SSH, para ello ir a opciones avanzadas y seleccionar la red y habilitar SSH. 

Setear el nombre del host como `ciervo` y el usuario como `ciervo`. Usar una contraseña segura.  




## Install Docker
Setup repositorio apt de docker
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

Instalar Docker
```bash
 sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Añadir el usuario al grupo `docker`
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

Probar la instalación
```bash
sudo docker run --rm hello-world
```

Si todo está bien, debería aparecer un mensaje de bienvenida de Docker: Hello from Docker!