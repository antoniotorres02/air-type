## Tareas a implementar

1. **Posicionamiento de la ventana:**  
   Si la ventana está muy arriba de la pantalla, en vez de salir por encima del ratón, debería salir por debajo del ratón.

2. **Cierre de la ventana al parar la grabación:**  
   Al detener la grabación (ejecutando nuevamente `python main.py --transcript`), la ventanita también debe cerrarse, ya que actualmente permanece abierta.

3. **Extensión de la interfaz de configuración:**  
   En la interfaz de configuración inicial (basada en PyQt), se debe comenzar a implementar soporte para otros proveedores de transcripción de audio. Actualmente, solo está implementado Groq.

4. **Pruebas en Windows:**  
   Realizar pruebas del adaptador, enfocándose principalmente en el entorno Windows.

5. **Empaquetado y ejecución en distintos entornos:**  
   Se debe tener en cuenta cómo se va a empaquetar la aplicación y cómo se va a ejecutar en los distintos entornos.