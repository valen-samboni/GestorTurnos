# Sistema de Gestión de Turnos basado en Microservicios

## Descripción del proyecto

El presente proyecto implementa un sistema de gestión de turnos utilizando una arquitectura de microservicios, en la cual cada componente del sistema funciona de manera independiente y se comunica con los demás a través de protocolos de red.

El sistema permite el registro de usuarios, la asignación de turnos y generar notificaciones. Cada una de estas funcionalidades está desacoplada en servicios independientes, lo que facilita la escalabilidad, mantenibilidad y despliegue del sistema.

Se implementa una comunicación síncrona entre microservicios mediante el uso de HTTP, donde cada servicio realiza solicitudes a otros y espera una respuesta para continuar con su ejecución. Adicionalmente, se utiliza una base de datos relacional (PostgreSQL) para cada servicio siguiendo el principio de desacoplamiento y autonomía de datos, junto con volúmenes en Docker para evitar la pérdida de datos y también se implementó un API Gateway como punto único de entrada para centralizar las solicitudes del cliente.

El sistema está contenerizado mediante Docker y orquestado con Docker Compose, lo que permite su ejecución en diferentes entornos de manera consistente.

## Instrucciones para la ejecución

1. Clonar el repositorio:

    git clone: https://github.com/juanhr1/Sistema-de-turnos.git
    cd gestor-turnos-py

2. Crear el archivo de configuración `.env` en la raíz del proyecto:
    env
        DB_HOST=db
        DB_NAME=turnos_db
        DB_USER=admin
        DB_PASSWORD=admin

3. Construir y ejecutar los contenedores:

    docker-compose up --build


4. Verificar el funcionamiento de los servicios en:

* http://localhost:5000
* http://localhost:5001/users
* http://localhost:5002/turns
* http://localhost:5003/notifications

## Arquitectura del sistema

El proyecto está compuesto por los siguientes servicios:
### 1. API Gateway
Encargado de recibir solicitudes externas y redirigirlas al servicio correcto.
Puerto: 5000

### 2. Users Service
Gestiona la información de usuarios.
Funciones:
- Registrar usuarios.
- Consultar usuarios registrados.

Puerto: 5001

Crear usuario
* **POST /users**
  Permite registrar un nuevo usuario en el sistema.

json
    {
    "identificacion": "123",
    "telefono": "3001234567"
    }

Ver usuarios
* **GET /users**
  Retorna la lista de usuarios registrados.

### 3. Turns Service
Gestiona la lógica de turnos
Funciones:
- Validar usuario existente.
- Generar turnos consecutivos.
- Guardar turnos.
- Enviar notificaciones.

Puerto: 5002

crear turno
* **POST /turn**
  Permite crear un turno para un usuario existente. Este endpoint realiza una comunicación síncrona con el servicio de usuarios para validar la existencia del usuario antes de registrar el turno.

json
    {
    "identificacion": "123"
    }

Consultar turnos
* **GET /turns**
  Permite consultar los turnos almacenados en la base de datos.


### 4. Notifications Service
Gestiona el historial de notificaciones.
Funciones:
- Recibir eventos de nuevos turnos.
- Guardar mensajes.
- Consultar historial.

Puerto: 5003

crear natificación manual
* **POST /notify**
  Recibe solicitudes desde el servicio de turnos para simular el envío de notificaciones. Este servicio representa un comportamiento desacoplado dentro del sistema.

consultar natificación 
* **GET /notifications**

### 5. PostgreSQL
## Bases de datos por servicio

- users-service → users_db
- turns-service → turns_db
- notifications-service → notifications_db

Cada base contiene únicamente la información correspondiente a su dominio funcional.

## Base de datos
Se utiliza PostgreSQL con persistencia mediante volumen Docker.
- Conservación de datos.
- Estructura relacional.
- Integridad de información.
- Soporte SQL.

## Variables de entorno
Se utilizan variables de entorno para separar configuración del código.
- Host de base de datos
- Usuario
- Contraseña
- Nombre de base de datos

Esto mejora seguridad y portabilidad.

## Logs y Monitoreo
Cada servicio registra eventos en consola:
- Solicitudes recibidas.
- Usuarios creados.
- Turnos asignados.
- Notificaciones registradas.
- Errores internos.

Ver logs en tiempo real:
  docker-compose logs -f
Esto facilita el seguimiento de solicitudes, errores y pruebas de disponibilidad.

## Tolerancia básica a fallos

Se implementaron timeouts en las comunicaciones entre servicios para evitar bloqueos cuando un microservicio no responde o se encuentra caído.

## Tecnologías Utilizadas
- Python
- Flask
- PostgreSQL
- Docker
- Docker Compose
- Requests
- Psycopg2
- Postman

## Conceptos aplicados
- Microservicios
- Comunicación distribuida
- API Gateway
- Persistencia
- Contenedores
- Escalabilidad
- Portabilidad
- Logs

## Comando útiles
- Detener el sistema: docker-compose down
- Reconstruir sistema: docker-compose up --build
- Ver contenedores activos: docker ps
- Ver logs: docker-compose logs -f

## Conclusión

El sistema desarrollado evidencia la aplicación de conceptos fundamentales de sistemas distribuidos, tales como la separación de responsabilidades, comunicación entre servicios, persistencia de datos y despliegue en contenedores. Esta arquitectura permite la escalabilidad del sistema y facilita su mantenimiento y evolución.
