# LexiVerse

### Descripción

Juego para aprender palabras en distintos idiomas (Actualmente: Español, Francés e Inglés).

El desarrollo de esta aplicación sirve para aprender conocimientos sobre Computación Ubicua. La aplicación hace uso de reconocimiento facial, reconocimineto de voz y realidad aumentada. 

El mazo para jugar es: https://github.com/danieeeld2/LexiVerse/tree/main/cartas

- Cuenta con un **modo de aprendizaje** donde, al enfocar una carta, la identifica y te indica cómo se escribe por interfaz gráfica. *Para hacer uso de la realidad aumentada, escribe el texto en el medio de la carta*.

- Cuenta con un **modo de juego**, donde la aplicación lanza al usuario una palabra y este debe buscar la carta correcta para obtener puntos.

### Uso

La aplicación funciona íntegramente por voz. Los comandos de voz son los siguientes:

- `Modo Aprender` : *Solo se puede usar si **NO** hay un modo previamente iniciado*. Permite acceder al modo de aprendizaje.
  
- `Modo Jugar` : *Solo se puede usar si **NO** hay un modo previamente iniciado*. Permite acceder al modo de jugar.

- `Modo Cambiar Idioma` : *Solo se puede usar si **NO** hay un modo previamente iniciado*. Permite cambiar el idioma del juego. Solo cambia el idioma de las palabras del mazo, proximamente se incluirá el cambio de idioma de los diálogos. Los idiomas válidos son Español, Francés e Inglés.
  
- `Modo Salir` : *Solo se puede usar si **SÍ** hay un modo previamente iniciado*. Permite salir de uno de los modos anteriores.

- `Modo Cerrar Sesión` : *Solo se puede usar si **SÍ** hay un usuario iniciado*. Permite cerrar sesión para que se identifique  otra persona mediante reconocimiento facial.

El flujo de la aplicaión es el siguiente: 

Al activarse la cámara, busca caras en el frame para iniciar sesión mediante reconocimiento facial. Si la cara que reconoce coincide con algunas de las almacenadas en la BD, entonces carga tu perfil. En caso contrario, comienza el registro de usuario y escaneado de la cara para crear el nuevo perfil de usuario.

Una vez iniciado sesión, puedes elergir entre `Modo Aprender`, `Modo Jugar` y `Modo Cambiar Idioma`. Para salir de los modos, usa `Modo Salir`. En cualquier momento puedes cerrar la sesión con `Modo Cerrar Sesión` para comenzar de nuevo este flujo de aplicación.

### Decisiones

Las cartas cuentan con 4 marcadores (uno en cada esquina). Una carta se identifica en el frame si aparecen 3 o 4 de los marcadores que la definen. Esto se debe a la posibilidad de que, al tomar una carta con la mano, exista una ocultación parcial de uno de los marcadores.

Por otro lado, se utilizan dos hebras paralelas al programa:

- La primera es para es para que la aplicación lea texto. Utiliza una cola para que el `main` pueda indicar que texto leer. Además, usa un evento para que, mientras no termine de leer (el evento de hablar está activo) siga mostrando frames y no se quede congelada la cámara.
- La segunda hebra es para reconocer la voz. También hace uso de un evento para saber cuando escuchar y cuando no. Escucha en intervalos de 4 segundos antes de procesar y añade el texto reconocido a una cola para llevarlo al main. Previamente, hay un filtrado de palabras claves para saber si el texto que está reconociendo es válido para la lógica de la aplicación. Por otro lado, ya en el main y dependiendo del bloque (o situación) que se esté procesando, ya se acab de validar para saber si el usuario tiene que reintentar la indicación de la orden o la indicada es válida y se puede procesar.

En cuanto a los paquetes usados, no se ha utilizado nada de gran complejidad y que no se haya visto en clase. Se hace uso de `opencv` para la realidad aumentada y el reconocimiento de Aruzo. Para la realidad aumentada (en el `modo aprender`) se dibuja el nombre de la carta en el idioma seleccionado en el medio de la misma. Para ello, simplemente calcula el centro usando la posición relativa de los marcadores.

Por otro lado, usa `speech_recognition` con la IA de Google para el procesado de las ordenes por voz. Utilizo esta porque es la que mejor reconoce los nombres de personas (para poder hacer el registro por voz).

Finalmente, hace uso de `face_recognition` para hacer la gestión de LogIn. Las codificaciones se guardan en una carpeta donde se almacenan ficheros de matrices de `numpy` con nombre del fichero el nombre del usuario. Los perfiles de usuario se gestionan en un `json` y permite simular de forma sencilla una BD (aunque es menos escalable. Esta aplicación se trata de un prototipo para la asignatura, pro lo que no va a contar con un número creciente de usuarios, pero debería tenerse en cuenta la mejora de usar una BD en el futuro).

### Ideas descartadas

En la propuesta inicial, añadí un par de ideas extras, como bonificaciones al decir una carta por voz, pero esto aumentaba la carga computacional, por lo que la lectura de frames iba menos fluida. Decidí que era mejor priorizar una esperiencia fluida que meter complejidad por incluir más código. Por otro lado, también indiqué que el programa leería las palabras en alto, pero las voces que tengo instaladas en el sistema no ofrecen una experiencia fluida, por lo que decidí descartarlo.

Finalmente, el modo contrareloj ha sido eliminado y los puntos otorgados al eliminar una carta se deciden por una bonificación aleatoria, tiempo que tarda en encontrar la carta y la frecuencia de acierto de las cartas.
