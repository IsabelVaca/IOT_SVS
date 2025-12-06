Este proyecto consiste en el desarrollo de un sistema de monitoreo inteligente para licuadoras, basado en sensores, cuyo objetivo es detectar a tiempo el desgaste de las aspas, el desbalanceo o el sobreesfuerzo del motor. A través de un dispositivo IoT —integrado por un microcontrolador y sensores de temperatura, corriente y vibración— se recopilan datos en tiempo real sobre el comportamiento del equipo.

La información se procesa y se envía a una interfaz interactiva donde el usuario puede visualizar el estado de la licuadora, recibir alertas tempranas de fallas.

El proyecto está dirigido tanto a usuarios domésticos como a cocineros de restaurantes o cafeterías, ofreciendo una herramienta intuitiva, accesible y universal que permite tomar decisiones informadas sobre el uso seguro y eficiente de la licuadora para aumentar la productividad.

Para correr el proyecto se debe conectar el esp32 por medio de arduino, se debe correr el código del servidor flask en terminal, a su vez correr el código de sql y tener mysql corriendo, finalmente se debe correr el código del dashboard en terminal por medio de streamlit. "streamlit run dashboard.py" los archivos: Dashboard.py, 1.svg, 2.svg, 3.svg, logo.png deben de estar en la misma carpeta. 
