# LexiVerse

### Descripción

Juego para aprender palabras en distintos idiomas (Actualmente: Español, Francés e Inglés).

El desarrollo de esta aplicación sirve para aprender conocimientos sobre Computación Ubicua. La aplicación hace uso de reconocimiento facial, reconocimineto de voz y realidad aumentada. 

El mazo para jugar es: (Pendiente)

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

