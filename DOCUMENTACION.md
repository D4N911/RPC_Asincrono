# Documentación Técnica del Sistema RPC Asíncrono

## 1. Diagrama de Arquitectura Basada en Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA RPC ASÍNCRONO                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────┐                          ┌───────────────┐
│   COMPONENTE  │                          │   COMPONENTE  │
│    CLIENTE    │                          │    SERVIDOR   │
└───────────────┘                          └───────────────┘
        │                                           │
        │                                           │
        │ Socket TCP                                │ Socket TCP
        │ JSON                                      │ JSON
        │                                           │
        └──────────────────┬───────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │     COMPONENTE DE COMUNICACIÓN       │
        │         (Socket TCP/JSON)            │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │   COMPONENTE DE GESTIÓN DE COLAS     │
        │    (Priority Queue - Prioridades)   │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │   COMPONENTE DE PROCESAMIENTO        │
        │    (Worker Threads Pool)            │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │   COMPONENTE DE GESTIÓN DE DATOS     │
        │      (ProductManager + XML)         │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │   COMPONENTE DE PERSISTENCIA         │
        │         (productos.xml)             │
        └──────────────────────────────────────┘
```

### Descripción de Componentes

#### 1. Componente Cliente
- **Responsabilidad**: Generar y enviar solicitudes RPC
- **Características**:
  - Genera operaciones aleatorias (inserción/consulta)
  - Establece conexión TCP con el servidor
  - Serializa solicitudes en JSON
  - Recibe y procesa respuestas

#### 2. Componente Servidor
- **Responsabilidad**: Recibir y procesar solicitudes RPC
- **Características**:
  - Escucha conexiones TCP
  - Acepta múltiples clientes concurrentes
  - Deserializa solicitudes JSON
  - Enruta solicitudes a la cola de prioridades

#### 3. Componente de Comunicación
- **Responsabilidad**: Manejar la comunicación de red
- **Protocolo**: TCP/IP con mensajes JSON
- **Formato de mensaje**:
  ```json
  {
    "operation": "insert|query",
    "params": {...},
    "client_id": "CLIENT-1"
  }
  ```

#### 4. Componente de Gestión de Colas
- **Responsabilidad**: Ordenar solicitudes por prioridad
- **Implementación**: `queue.PriorityQueue`
- **Prioridades**:
  - Prioridad 1: Inserciones (mayor prioridad)
  - Prioridad 2: Consultas (menor prioridad)

#### 5. Componente de Procesamiento
- **Responsabilidad**: Procesar solicitudes de forma concurrente
- **Implementación**: Pool de threads worker
- **Características**:
  - Múltiples threads procesan solicitudes en paralelo
  - Respeta el orden de prioridades de la cola

#### 6. Componente de Gestión de Datos
- **Responsabilidad**: Operaciones CRUD sobre productos
- **Implementación**: `ProductManager`
- **Operaciones**:
  - `insert_product()`: Inserta producto con delay de 3s
  - `query_product()`: Consulta producto por ID

#### 7. Componente de Persistencia
- **Responsabilidad**: Almacenamiento persistente
- **Formato**: XML
- **Estructura**: Archivo único `productos.xml`

---

## 2. Diagrama de Flujo del Servidor

```
                    [INICIO]
                       │
                       ▼
            ┌──────────────────────┐
            │  Iniciar Servidor    │
            │  (Socket, Workers)   │
            └──────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Escuchar Conexiones │
            │    (server.listen)   │
            └──────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ ¿Nueva Conexión?     │
            └──────────────────────┘
                       │
            ┌──────────┴──────────┐
            │ NO                  │ SÍ
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │ Crear Thread Cliente │
            │          └──────────────────────┘
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │ Recibir Solicitud    │
            │          │ (JSON)               │
            │          └──────────────────────┘
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │ Determinar Prioridad │
            │          │ Insert=1, Query=2    │
            │          └──────────────────────┘
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │ Agregar a Cola       │
            │          │ (Priority Queue)     │
            │          └──────────────────────┘
            │                     │
            └─────────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │   WORKER THREAD (Pool)        │
        └───────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ ¿Solicitud en Cola?   │
            └──────────────────────┘
                       │
            ┌──────────┴──────────┐
            │ NO                  │ SÍ
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │ Obtener Solicitud    │
            │          │ (Mayor Prioridad)    │
            │          └──────────────────────┘
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │ ¿Tipo Operación?     │
            │          └──────────────────────┘
            │                     │
            │      ┌───────────────┴───────────────┐
            │      │                               │
            │      ▼                               ▼
            │ ┌──────────────┐          ┌──────────────┐
            │ │   INSERT     │          │    QUERY     │
            │ └──────────────┘          └──────────────┘
            │      │                         │
            │      ▼                         ▼
            │ ┌──────────────┐          ┌──────────────┐
            │ │ Lock XML     │          │ Lock XML     │
            │ └──────────────┘          └──────────────┘
            │      │                         │
            │      ▼                         ▼
            │ ┌──────────────┐          ┌──────────────┐
            │ │ Delay 3 seg  │          │ Buscar ID    │
            │ └──────────────┘          └──────────────┘
            │      │                         │
            │      ▼                         ▼
            │ ┌──────────────┐          ┌──────────────┐
            │ │ Insertar     │          │ Obtener      │
            │ │ Producto     │          │ Posición     │
            │ └──────────────┘          └──────────────┘
            │      │                         │
            │      └───────────┬─────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Generar Respuesta    │
            │          │ {status, position}  │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Enviar Respuesta     │
            │          │ al Cliente           │
            │          └──────────────────────┘
            │                  │
            └──────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ ¿Servidor Activo?    │
            └──────────────────────┘
                       │
            ┌──────────┴──────────┐
            │ SÍ                  │ NO
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │   Cerrar Servidor    │
            │          │      [FIN]           │
            │          └──────────────────────┘
            │
            └─────────────────────┘
