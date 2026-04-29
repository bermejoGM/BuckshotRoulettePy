# BuckshotRoulettePy

Documentación del proyecto **BuckshotRoulettePy**.

## Descripción

BuckshotRoulettePy es una implementación en Python inspirada en el juego *Buckshot Roulette*, con soporte para partidas locales y un sistema de puntuaciones persistente mediante servidor.

El proyecto está pensado para ejecutarse en local y permite:

* Ejecutar el juego desde terminal.
* Gestionar dependencias mediante `requirements.txt`.
* Conectarse a un servidor de puntuaciones.
* Registrar y consultar puntuaciones de jugadores.

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd BuckshotRoulettePy
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
```

Activar entorno virtual:

* **Windows**

```bash
venv\Scripts\activate
```

* **Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

Las dependencias del proyecto están definidas en `requirements.txt`.

```bash
pip install -r requirements.txt
```

---

## Dependencias

Todas las dependencias necesarias están listadas en el archivo `requirements.txt`.

Para instalarlas:

```bash
pip install -r requirements.txt
```

Estas dependencias incluyen las librerías necesarias para:

* Ejecución del juego
* Comunicación cliente/servidor
* Persistencia de puntuaciones
* Utilidades auxiliares

---

## Ejecutar el proyecto

Para iniciar el juego, en la raiz del proyecto:

```bash
.\start_all.py
```

---

## Servidor de puntuaciones

El proyecto incluye un servidor de puntuaciones para registrar y consultar resultados.

### Funcionalidad

El servidor de puntuaciones permite:

* Guardar puntuaciones de jugadores
* Consultar ranking
* Persistir datos entre sesiones
* Servir puntuaciones a clientes conectados

---

## Montaje del servidor de puntuaciones

Al ejecutar el programa con algun start_all, se ejecutará automaticamente el servidor

---

## Solución de problemas

### El servidor no inicia

Es posible que la ejecución del servidor pueda fallar, esto sucede al intentar hacer la conexion con la base de datos en MongoDB Atlas, sobre todo si se usa la red del instituto ya que el firewall puede estar bloqueando esas direcciones. Posibles soluciones:

* Reinstala Python y sus dependencias
* Comprueba que el puerto no está en uso
* Usa otra red, por ejemplo, conectando el ordenador al movil.

### El cliente no conecta

Verifica:

* IP correcta
* Puerto correcto
* Firewall permitido
* El servidor está en ejecución

---

## Autores
Kai Angulo, Karen Sofía Sanchez y Diego Bermejo