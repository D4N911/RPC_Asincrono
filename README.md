# Sistema RPC Asíncrono para Gestión de Productos

Sistema RPC asíncrono que permite operaciones concurrentes de inserción y consulta sobre productos almacenados en un archivo XML. El sistema implementa un mecanismo de prioridades donde las operaciones de inserción tienen mayor precedencia que las de consulta.

## Características

- **Operaciones concurrentes**: Múltiples clientes pueden conectarse simultáneamente
- **Sistema de prioridades**: Las inserciones se procesan antes que las consultas
- **Persistencia XML**: Los productos se almacenan en un archivo XML único
- **Operaciones aleatorias**: Los clientes realizan operaciones generadas aleatoriamente
- **Simulación de carga**: Las inserciones tienen una espera de 3 segundos

## Requisitos

- Python 3.7 o superior
- Módulos estándar de Python (socket, threading, xml.etree.ElementTree, json, queue)

## Uso

### Iniciar el servidor

```bash
python3 servidor.py
```

### Ejecutar un cliente

```bash
python3 cliente.py CLIENT-1 10
```

### Ejecutar múltiples clientes concurrentes

```bash
# Terminal 1
python3 cliente.py CLIENT-1 10

# Terminal 2
python3 cliente.py CLIENT-2 10

# Terminal 3
python3 cliente.py CLIENT-3 10
```

## Estructura del Proyecto

- `servidor.py` - Servidor RPC asíncrono con sistema de prioridades
- `cliente.py` - Cliente RPC con operaciones aleatorias
- `productos.xml` - Archivo XML de productos
- `DOCUMENTACION.md` - Documentación técnica completa con diagramas
- `test_concurrente.py` - Script de prueba automatizada
- `demo.py` - Script de demostración
- `ver_xml.py` - Visualizador del contenido XML

## Documentación

Ver `DOCUMENTACION.md` para la documentación técnica completa, incluyendo:
- Diagrama de arquitectura basada en componentes
- Diagramas de flujo del servidor y cliente
- Grafo de precedencia
- Detalles de implementación