```

### Puntos Clave del Flujo del Servidor

1. **Aceptación de Conexiones**: El servidor acepta múltiples conexiones concurrentes
2. **Clasificación por Prioridad**: Cada solicitud se clasifica y agrega a la cola con su prioridad
3. **Procesamiento Asíncrono**: Los workers procesan solicitudes de la cola respetando prioridades
4. **Sincronización**: El acceso al XML está protegido con locks
5. **Delay en Inserciones**: Las inserciones tienen un delay de 3 segundos

---

## 3. Diagrama de Flujo del Cliente

```
                    [INICIO]
                       │
                       ▼
            ┌──────────────────────┐
            │  Inicializar Cliente │
            │  (ID, Host, Port)    │
            └──────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Generar Operaciones │
            │    Aleatorias (N)    │
            └──────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ ¿Operaciones         │
            │ Pendientes?          │
            └──────────────────────┘
                       │
            ┌──────────┴──────────┐
            │ NO                  │ SÍ
            │                     │
            │                     ▼
            │          ┌──────────────────────┐
            │          │ Decidir Operación    │
            │          │ (Aleatorio)          │
            │          └──────────────────────┘
            │                     │
            │      ┌───────────────┴───────────────┐
            │      │                               │
            │      ▼                               ▼
            │ ┌──────────────┐          ┌──────────────┐
            │ │   INSERT     │          │    QUERY     │
            │ │ (60% prob)   │          │ (40% prob)   │
            │ └──────────────┘          └──────────────┘
            │      │                         │
            │      ▼                         ▼
            │ ┌──────────────┐          ┌──────────────┐
            │ │ Generar ID   │          │ Seleccionar  │
            │ │ Nombre       │          │ ID (propio   │
            │ │ Precio       │          │ o aleatorio) │
            │ └──────────────┘          └──────────────┘
            │      │                         │
            │      └───────────┬─────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Conectar al Servidor │
            │          │ (Socket TCP)         │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Serializar Solicitud │
            │          │ (JSON)               │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Enviar Solicitud     │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Esperar Respuesta    │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Recibir Respuesta    │
            │          │ (JSON)               │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Deserializar        │
            │          │ Respuesta           │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Mostrar Resultado    │
            │          │ (Posición o -1)      │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Cerrar Conexión      │
            │          └──────────────────────┘
            │                  │
            │                  ▼
            │          ┌──────────────────────┐
            │          │ Espera Aleatoria     │
            │          │ (0.5-2 segundos)     │
            │          └──────────────────────┘
            │                  │
            └──────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   [FIN]              │
            └──────────────────────┘
