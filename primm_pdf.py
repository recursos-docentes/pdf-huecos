#!/usr/bin/env python3
"""
Fichas PRIMM micro:bit — PDF Rellenables
Genera 12 fichas PDF independientes con campos de formulario interactivos.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont('Reg',  f'{FONT_DIR}/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold', f'{FONT_DIR}/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Ital', f'{FONT_DIR}/DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('Mono', f'{FONT_DIR}/DejaVuSansMono.ttf'))

# ── Page geometry ──────────────────────────────────────────────────────────────
W, H   = A4
M      = 18 * mm
CW     = W - 2 * M
BLIMIT = M + 14 * mm          # bottom limit before footer

# ── Colour helpers ─────────────────────────────────────────────────────────────
def rgb(h): return colors.Color(int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255)

# ── Config ────────────────────────────────────────────────────────────────────
PHASES = {
    'predict':     {'n':1,'lbl':'PREDICT',    'desc':'Predecir',   'c':'D35400','bg':'FEF9E7'},
    'run':         {'n':2,'lbl':'RUN',        'desc':'Ejecutar',   'c':'1A5E20','bg':'EAFAF1'},
    'investigate': {'n':3,'lbl':'INVESTIGATE','desc':'Investigar', 'c':'1A237E','bg':'EBF5FB'},
    'modify':      {'n':4,'lbl':'MODIFY',     'desc':'Modificar',  'c':'4A148C','bg':'F5EEF8'},
    'make':        {'n':5,'lbl':'MAKE',       'desc':'Crear',      'c':'7B241C','bg':'FDEDEC'},
}
STATIONS = [
    {'n':1,  'color':'1A5276','title':'El Filtro "Y"',          'sub':'La Conjunción  ∧'},
    {'n':2,  'color':'1E8449','title':'El Semáforo Seguro',     'sub':'Combinada  ∧, ¬'},
    {'n':3,  'color':'A04000','title':'La Caja Fuerte',          'sub':'La Disyunción  ∨'},
    {'n':4,  'color':'6C3483','title':'El Espejo Mágico',        'sub':'Bicondicional  ↔'},
    {'n':5,  'color':'117A65','title':'Alarma de Inundación',    'sub':'Sensores Físicos'},
    {'n':6,  'color':'922B21','title':'El Sistema de Vuelo',     'sub':'Exclusión XOR'},
    {'n':7,  'color':'2E4057','title':'El Interruptor Invertido','sub':'La Negación  ¬'},
    {'n':8,  'color':'01695C','title':'La Bifurcación',          'sub':'El Condicional  →'},
    {'n':9,  'color':'880E4F','title':'El Comparador',           'sub':'Desigualdades  >, <, ='},
    {'n':10, 'color':'4E342E','title':'El Acumulador',           'sub':'Variables y Conteo'},
    {'n':11, 'color':'0D47A1','title':'Faros Automáticos',       'sub':'Circuito Multi-Regla  ∧, ∨, ¬'},
    {'n':12, 'color':'4A235A','title':'Luces Interiores',        'sub':'Compuertas OR en Serie'},
]

# ── Station content ───────────────────────────────────────────────────────────
# Element types:
#  ('ph', key)                      phase header
#  ('t',  text)                     descriptive / instruction text
#  ('b',  text)                     bullet question  → gets answer field
#  ('bi', text)                     bullet info      (no answer field)
#  ('code', text)                   monospace code block
#  ('pt', inputs, label, rows)      prediction table with form fields

CONTENT = {
    1: [
        ('ph','predict'),
        ('t','Mirá este código:'),
        ('code','Si (Botón A presionado) Y (Botón B presionado) entonces mostrar [ ✓ ]'),
        ('t','Sin ejecutar el programa, completá la columna "Mi predicción" de la tabla:'),
        ('pt',['Botón A','Botón B'],'¿Aparece [ ✓ ]?',[['No','No'],['Sí','No'],['No','Sí'],['Sí','Sí']]),
        ('b','¿Qué tiene que pasar para que aparezca el ícono? ¿Alcanza con uno solo de los botones?'),
        ('ph','run'),
        ('t','Cargá el programa en la micro:bit y probá las 4 combinaciones. Completá "Resultado real".'),
        ('b','¿Tu tabla de predicción coincidió con la realidad? ¿En qué filas sí y en cuáles no?'),
        ('b','¿Qué nombre le darías a este tipo de condición que necesita AMBAS entradas verdaderas?'),
        ('ph','investigate'),
        ('t','En MakeCode, cambiá el ícono [ ✓ ] por un [ ♥ ].'),
        ('b','¿Cambió la tabla de verdad o solo el dibujo? ¿Por qué?'),
        ('ph','modify'),
        ('t','Cambiá el bloque Y por un bloque O.'),
        ('b','Probá apretar solo el botón A. ¿Qué diferencia notás con el programa anterior? ¿Cambiaría la tabla?'),
        ('ph','make'),
        ('b','Modificá el código para que, si NO estás apretando ningún botón, la micro:bit muestre [ ✗ ].'),
    ],
    2: [
        ('ph','predict'),
        ('t','Código:'),
        ('code','Si (Botón A presionado) Y  NO (Botón B presionado)  entonces mostrar [ ☺ ]'),
        ('t','Recordá: el bloque NO invierte el valor de B antes de evaluar el Y.'),
        ('t','Completá la columna "Mi predicción":'),
        ('pt',['Botón A','Botón B'],'¿Aparece [ ☺ ]?',[['No','No'],['Sí','No'],['No','Sí'],['Sí','Sí']]),
        ('b','¿Qué combinación única activa la carita? ¿Por qué los dos botones juntos no sirven?'),
        ('ph','run'),
        ('t','Cargá y probá. Completá "Resultado real".'),
        ('b','¿Tu tabla coincidió? ¿Hubo alguna fila que te sorprendió?'),
        ('b','Compará con la Estación 1: ¿en qué filas cambia el resultado?'),
        ('ph','investigate'),
        ('t','Sacá el bloque NO y dejalo como  A Y B.'),
        ('b','¿Cómo cambió la tabla de verdad comparada con la que acabás de construir?'),
        ('ph','modify'),
        ('b','Hacé que si el semáforo está en "Pare" (no se cumple la lógica), suene un pitido (micro:bit V2).'),
        ('ph','make'),
        ('b','Crea una "Luz de Noche": Panel encendido si nivel de luz < 50  Y  Botón A  NO  presionado.'),
    ],
    3: [
        ('ph','predict'),
        ('t','Código:'),
        ('code','Si (Botón A presionado) O (Botón B presionado) entonces mostrar [ ◆ ]'),
        ('t','Completá la columna "Mi predicción" y comparala con la de la Estación 1:'),
        ('pt',['Botón A','Botón B'],'¿Aparece [ ◆ ]?',[['No','No'],['Sí','No'],['No','Sí'],['Sí','Sí']]),
        ('b','¿Cuántas formas creés que existen para que aparezca el diamante?'),
        ('ph','run'),
        ('t','Cargá y probá todas las combinaciones. Completá "Resultado real".'),
        ('b','¿Tu predicción fue correcta? ¿Es más fácil o más difícil de activar que la Estación 1 (AND)?'),
        ('b','¿En qué fila(s) difieren las tablas de OR y AND?'),
        ('ph','investigate'),
        ('t','Agregá un tercer botón usando el pin 0:'),
        ('code','(Botón A O Botón B) O (Pin P0 presionado)'),
        ('b','¿Qué pasa si ahora tocás el Pin 0? ¿Aumentan o disminuyen los casos verdaderos?'),
        ('ph','modify'),
        ('b','Cambiá el ícono por [ ☠ ] si NO se presiona ninguno de los dos botones.'),
        ('ph','make'),
        ('b','Crea un sistema donde la puerta se abra con el Botón A  O  al agitar la placa (Gesto: agitar).'),
    ],
    4: [
        ('ph','predict'),
        ('t','Código:'),
        ('code','Si (Botón A presionado) == (Botón B presionado) entonces mostrar [ SÍ ]'),
        ('t','El  ==  es verdadero cuando ambos lados tienen el MISMO estado. Completá tu predicción:'),
        ('pt',['Botón A','Botón B'],'¿Aparece [ SÍ ]?',[['No','No'],['Sí','No'],['No','Sí'],['Sí','Sí']]),
        ('b','¿Cuándo es FALSA la condición? ¿Tiene sentido con el nombre "bicondicional"?'),
        ('ph','run'),
        ('t','Cargá y probá. Completá "Resultado real".'),
        ('b','¿Tu predicción fue correcta? ¿Qué pasa cuando los botones están en estados diferentes?'),
        ('b','¿Cuántas combinaciones hacen que la condición sea FALSA?'),
        ('ph','investigate'),
        ('t','Cambiá el símbolo  ==  por  ≠  (Diferente).'),
        ('b','¿Qué lógica representa ahora? ¿Qué relación tiene con la tabla que construiste?'),
        ('ph','modify'),
        ('b','Hacé que muestre una flecha  ←  si apretás A y una flecha  →  si apretás B.'),
        ('ph','make'),
        ('b','Diseñá un "Juego de Reincidencia": Si ambos jugadores aprietan a la vez → [ ♥ ], si no → [ ✗ ].'),
    ],
    5: [
        ('ph','predict'),
        ('t','Código:'),
        ('code','Si (Pin P0 presionado) entonces mostrar [ ☂ ]'),
        ('t','El Pin P0 actúa como una entrada lógica: circuito cerrado = Verdadero. Predecí:'),
        ('pt',['Estado del Pin P0'],'¿Aparece [ ☂ ]?',[['Abierto (sin agua)'],['Cerrado (con agua)']]),
        ('b','¿El agua conduce electricidad suficiente para actuar como un "Verdadero" lógico?'),
        ('ph','run'),
        ('t','Conectá los cables cocodrilo al Pin 0 y a GND. Probá en el vaso con agua.'),
        ('b','¿Tu predicción coincidió? ¿Qué valor lógico representa el agua cerrando el circuito?'),
        ('b','Probá ahora con tus dedos mojados: ¿tu cuerpo también conduce?'),
        ('ph','investigate'),
        ('t','Probá tocar los cables con distintos materiales: papel, metal, plástico, fruta.'),
        ('b','¿Cuáles conducen y cuáles no? ¿Qué los hace "Verdadero" o "Falso" en la lógica del circuito?'),
        ('ph','modify'),
        ('b','Agregá condición: la alarma sólo suena si hay agua  Y  el Botón B está presionado.'),
        ('ph','make'),
        ('b','Crea una alarma de "Nivel Crítico": detectar agua Y que el nivel de luz sea alto.'),
    ],
    6: [
        ('ph','predict'),
        ('t','Código (OR exclusivo — solo uno de los dos, nunca ambos):'),
        ('code','Si (Botón A O Botón B)  Y  NO (Botón A Y Botón B)  entonces mostrar [ ✈ ]'),
        ('t','Pensá paso a paso: primero OR, luego descartá el caso donde ambos son Sí. Completá:'),
        ('pt',['Botón A','Botón B'],'¿Aparece [ ✈ ]?',[['No','No'],['Sí','No'],['No','Sí'],['Sí','Sí']]),
        ('b','¿Qué diferencia tiene la fila (Sí, Sí) respecto a la Estación 3 (OR)?'),
        ('ph','run'),
        ('t','Cargá y probá. Completá "Resultado real".'),
        ('b','¿Tu predicción fue correcta? ¿Por qué el XOR es más seguro que un simple OR para un motor?'),
        ('b','Comparando con OR (Est. 3): ¿solo difieren en una fila?'),
        ('ph','investigate'),
        ('t','Desarmá el código en MakeCode y tratá de reconstruirlo vos solo (3 bloques anidados).'),
        ('ph','modify'),
        ('b','Si se presionan ambos (A y B), hacé que la placa muestre el mensaje "ERROR".'),
        ('ph','make'),
        ('b','Crea un ascensor: Solo puede ir al Piso 1 (A) o Piso 2 (B). Ambos juntos → bloqueo.'),
    ],
    7: [
        ('ph','predict'),
        ('t','Mirá este código:'),
        ('code','Si  NO (Botón A presionado)  entonces mostrar [ ♥ ]'),
        ('t','El bloque NO invierte el valor: si A es Verdadero, NO A es Falso, y viceversa. Predecí:'),
        ('pt',['Botón A presionado'],'¿Aparece [ ♥ ]?',[['No (sin presionar)'],['Sí (presionado)']]),
        ('b','¿Cuándo se apaga el corazón? ¿Por qué el ícono aparece "al revés" de lo que esperarías?'),
        ('ph','run'),
        ('t','Cargá y probá. Completá "Resultado real".'),
        ('b','¿Tu predicción coincidió? ¿Qué conclusión sacás sobre el bloque NO?'),
        ('b','¿Qué pasa si el programa corre y no hacés nada — el ícono aparece o no?'),
        ('ph','investigate'),
        ('t','Cambiá el código a doble negación:'),
        ('code','Si  NO NO (Botón A presionado)  entonces mostrar [ ♥ ]'),
        ('b','¿Es igual al código sin ningún NO? ¿Qué conclusión sacás sobre la doble negación?'),
        ('ph','modify'),
        ('t','Probá esta combinación:'),
        ('code','Si  NO (Botón A)  Y  NO (Botón B)  entonces mostrar [ ☺ ]'),
        ('b','¿En cuántas de las 4 combinaciones aparece la carita? (Pista: Ley de De Morgan)'),
        ('ph','make'),
        ('b','Crea una "Luz Nocturna": estrella [ ✦ ] cuando nivel de luz NO sea alto (< 100).'),
    ],
    8: [
        ('ph','predict'),
        ('t','Código:'),
        ('code','Si (Botón A presionado)  entonces mostrar [ ✓ ]  de lo contrario mostrar [ ✗ ]'),
        ('t','Este programa siempre muestra ALGO. Predecí qué muestra en cada caso:'),
        ('pt',['Botón A presionado'],'¿Qué muestra?',[['Sí (presionado)'],['No (sin presionar)']]),
        ('b','¿Puede existir algún momento en que la pantalla no muestre nada? ¿Por qué?'),
        ('ph','run'),
        ('t','Cargá y probá los dos casos. Completá "Resultado real".'),
        ('b','¿Tu predicción fue correcta? ¿Siempre hay una respuesta visible?'),
        ('b','¿Qué pasa con la pantalla entre que soltás A y volvés a apretarlo?'),
        ('ph','investigate'),
        ('t','Eliminá el bloque "de lo contrario" (else).'),
        ('b','¿Qué pasa ahora cuando NO apretás el botón? ¿Qué diferencia hay con el else?'),
        ('ph','modify'),
        ('t','Agregá un segundo nivel de decisión:'),
        ('code','Si A → mostrar [ ✓ ]   Si B → mostrar [ ? ]   de lo contrario → mostrar [ ✗ ]'),
        ('b','¿Cuántas "ramas" de decisión tiene ahora? ¿Qué pasa si apretás A y B juntos?'),
        ('ph','make'),
        ('b','Crea un "Consejero Climático": temperatura > 28°C → [ ☀ ], < 15°C → [ ❄ ], si no → [ ☁ ].'),
    ],
    9: [
        ('ph','predict'),
        ('t','Código:'),
        ('code','Si (nivel de luz < 50)  entonces mostrar [ ☽ ]'),
        ('t','Predecí: ¿cuándo aparece la luna según el nivel de luz del sensor?'),
        ('pt',['Condición del sensor de luz'],'¿Aparece [ ☽ ]?',[
            ['Tapado con el dedo (oscuro, ~10)'],
            ['Normal en el aula (~200–400)'],
            ['Bajo luz directa (~800+)'],
        ]),
        ('b','¿El valor de corte es 50? ¿Qué representa ese número en la práctica?'),
        ('ph','run'),
        ('t','Probá tapando y destapando el sensor. Completá "Resultado real".'),
        ('b','¿Tu predicción coincidió? ¿Qué valor de luz hay ahora mismo en tu aula?'),
        ('b','¿Encontraste el valor límite exacto? ¿Es exactamente 50 o hay margen?'),
        ('ph','investigate'),
        ('t','Cambiá el operador  <  por  >.'),
        ('b','¿Cómo cambió el comportamiento? ¿Qué ocurre en el valor límite 50 exacto?'),
        ('ph','modify'),
        ('t','Combiná dos sensores:'),
        ('code','Si (nivel de luz < 50)  Y  (temperatura > 25)  entonces mostrar [ ☀ ]'),
        ('b','¿Qué situación del mundo real podría representar esta condición combinada?'),
        ('ph','make'),
        ('b','Diseñá un "Detector de Presencia": [ ◆ ] si nivel de luz baja de golpe  Y  Botón A activo.'),
    ],
    10: [
        ('ph','predict'),
        ('t','Código:'),
        ('code','contador = 0\nCuando A presionado: contador = contador + 1\nSi contador >= 3  →  mostrar [ ◆ ]'),
        ('t','Pensá cuántas veces hay que apretar A para llegar al umbral. Completá tu predicción:'),
        ('pt',['Cantidad de presiones de A'],'¿Aparece [ ◆ ]?',[
            ['1 presión'],['2 presiones'],['3 presiones'],['4 o más presiones'],
        ]),
        ('b','¿A partir de cuántas presiones aparece el ícono? ¿Sigue apareciendo después?'),
        ('ph','run'),
        ('t','Cargá y probá contando en voz alta. Completá "Resultado real".'),
        ('b','¿Tu predicción coincidió? ¿Se acumulan las presiones entre cada una?'),
        ('b','¿Qué pasa si seguís apretando A después de llegar a 3? ¿El ícono sigue o se va?'),
        ('ph','investigate'),
        ('t','Cambiá el umbral de 3 a 5.'),
        ('b','¿El contador se resetea solo al mostrar el ícono, o sigue subiendo indefinidamente?'),
        ('ph','modify'),
        ('t','Agregá un reset:'),
        ('code','Cuando Botón B presionado:  contador = 0  →  mostrar [ ✗ ]'),
        ('b','¿Para qué sirve tener un reset en un sistema lógico real? Dá un ejemplo cotidiano.'),
        ('ph','make'),
        ('b','Crea una "Cerradura de Combinación": [ ✓ ] si Botón A es presionado exactamente 3 veces y luego Botón B 1 vez. Si no → [ ✗ ].'),
    ],
    11: [
        ('ph','predict'),
        ('t','Lee las cuatro reglas del sistema automático de faros:'),
        ('bi','Regla 1: Los faros se encienden si el motor está ON y está oscuro afuera (noche o túnel).'),
        ('bi','Regla 2: Los faros se encienden si el motor está ON y está lloviendo.'),
        ('bi','Regla 3: Los faros se encienden si el interruptor manual está activado (aunque el motor esté apagado).'),
        ('bi','Regla 4: Si no se cumple ninguna regla, los faros se apagan.'),
        ('t','La fórmula lógica completa (L=luz, H=humedad, M=motor, S=switch manual):'),
        ('code','Faros  =  (M ∧ ¬L)  ∨  (M ∧ H)  ∨  S'),
        ('t','Aplicá las reglas a cada escenario y completá "Mi predicción" ANTES de ejecutar:'),
        ('pt',
            ['Sensor Luz (L)','Humedad (H)','Motor (M)','Switch (S)'],
            '¿Faros encendidos?',
            [
                ['Día (1)','Seco (0)','OFF (0)','OFF (0)'],
                ['Día (1)','Seco (0)','ON (1)','OFF (0)'],
                ['Noche (0)','Seco (0)','ON (1)','OFF (0)'],
                ['Noche (0)','Lluvia (1)','ON (1)','OFF (0)'],
                ['Día (1)','Lluvia (1)','ON (1)','OFF (0)'],
                ['Noche (0)','Seco (0)','OFF (0)','OFF (0)'],
                ['Día (1)','Seco (0)','OFF (0)','ON (1)'],
                ['Noche (0)','Lluvia (1)','OFF (0)','ON (1)'],
            ]
        ),
        ('b','¿Cuántos de los 8 escenarios encienden los faros? ¿Qué regla activa más casos?'),
        ('b','¿Por qué el escenario 6 (Noche + Motor OFF + Switch OFF) los apaga? ¿Tiene sentido en un auto real?'),
        ('ph','run'),
        ('t','Mapeo micro:bit: Botón A = Motor (M), Botón B = Switch (S), sensor de luz = Luz (L), Pin P0 = Lluvia (H).'),
        ('code','Si (A Y NO(luz>100)) O (A Y P0) O B  →  mostrar [ 💡 ]\nde lo contrario  →  mostrar [ ○ ]'),
        ('t','Simulá cada fila: tapá el sensor para "noche", cerrá Pin P0 para "lluvia". Completá "Resultado real".'),
        ('b','¿Tu predicción coincidió con todos los escenarios? ¿Hubo alguno que te sorprendió?'),
        ('b','Identificá qué regla (1, 2 ó 3) dispara los faros en las filas 3, 5 y 7.'),
        ('ph','investigate'),
        ('t','Analizá la fórmula simplificada  M ∧ (¬L ∨ H)  ∨  S  (factor común M).'),
        ('b','¿Produce la misma tabla de verdad que la fórmula original? Verificalo con las filas 3 y 5.'),
        ('b','Si el motor está apagado y está lloviendo fuerte, ¿los faros se encienden? ¿Debería ser así?'),
        ('ph','modify'),
        ('t','Agregá una Regla 5: Luces de emergencia se activan si se presionan A y B al mismo tiempo.'),
        ('b','Modificá la fórmula y el código. ¿La nueva regla usa AND, OR o NOT? ¿Por qué?'),
        ('ph','make'),
        ('b','Diseñá un "Sistema DRL": luz tenue siempre activa con motor ON, faros plenos cuando se cumpla la Regla 1 ó 2. Usá dos íconos distintos para cada nivel.'),
    ],
    12: [
        ('ph','predict'),
        ('t','Los autos modernos encienden la luz interior con estas reglas:'),
        ('bi','Regla 1: La luz se enciende si el interruptor manual está activado.'),
        ('bi','Regla 2: La luz se enciende si al menos una puerta está abierta (conductor, pasajero o maletero).'),
        ('bi','Regla 3: Si no se cumple ninguna regla, la luz se apaga.'),
        ('t','Fórmula del sistema (S=switch, D=conductor, P=pasajero, B=maletero):'),
        ('code','Luz  =  S  ∨  D  ∨  P  ∨  B'),
        ('t','Aplicá las reglas y completá "Mi predicción":'),
        ('pt',
            ['Switch (S)','P. Conductor (D)','P. Pasajero (P)','Maletero (B)'],
            '¿Luz interior?',
            [
                ['OFF (0)','Cerrada (0)','Cerrada (0)','Cerrado (0)'],
                ['ON (1)','Cerrada (0)','Cerrada (0)','Cerrado (0)'],
                ['OFF (0)','Abierta (1)','Cerrada (0)','Cerrado (0)'],
                ['OFF (0)','Cerrada (0)','Abierta (1)','Cerrado (0)'],
                ['OFF (0)','Cerrada (0)','Cerrada (0)','Abierto (1)'],
                ['OFF (0)','Abierta (1)','Abierta (1)','Cerrado (0)'],
            ]
        ),
        ('b','¿Cuántas combinaciones de las 6 encienden la luz? ¿Cuál NO la enciende?'),
        ('b','¿La compuerta OR necesita que TODAS las entradas sean 1, o basta con una?'),
        ('ph','run'),
        ('t','Mapeo: Botón A = Switch (S), Pin P0 = Conductor (D), Pin P1 = Pasajero (P), Botón B = Maletero (B).'),
        ('code','Si A O P0 O P1 O B  →  mostrar [ 💡 ]\nde lo contrario  →  mostrar [ ○ ]'),
        ('t','Simulá cada fila. Completá "Resultado real".'),
        ('b','¿Tu predicción coincidió? ¿Qué combinación fue la única en que la luz se apaga?'),
        ('b','Compará la fórmula de esta estación con la de Faros (Est. 11): ¿cuál es más compleja? ¿Por qué?'),
        ('ph','investigate'),
        ('t','¿Qué pasa si agregás una cuarta puerta (Pin P2)?'),
        ('b','¿Cambia la estructura de la fórmula o solo se extiende? Modificá el código y probalo.'),
        ('b','¿Cuántas combinaciones de 5 entradas existirían en total? (Pista: 2⁵)'),
        ('ph','modify'),
        ('t','Agregá un temporizador: la luz se apaga automáticamente 3 s después de cerrar todas las puertas.'),
        ('b','¿Necesitás lógica adicional o alcanza con un bloque "pausa"? Implementalo y probá.'),
        ('ph','make'),
        ('b','Diseñá un sistema de "Cortesía al subir": al abrir cualquier puerta → luz al 50% (ícono tenue). Al cerrarlas todas → baja gradualmente durante 5 s. Usá variables para simular el brillo.'),
    ],
}

# ── Renderer ──────────────────────────────────────────────────────────────────
class StationRenderer:
    def __init__(self, s, out_path):
        self.s  = s
        self.c  = canvas.Canvas(out_path, pagesize=A4)
        self.y  = H - M
        self.pg = 1
        self.fc = 0   # field counter

    # ── helpers ────────────────────────────────────────────────────────────────
    def _fid(self, tag):
        self.fc += 1
        return f"s{self.s['n']}_{tag}_{self.fc}"

    def _footer(self):
        self.c.setFont('Reg', 7.5)
        self.c.setFillColor(rgb('9E9E9E'))
        self.c.drawCentredString(
            W/2, 8*mm,
            f"Estación {self.s['n']}  ·  {self.s['title']}  ·  Metodología PRIMM  ·  Página {self.pg}"
        )

    def _newpage(self):
        self._footer()
        self.c.showPage()
        self.pg += 1
        self.y  = H - M

    def _need(self, h):
        if self.y - h < BLIMIT:
            self._newpage()

    def _wrap(self, txt, font, size, width):
        return simpleSplit(txt, font, size, width)

    # ── drawing primitives ────────────────────────────────────────────────────
    def draw_banner(self):
        bh = 27 * mm
        col = rgb(self.s['color'])
        self.c.setFillColor(col)
        self.c.rect(M, self.y - bh, CW, bh, fill=1, stroke=0)
        self.c.setFillColor(colors.white)
        self.c.setFont('Bold', 18)
        self.c.drawString(M + 5*mm, self.y - 9*mm, f"ESTACIÓN {self.s['n']}")
        self.c.setFont('Bold', 13)
        self.c.drawString(M + 5*mm, self.y - 17*mm, self.s['title'])
        self.c.setFont('Reg', 9)
        self.c.setFillColor(rgb('DDDDDD'))
        self.c.drawString(M + 5*mm, self.y - 24*mm, f"· {self.s['sub']}")
        self.y -= bh + 5*mm

    def draw_phase(self, key):
        ph = PHASES[key]
        h  = 9 * mm
        self._need(h + 6*mm)
        self.y -= 4*mm
        col = rgb(ph['c']); bg = rgb(ph['bg'])
        # background
        self.c.setFillColor(bg)
        self.c.rect(M, self.y - h, CW, h, fill=1, stroke=0)
        # left accent
        self.c.setFillColor(col)
        self.c.rect(M, self.y - h, 3*mm, h, fill=1, stroke=0)
        # text
        self.c.setFillColor(col)
        self.c.setFont('Bold', 12)
        self.c.drawString(M + 6*mm, self.y - 6.5*mm, f"{ph['n']}. {ph['lbl']}")
        self.c.setFont('Ital', 9)
        self.c.drawString(M + 6*mm + 48*mm, self.y - 6.5*mm, f"({ph['desc']})")
        self.y -= h + 3*mm

    def draw_text(self, txt, indent=5*mm):
        lines = self._wrap(txt, 'Reg', 9.5, CW - indent)
        lh    = 5 * mm
        self._need(len(lines)*lh + 2*mm)
        self.c.setFillColor(rgb('1A1A1A'))
        for ln in lines:
            self.c.setFont('Reg', 9.5)
            self.c.drawString(M + indent, self.y - 4*mm, ln)
            self.y -= lh
        self.y -= 1.5*mm

    def draw_bullet(self, txt, with_field=True):
        bx   = M + 5*mm
        tx   = M + 10*mm
        avail = CW - 10*mm
        lines = self._wrap(txt, 'Reg', 9.5, avail)
        lh    = 5 * mm
        fh    = 14 * mm
        needed = len(lines)*lh + (fh + 3*mm if with_field else 2*mm)
        self._need(needed)
        # bullet dot
        self.c.setFillColor(rgb('37474F'))
        self.c.setFont('Bold', 12)
        self.c.drawString(bx, self.y - 4.5*mm, '•')
        # text lines
        self.c.setFont('Reg', 9.5)
        self.c.setFillColor(rgb('1A1A1A'))
        for i, ln in enumerate(lines):
            self.c.drawString(tx, self.y - 4*mm, ln)
            if i < len(lines)-1:
                self.y -= lh
        self.y -= lh
        if with_field:
            self.c.acroForm.textfield(
                name=self._fid('q'),
                x=tx, y=self.y - fh,
                width=CW - 10*mm, height=fh,
                fontSize=9,
                fieldFlags='multiline',
                borderColor=rgb('B0BEC5'),
                fillColor=rgb('F9FAFB'),
                textColor=rgb('212121'),
            )
            self.y -= fh + 3*mm
        else:
            self.y -= 1*mm

    def draw_code(self, txt):
        lines = txt.split('\n')
        lh    = 5 * mm
        pad   = 5 * mm
        bh    = len(lines)*lh + 2*pad
        self._need(bh + 2*mm)
        # background
        self.c.setFillColor(rgb('ECEFF1'))
        self.c.rect(M, self.y - bh, CW, bh, fill=1, stroke=0)
        # left accent
        self.c.setFillColor(rgb('546E7A'))
        self.c.rect(M, self.y - bh, 3*mm, bh, fill=1, stroke=0)
        # text
        self.c.setFont('Mono', 8.5)
        self.c.setFillColor(rgb('263238'))
        cy = self.y - pad - 3.5*mm
        for ln in lines:
            self.c.drawString(M + 6*mm, cy, ln)
            cy -= lh
        self.y -= bh + 2*mm

    def draw_pred_table(self, inputs, out_label, rows):
        n_in   = len(inputs)
        n_cols = n_in + 2

        # column proportions
        if n_in == 1:
            cws = [CW*0.30, CW*0.35, CW*0.35]
        elif n_in == 2:
            cws = [CW*0.18, CW*0.18, CW*0.32, CW*0.32]
        else:  # 4 inputs
            cws = [CW*0.145, CW*0.145, CW*0.145, CW*0.145, CW*0.21, CW*0.21]

        ROW_H  = 7.5 * mm
        n_rows = 2 + len(rows)   # hdr + sub-hdr + data
        total  = ROW_H * n_rows + 2*mm
        self._need(total)

        tx = M
        ty = self.y

        # Header colours
        hdr_fill = [*[rgb('37474F')]*n_in, rgb('7B5E00'), rgb('1A5E20')]
        headers  = [*inputs, 'Mi predicción', '¿Qué pasó realmente?']

        # ── header row ──
        x = tx
        for ci in range(n_cols):
            cw = cws[ci]
            self.c.setFillColor(hdr_fill[ci])
            self.c.rect(x, ty - ROW_H, cw, ROW_H, fill=1, stroke=0)
            self.c.setFillColor(colors.white)
            fs  = 7.5 if ci < n_in else 7
            fnt = 'Bold'
            lns = self._wrap(headers[ci], fnt, fs, cw - 3*mm)
            base_y = ty - ROW_H/2 + (len(lns)-1)*2*mm
            for ln in lns:
                self.c.setFont(fnt, fs)
                self.c.drawCentredString(x + cw/2, base_y, ln)
                base_y -= 3.8*mm
            x += cw

        # ── sub-header row (out_label) ──
        sy = ty - ROW_H
        x  = tx
        subBg  = [*[rgb('ECEFF1')]*n_in, rgb('FFF9C4'), rgb('C8E6C9')]
        subFg  = [*[rgb('607D8B')]*n_in, rgb('795548'), rgb('2E7D32')]
        subLbl = [*['Entrada']*n_in, out_label, out_label]
        for ci in range(n_cols):
            cw = cws[ci]
            self.c.setFillColor(subBg[ci])
            self.c.rect(x, sy - ROW_H, cw, ROW_H, fill=1, stroke=0)
            self.c.setFillColor(subFg[ci])
            self.c.setFont('Ital', 6.5)
            lns = self._wrap(subLbl[ci], 'Ital', 6.5, cw - 2*mm)
            base_y = sy - ROW_H/2 + (len(lns)-1)*1.8*mm
            for ln in lns:
                self.c.drawCentredString(x + cw/2, base_y, ln)
                base_y -= 3.2*mm
            x += cw

        # ── data rows ──
        for ri, row in enumerate(rows):
            ry  = ty - ROW_H * (ri + 2)
            row_bg = rgb('F5F8FA') if ri % 2 == 0 else rgb('FFFFFF')
            x = tx
            for ci in range(n_cols):
                cw = cws[ci]
                if ci < n_in:
                    # fixed input cell
                    self.c.setFillColor(row_bg)
                    self.c.rect(x, ry - ROW_H, cw, ROW_H, fill=1, stroke=0)
                    self.c.setFillColor(rgb('212121'))
                    self.c.setFont('Reg', 7.5)
                    lns = self._wrap(row[ci], 'Reg', 7.5, cw - 2*mm)
                    base_y = ry - ROW_H/2 + (len(lns)-1)*1.8*mm
                    for ln in lns:
                        self.c.drawCentredString(x + cw/2, base_y, ln)
                        base_y -= 3.2*mm
                elif ci == n_in:
                    # prediction form field
                    self.c.setFillColor(rgb('FFFDE7'))
                    self.c.rect(x, ry - ROW_H, cw, ROW_H, fill=1, stroke=0)
                    self.c.acroForm.textfield(
                        name=f"s{self.s['n']}_pred_{ri}",
                        x=x+1, y=ry - ROW_H + 1,
                        width=cw-2, height=ROW_H-2,
                        fontSize=8,
                        borderColor=rgb('D4C000'),
                        fillColor=rgb('FFFDE7'),
                        textColor=rgb('212121'),
                    )
                else:
                    # reality form field
                    self.c.setFillColor(rgb('F1F8E9'))
                    self.c.rect(x, ry - ROW_H, cw, ROW_H, fill=1, stroke=0)
                    self.c.acroForm.textfield(
                        name=f"s{self.s['n']}_real_{ri}",
                        x=x+1, y=ry - ROW_H + 1,
                        width=cw-2, height=ROW_H-2,
                        fontSize=8,
                        borderColor=rgb('4CAF50'),
                        fillColor=rgb('F1F8E9'),
                        textColor=rgb('212121'),
                    )
                x += cw

        # ── grid lines ──
        self.c.setStrokeColor(rgb('B0BEC5'))
        self.c.setLineWidth(0.4)
        for row_i in range(n_rows + 1):
            gy = ty - ROW_H * row_i
            self.c.line(tx, gy, tx + sum(cws), gy)
        x = tx
        for cw in cws:
            self.c.line(x, ty, x, ty - ROW_H * n_rows)
            x += cw
        self.c.line(tx + sum(cws), ty, tx + sum(cws), ty - ROW_H * n_rows)

        self.y = ty - ROW_H * n_rows - 4*mm

    # ── height estimation (pre-pass, no drawing) ────────────────────────────
    def _est_elem(self, elem):
        t = elem[0]
        if t == 'ph':
            return 4*mm + 9*mm + 3*mm               # pre-gap + bar + post-gap
        elif t == 't':
            lns = self._wrap(elem[1], 'Reg', 9.5, CW - 5*mm)
            return len(lns) * 5*mm + 1.5*mm
        elif t == 'b':
            lns = self._wrap(elem[1], 'Reg', 9.5, CW - 10*mm)
            return len(lns) * 5*mm + 14*mm + 3*mm   # text + field + gap
        elif t == 'bi':
            lns = self._wrap(elem[1], 'Reg', 9.5, CW - 10*mm)
            return len(lns) * 5*mm + 1*mm
        elif t == 'code':
            n = len(elem[1].split('\n'))
            return n * 5*mm + 10*mm + 2*mm           # lines + 2×padding + gap
        elif t == 'pt':
            n_rows = len(elem[3]) + 2                # hdr + sub-hdr + data
            return n_rows * 7.5*mm + 4*mm
        return 5*mm

    def _group_by_phase(self, content):
        """Split content list into sublists, each starting with its 'ph' header."""
        groups, current = [], []
        for elem in content:
            if elem[0] == 'ph' and current:
                groups.append(current)
                current = [elem]
            else:
                current.append(elem)
        if current:
            groups.append(current)
        return groups

    def _draw_elem(self, elem):
        t = elem[0]
        if   t == 'ph':   self.draw_phase(elem[1])
        elif t == 't':    self.draw_text(elem[1])
        elif t == 'b':    self.draw_bullet(elem[1], with_field=True)
        elif t == 'bi':   self.draw_bullet(elem[1], with_field=False)
        elif t == 'code': self.draw_code(elem[1])
        elif t == 'pt':   self.draw_pred_table(elem[1], elem[2], elem[3])

    # ── main render ──────────────────────────────────────────────────────────
    def render(self):
        self.draw_banner()
        full_page = H - M - BLIMIT      # usable height on a fresh page

        for group in self._group_by_phase(CONTENT[self.s['n']]):
            group_h   = sum(self._est_elem(e) for e in group)
            available = self.y - BLIMIT

            if group_h > available:
                # Section fits entirely on the next page → jump now
                if group_h <= full_page:
                    self._newpage()
                # Section is multi-page but we're already in the bottom 40% → jump
                elif available < full_page * 0.40:
                    self._newpage()

            for elem in group:
                self._draw_elem(elem)

        self._footer()
        self.c.save()


# ── Generate all PDFs ─────────────────────────────────────────────────────────
def safe_name(s):
    return s.replace('"','').replace("'",'').replace(' ','_').replace('/','').replace('\\','')

if __name__ == '__main__':
    OUT_DIR = "/sessions/funny-nifty-hawking/mnt/Lógica y Matemática Discreta/Fichas_PRIMM"
    os.makedirs(OUT_DIR, exist_ok=True)
    for st in STATIONS:
        fname = f"Estacion_{st['n']:02d}_{safe_name(st['title'])}.pdf"
        path  = os.path.join(OUT_DIR, fname)
        renderer = StationRenderer(st, path)
        renderer.render()
        print(f"✓  {fname}")
    print(f"\n✓ 12 fichas generadas en {OUT_DIR}")
