# 🚀 Migración de PostgreSQL a MongoDB Atlas

Este guía te ayudará a migrar tu proyecto Buckshot Roulette de PostgreSQL a MongoDB Atlas en la nube.

## ✅ Cambios Realizados

### 📦 Dependencias
- ❌ Removido: `psycopg2-binary` (PostgreSQL)
- ✅ Agregado: `pymongo==4.6.0` (MongoDB)

### 📝 Archivos Modificados
- `requirements.txt` - Reemplazado PostgreSQL por MongoDB
- `config.py` - Configuración de MongoDB Atlas en lugar de PostgreSQL
- `models.py` - Actualizado para usar operaciones MongoDB (no SQL)
- `app.py` - Importa `mongodb` en lugar de `database`
- `init_db.py` - Script de inicialización para MongoDB
- `start_all.bat` - No requiere PostgreSQL

### 🆕 Archivos Nuevos
- `mongodb.py` - Clase MongoDatabase con manejo de conexiones optimizado
- `.env.ejemplo` - Template de configuración

---

## 🔧 Instalación Paso a Paso

### **Paso 1: Crear Cuenta MongoDB Atlas** (5 min)

1. Ve a: https://www.mongodb.com/cloud/atlas/register
2. Crea una cuenta **gratuita**
3. Crea un nuevo proyecto (ej: "Buckshot Roulette")
4. Crea un **Cluster M0** (gratuito, suficiente para desarrollo)

```
Nombre: buckshot-roulette
Proveedor: AWS (o el que prefieras)
Región: Elige la más cercana a ti
```

### **Paso 2: Crear Usuario de Base de Datos**

1. En MongoDB Atlas, ve a **Database Access**
2. Haz clic en **Add New Database User**
3. Configura:
   ```
   Nombre: buckshot_user
   Contraseña: [Genera una contraseña fuerte]
   Permisos: Atlas admin
   ```
4. **Copia la contraseña** (la necesitarás después)

### **Paso 3: Permitir Tu IP**

1. Ve a **Network Access** en MongoDB Atlas
2. Haz clic en **Add IP Address**
3. Opción rápida: Agrega `0.0.0.0/0` (permite cualquier IP, solo para desarrollo)
   - ⚠️ En producción, usa solo tu IP

### **Paso 4: Obtener Connection String**

1. Ve a **Clusters** y haz clic en **Connect**
2. Selecciona **Drivers** → **Python**
3. Copia la connection string que se parece a esto:
   ```
   mongodb+srv://buckshot_user:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

### **Paso 5: Configurar tu Aplicación**

1. En la raíz del proyecto, copia `.env.ejemplo` a `.env`:
   ```bash
   copy .env.ejemplo .env
   ```

2. Edita `.env` y reemplaza:
   ```
   MONGODB_URL=mongodb+srv://buckshot_user:TU_PASSWORD@cluster-name.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=buckshot_roulette
   ```

   **Ejemplo real:**
   ```
   MONGODB_URL=mongodb+srv://buckshot_user:mySuperPassword123@buckshot-roulette.abcdef.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=buckshot_roulette
   ```

### **Paso 6: Instalar Dependencias**

```bash
# Crea venv (si no existe)
python -m venv venv

# Activa venv
.\venv\Scripts\activate

# Instala las nuevas dependencias
pip install -r requirements.txt
```

### **Paso 7: Verificar Conexión**

```bash
# Desde la carpeta servidor/
cd servidor
python init_db.py
```

**Debería mostrar:**
```
✅ Conexión exitosa a MongoDB Atlas
Colecciones disponibles:
   - puntuaciones
   - sesiones_juego
```

---

## 🎮 Ejecutar la Aplicación

Una vez configurado, ejecuta como siempre:

```bash
# Desde la raíz del proyecto
.\start_all.bat
```

O manualmente:

```bash
# Terminal 1 - Servidor
cd servidor
python app.py

# Terminal 2 - Cliente
cd cliente
python main.py
```

---

## 🔄 Migración de Datos (Opcional)

Si tenías datos en PostgreSQL y quieres migrarlos a MongoDB:

### Opción 1: Script Manual

```python
# En servidor/migrate_data.py
from datetime import datetime
from database import init_db as init_pg
from mongodb import init_db as init_mongo
from config import get_config

config = get_config()
db_pg = init_pg(config)  # PostgreSQL antiguo
db_mongo = init_mongo(config)  # MongoDB nuevo

# Migrar puntuaciones
with db_pg.get_cursor() as cursor:
    cursor.execute("SELECT nombre, puntos, fecha, session_id FROM puntuaciones")
    for row in cursor.fetchall():
        db_mongo.insert_one('puntuaciones', {
            'nombre': row[0],
            'puntos': row[1],
            'fecha': row[2],
            'session_id': row[3]
        })

# Migrar sesiones
with db_pg.get_cursor() as cursor:
    cursor.execute("SELECT * FROM sesiones_juego")
    for row in cursor.fetchall():
        db_mongo.insert_one('sesiones_juego', {
            'session_id': row[1],
            'nombre_jugador': row[2],
            'fecha_inicio': row[3],
            'fecha_fin': row[4],
            'puntos_finales': row[5],
            'balas_disparadas': row[6]
        })
```

### Opción 2: Empezar de Cero

Si no necesitas datos antiguos, simplemente comienza nuevo con MongoDB.

---

## 📊 Diferencias: PostgreSQL vs MongoDB

### PostgreSQL (Anterior)
```
Tablas: SQL, esquema rígido
puntuaciones (id, nombre, puntos, fecha, session_id)
sesiones_juego (id, session_id, nombre_jugador, ...)

Query: SELECT * FROM puntuaciones ORDER BY puntos DESC
```

### MongoDB (Nuevo)
```
Colecciones: Documentos JSON, esquema flexible
db.puntuaciones.find({}).sort({puntos: -1})

Ventajas:
✅ Sin instalación local (nube)
✅ Escalable automáticamente
✅ Flexible (cambiar campos fácil)
✅ Tier gratuito M0
```

---

## 🐛 Solución de Problemas

### Error: "Cannot authenticate"
- ❌ Contraseña incorrecta en .env
- ✅ Verifica que la contraseña sea la correcta (sin caracteres especiales escapados)

### Error: "Connection timed out"
- ❌ Tu IP no está permitida
- ✅ Agrega tu IP en Network Access (o usa 0.0.0.0/0 para desarrollo)

### Error: "No module named 'pymongo'"
- ❌ pymongo no está instalado
- ✅ Ejecuta: `pip install -r requirements.txt`

### Error: "Cannot connect to MongoDB"
- ❌ Cluster no está corriendo o URL es incorrecta
- ✅ Verifica que el cluster esté en estado "Running" en MongoDB Atlas

---

## 📚 Recursos

- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
- PyMongo Docs: https://pymongo.readthedocs.io/
- MongoDB Query Language: https://docs.mongodb.com/manual/

---

## ✨ ¡Listo!

¡Tu aplicación ahora usa MongoDB Atlas en la nube! 🎉

- ❌ Sin instalación de PostgreSQL
- ✅ Base de datos en la nube
- ✅ Escalable y mantenido por MongoDB
