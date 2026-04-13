Readme · MD


Visual Studio Code

# Taller de Lógica con micro:bit — Metodología PRIMM
 
Recurso docente para trabajar compuertas lógicas y pensamiento computacional con placas **micro:bit** usando la metodología **PRIMM** (Predict · Run · Investigate · Modify · Make).
 
---
 
## ¿Qué contiene este repositorio?
 
```
📁 Fichas_PRIMM/
│   ├── Estacion_01_El_Filtro_Y.pdf
│   ├── Estacion_02_El_Semáforo_Seguro.pdf
│   ├── Estacion_03_La_Caja_Fuerte.pdf
│   ├── Estacion_04_El_Espejo_Mágico.pdf
│   ├── Estacion_05_Alarma_de_Inundación.pdf
│   ├── Estacion_06_El_Sistema_de_Vuelo.pdf
│   ├── Estacion_07_El_Interruptor_Invertido.pdf
│   ├── Estacion_08_La_Bifurcación.pdf
│   ├── Estacion_09_El_Comparador.pdf
│   ├── Estacion_10_El_Acumulador.pdf
│   ├── Estacion_11_Faros_Automáticos.pdf
│   └── Estacion_12_Luces_Interiores.pdf
📄 Fichas_PRIMM_micro-bit.docx   ← todas las estaciones en un solo Word (editable)
📄 primm_pdf.py                  ← script para regenerar o personalizar los PDFs
📄 primm_corrector.py            ← script de corrección automática
📄 README.md                     ← este archivo
```
 
---
 
## Las 12 estaciones
 
| # | Título | Concepto lógico | Entradas |
|---|--------|-----------------|----------|
| 1 | El Filtro "Y" | Conjunción ∧ (AND) | Botón A, Botón B |
| 2 | El Semáforo Seguro | Combinada ∧, ¬ | Botón A, Botón B |
| 3 | La Caja Fuerte | Disyunción ∨ (OR) | Botón A, Botón B |
| 4 | El Espejo Mágico | Bicondicional ↔ | Botón A, Botón B |
| 5 | Alarma de Inundación | Sensores físicos | Pin P0 (agua) |
| 6 | El Sistema de Vuelo | Exclusión XOR | Botón A, Botón B |
| 7 | El Interruptor Invertido | Negación ¬ (NOT) | Botón A |
| 8 | La Bifurcación | Condicional → (IF/ELSE) | Botón A |
| 9 | El Comparador | Desigualdades >, <, = | Sensor de luz |
| 10 | El Acumulador | Variables y conteo | Botón A, Botón B |
| 11 | Faros Automáticos | Multi-regla ∧, ∨, ¬ | Luz, Humedad, Motor, Switch |
| 12 | Luces Interiores | OR en serie | Switch, 3 puertas |
 