```

### Puntos Clave del Flujo del Cliente

1. **Operaciones Aleatorias**: El cliente genera operaciones de forma aleatoria
2. **Distribución**: 60% inserciones, 40% consultas
3. **Conexión por Operación**: Cada operación abre una nueva conexión
4. **Espera entre Operaciones**: Delay aleatorio de 0.5-2 segundos
5. **Trazabilidad**: El cliente mantiene lista de productos insertados

---

## 4. Grafo de Precedencia del Sistema

```
                    [INICIO]
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   [Cliente 1]   [Cliente 2]   [Cliente N]
        │              │              │
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   Servidor Socket    │
            │   (Acepta Conexiones)│
            └──────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Thread por Cliente  │
            │  (Manejo Conexión)   │
            └──────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Cola de Prioridades │
            │  ┌───────────────┐   │
            │  │ Insert (P=1)  │   │
            │  │ Insert (P=1)  │   │
            │  │ Query (P=2)   │   │
            │  │ Query (P=2)   │   │
            │  └───────────────┘   │
            └──────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   [Worker 1]    [Worker 2]    [Worker 3]
        │              │              │
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  ProductManager    │
            │  (Lock XML)        │
            └──────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   productos.xml     │
            └──────────────────────┘
```

### Dependencias de Precedencia

1. **Cliente → Servidor**: Los clientes deben conectarse antes de enviar solicitudes
2. **Servidor → Cola**: Las solicitudes deben clasificarse antes de procesarse
3. **Cola → Workers**: Los workers procesan en orden de prioridad
4. **Workers → ProductManager**: Solo un worker accede al XML a la vez (lock)
5. **ProductManager → XML**: El XML se actualiza después de cada operación

---

## 5. Detalles de Implementación

### 5.1. Sistema de Prioridades

El sistema utiliza `queue.PriorityQueue` de Python, donde:
- Menor número = Mayor prioridad
- Inserciones: Prioridad 1
- Consultas: Prioridad 2

### 5.2. Manejo de Concurrencia

- **Locks Reentrantes**: `threading.RLock()` permite acceso exclusivo al XML
- **Thread Pool**: Múltiples workers procesan solicitudes en paralelo
- **Conexiones Concurrentes**: Cada cliente tiene su propio thread de manejo

### 5.3. Formato de Mensajes

**Solicitud:**
```json
{
  "operation": "insert",
  "params": {
    "id": "PROD-001",
    "nombre": "Laptop",
    "precio": 999.99
  },
  "client_id": "CLIENT-1"
}
```

**Respuesta:**
```json
{
  "status": "success",
  "position": 0
}
```

### 5.4. Estructura XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<productos>
    <producto id="PROD-001" nombre="Laptop" precio="999.99"/>
    <producto id="PROD-002" nombre="Mouse" precio="25.50"/>
</productos>
```

---

## 6. Consideraciones de Diseño

### 6.1. Escalabilidad

- El sistema puede manejar múltiples clientes simultáneos
- El número de workers es configurable
- La cola de prioridades maneja automáticamente el ordenamiento

### 6.2. Seguridad

- El acceso al XML está protegido con locks
- Cada operación es atómica (lock durante toda la operación)
- No hay condiciones de carrera en el acceso al archivo

### 6.3. Rendimiento

- Las inserciones tienen delay de 3s para simular carga
- Las consultas son rápidas (solo lectura)
- El sistema de prioridades asegura que las inserciones se procesen primero

---

## 7. Pruebas y Evidencias

Para demostrar el funcionamiento concurrente:

1. Inicie el servidor: `python3 servidor.py`
2. Inicie múltiples clientes en terminales separadas
3. Observe las impresiones que muestran:
   - Orden de recepción de solicitudes
   - Orden de procesamiento (inserciones primero)
   - Posiciones devueltas

Las impresiones del servidor mostrarán claramente cómo el sistema respeta las prioridades y maneja la concurrencia.