> Las estaciones 11 y 12 están adaptadas de [Logic Gates Circuits in Cars — 101 Computing](https://www.101computing.net/logic-gates-circuits-in-cars/).
 
---
 
## Estructura de cada ficha PRIMM
 
Cada estación sigue las cinco fases:
 
| Fase | Descripción | Actividad principal |
|------|-------------|---------------------|
| **PREDICT** | Predecir antes de ejecutar | Completar tabla de verdad (columna "Mi predicción") |
| **RUN** | Ejecutar el programa | Verificar contra la realidad (columna "¿Qué pasó realmente?") |
| **INVESTIGATE** | Investigar el código | Modificar un parámetro y observar el cambio |
| **MODIFY** | Modificar con guía | Cambiar la lógica siguiendo una consigna dada |
| **MAKE** | Crear algo propio | Diseñar una solución original que integre lo aprendido |
 
La tabla de predicción tiene **dos columnas de salida** diferenciadas por color:
- 🟡 **Mi predicción** — el alumno completa *antes* de ejecutar
- 🟢 **¿Qué pasó realmente?** — el alumno completa *después* de probar en la micro:bit
 
---
 
## Uso con alumnos
 
### Distribución digital
 
Los PDFs tienen **campos de formulario interactivos** (AcroForm). Los alumnos pueden completarlos digitalmente desde cualquier lector de PDF.
 
**Lectores compatibles:**
- Adobe Acrobat Reader (gratuito) — guardar con `Ctrl+S`
- Microsoft Edge / Google Chrome — abrir el PDF, completar, `Ctrl+S`
- Foxit Reader — guardar con `Ctrl+S`
- Preview en macOS — guardar con `Cmd+S`
 
> ⚠️ **No usar** "Imprimir → Guardar como PDF" ni "Exportar como PDF" desde ninguna aplicación. Eso aplana el PDF y elimina los campos interactivos.
 
### En Google Classroom
 
1. Subir cada PDF como tarea.
2. Configurar la asignación como **"Los alumnos hacen una copia"**.
3. Los alumnos descargan su copia, la completan y vuelven a subir el archivo guardado.
 
### En papel
 
Las fichas también funcionan impresas. La tabla de predicción queda con espacios en blanco para completar a mano.
 
---
 
## Corrección automática
 
El script `primm_corrector.py` corrige automáticamente la **tabla de predicción y verificación** de cada estación (la única parte con respuestas determinísticas), y verifica si las preguntas abiertas fueron completadas.
 
### ¿Qué corrige?
 
- ✅ **Predicciones correctas** → celda verde con ✓
- ❌ **Predicciones incorrectas** → celda roja con ✗ y la respuesta correcta
- 📝 **Preguntas abiertas** → indica si fueron completadas o dejadas en blanco
- 🏅 **Badge de nota** al final del PDF: *Excelente / Muy bien / En proceso / Revisar*
 
### Cómo entregar los PDFs al corrector
 
**Si tenés Claude (Cowork o similar):** subí el PDF del alumno directamente al chat y pedí que lo corrija. Claude ejecuta el script y te devuelve el PDF corregido sin que necesites instalar nada.
 
**Si querés correr el script vos misma:**
 
Requisitos:
```bash
pip install reportlab pypdf
```
 
Corregir un archivo:
```bash
python primm_corrector.py Estacion_01_NombreAlumno.pdf "Nombre Alumno"
```
 
Corregir una carpeta de entregas completa:
```bash
python primm_corrector.py carpeta_entregas/
```
 
El script genera:
- Un PDF `*_corregido.pdf` por cada entrega con el feedback visual
- Un archivo `resumen_YYYYMMDD_HHMM.csv` con las notas de toda la clase
 
### Formato del CSV de resumen
 
| student | station | pred_correct | pred_total | pct | q_filled | q_total |
|---------|---------|-------------|------------|-----|----------|---------|
| María García | 1 | 3 | 4 | 75.0 | 5 | 6 |
 
---
 
## Generar los PDFs fuera de Claude
 
Los PDFs se generan con Python puro a partir del script `primm_pdf.py` incluido en este repositorio. No hace falta ninguna aplicación paga ni servicio en la nube.
 
### 1 · Instalar Python
 
Si no tenés Python instalado: descargalo desde [python.org/downloads](https://www.python.org/downloads/) (versión 3.9 o superior). Marcá la opción **"Add Python to PATH"** durante la instalación en Windows.
 
### 2 · Instalar las dependencias
 
Abrí una terminal (en Windows: buscá `cmd` o `PowerShell`) y ejecutá:
 
```bash
pip install reportlab pypdf
```
 
### 3 · Instalar la fuente DejaVu Sans
 
Los scripts usan DejaVu Sans para mostrar correctamente los símbolos lógicos (∧ ∨ ¬ → ↔).
 
**Linux** — generalmente ya viene instalada. Si no:
```bash
sudo apt install fonts-dejavu
```
 
**Windows**
1. Descargá el zip desde [dejavu-fonts.github.io](https://dejavu-fonts.github.io/)
2. Descomprimí y copiá los archivos `.ttf` a `C:\Windows\Fonts\`
 
**macOS**
1. Descargá el zip desde [dejavu-fonts.github.io](https://dejavu-fonts.github.io/)
2. Abrí cada `.ttf` con doble clic e instalá
 
> ⚠️ Si la fuente no está en `/usr/share/fonts/truetype/dejavu/` (Linux) abrí `primm_pdf.py` con cualquier editor de texto y cambiá la línea `_DEJA = "..."` al principio del archivo con la ruta correcta de tu sistema.
 
### 4 · Ejecutar los scripts
 
**Generar las 12 fichas en PDF:**
```bash
python primm_pdf.py
```
Los PDFs se guardan en la carpeta `Fichas_PRIMM/` (se crea automáticamente).
 
**Corregir una entrega de un alumno:**
```bash
python primm_corrector.py Estacion_01_NombreAlumno.pdf "Nombre Alumno"
```
 
**Corregir una carpeta completa de entregas:**
```bash
python primm_corrector.py carpeta_entregas/
```
 
### 5 · Personalizar el contenido
 
Todo el contenido de las fichas está definido en el diccionario `CONTENT` dentro de `primm_pdf.py`. Cada estación es una lista de elementos simples:
 
```python
CONTENT = {
    1: [
        ('ph', 'predict'),               # encabezado de fase
        ('t',  'Mirá este código:'),     # texto descriptivo
        ('code', 'Si A Y B → [ ✓ ]'),   # bloque de código
        ('pt', ['Botón A','Botón B'],    # tabla de predicción
               '¿Aparece [ ✓ ]?',
               [['No','No'],['Sí','Sí']]),
        ('b',  '¿Qué observás?'),        # pregunta con campo de respuesta
    ],
    ...
}
```
 
| Tipo | Descripción |
|------|-------------|
| `('ph', key)` | Encabezado de fase: `'predict'`, `'run'`, `'investigate'`, `'modify'`, `'make'` |
| `('t', texto)` | Párrafo descriptivo o instrucción |
| `('b', texto)` | Pregunta con campo de respuesta interactivo |
| `('bi', texto)` | Bullet informativo sin campo de respuesta |
| `('code', texto)` | Bloque de código en monoespaciado (separar líneas con `\n`) |
| `('pt', inputs, etiqueta, filas)` | Tabla de predicción con campos rellenables |
 
Para agregar una estación nueva: añadí su entrada en el diccionario `STATIONS`, creá su clave en `CONTENT` y su respuesta correcta en `ANSWER_KEYS` dentro de `primm_corrector.py`.
 
---
 
## Contexto pedagógico
 
### Metodología PRIMM
 
PRIMM es una metodología de enseñanza de programación desarrollada por **Sue Sentance et al. (King's College London)** que estructura el aprendizaje en cinco fases progresivas. La fase de *predicción* es clave: obliga a los estudiantes a razonar sobre el código antes de ejecutarlo, activando el pensamiento lógico y haciendo explícitos los modelos mentales incorrectos.
 
**Referencia:** Sentance, S., Waite, J., Kallia, M. (2019). *Teaching computer programming with PRIMM: a sociocultural perspective.* Computer Science Education, 29(2–3), 136–176.
 
### Inclusión
 
Las fichas están diseñadas para trabajo en grupos de 2–3 alumnos por estación. Los roles sugeridos son: quien opera la micro:bit, quien completa la tabla, y quien lee las instrucciones en voz alta. Esta distribución favorece la participación de alumnos con distintos perfiles de aprendizaje.
 
---
 
## Licencia
 
Material de uso libre para fines educativos no comerciales.  
Citá la fuente si lo adaptás para tus clases. 🙌
