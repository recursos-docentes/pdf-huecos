#!/usr/bin/env python3
"""
Corrector Automático — Fichas PRIMM micro:bit
=============================================
Uso:
  python3 primm_corrector.py <archivo_alumno.pdf>
  python3 primm_corrector.py <carpeta_de_entregas/>      ← corrige todos los PDFs

Genera:
  - Un PDF corregido por alumno (celdas verde/rojo, nota)
  - Un resumen CSV con todas las notas

Sólo corrige automáticamente la tabla de predicción (respuestas determinísticas).
Los campos de preguntas abiertas se marcan como "completado" o "sin completar".
"""

import os, sys, re, csv
from datetime import datetime
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# ── Fonts ─────────────────────────────────────────────────────────────────────
_DEJA = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont('Reg',  f'{_DEJA}/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold', f'{_DEJA}/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Ital', f'{_DEJA}/DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('Mono', f'{_DEJA}/DejaVuSansMono.ttf'))

# ── Page geometry ──────────────────────────────────────────────────────────────
W, H   = A4
M      = 18 * mm
CW     = W - 2 * M
BLIMIT = M + 14 * mm

def rgb(h): return colors.Color(int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255)

# ── Config ────────────────────────────────────────────────────────────────────
PHASES = {
    'predict':     {'n':1,'lbl':'PREDICT',    'desc':'Predecir',   'c':'D35400','bg':'FEF9E7'},
    'run':         {'n':2,'lbl':'RUN',        'desc':'Ejecutar',   'c':'1A5E20','bg':'EAFAF1'},
    'investigate': {'n':3,'lbl':'INVESTIGATE','desc':'Investigar', 'c':'1A237E','bg':'EBF5FB'},
    'modify':      {'n':4,'lbl':'MODIFY',     'desc':'Modificar',  'c':'4A148C','bg':'F5EEF8'},
    'make':        {'n':5,'lbl':'MAKE',       'desc':'Crear',      'c':'7B241C','bg':'FDEDEC'},
}
STATIONS = {
    1: {'color':'1A5276','title':'El Filtro "Y"',          'sub':'La Conjunción  ∧'},
    2: {'color':'1E8449','title':'El Semáforo Seguro',     'sub':'Combinada  ∧, ¬'},
    3: {'color':'A04000','title':'La Caja Fuerte',          'sub':'La Disyunción  ∨'},
    4: {'color':'6C3483','title':'El Espejo Mágico',        'sub':'Bicondicional  ↔'},
    5: {'color':'117A65','title':'Alarma de Inundación',   'sub':'Sensores Físicos'},
    6: {'color':'922B21','title':'El Sistema de Vuelo',    'sub':'Exclusión XOR'},
    7: {'color':'2E4057','title':'El Interruptor Invertido','sub':'La Negación  ¬'},
    8: {'color':'01695C','title':'La Bifurcación',          'sub':'El Condicional  →'},
    9: {'color':'880E4F','title':'El Comparador',           'sub':'Desigualdades  >, <, ='},
   10: {'color':'4E342E','title':'El Acumulador',           'sub':'Variables y Conteo'},
   11: {'color':'0D47A1','title':'Faros Automáticos',       'sub':'Circuito Multi-Regla  ∧, ∨, ¬'},
   12: {'color':'4A235A','title':'Luces Interiores',        'sub':'Compuertas OR en Serie'},
}

# ── Answer keys ──────────────────────────────────────────────────────────────
# Correct prediction for each row of the prediction table, per station.
# Values are normalised to lowercase "sí" / "no" for binary tables,
# or a short text for station 8 (which asks "what does it show?").
ANSWER_KEYS = {
    1:  ['no','no','no','sí'],               # AND
    2:  ['no','sí','no','no'],               # AND + NOT
    3:  ['no','sí','sí','sí'],               # OR
    4:  ['sí','no','no','sí'],               # Bicondicional ==
    5:  ['no','sí'],                         # Sensor PIN
    6:  ['no','sí','sí','no'],               # XOR
    7:  ['sí','no'],                         # NOT (heart when NOT pressed)
    8:  ['✓','✗'],                           # IF/ELSE (what it shows)
    9:  ['sí','no','no'],                    # Comparador (<50)
   10:  ['no','no','sí','sí'],               # Counter >=3
   11:  ['no','no','sí','sí','sí','no','sí','sí'],  # Faros
   12:  ['no','sí','sí','sí','sí','sí'],     # Interior lights
}

# Accepted equivalent spellings per canonical answer
ACCEPTED = {
    'sí':  {'sí','si','s','1','true','verdadero','yes','encendido','encendida','on','aparece'},
    'no':  {'no','n','0','false','falso','apagado','apagada','off','no aparece'},
    '✓':   {'✓','[✓]','[ ✓ ]','check','correcto','sí','si','yes'},
    '✗':   {'✗','[✗]','[ ✗ ]','x','incorrecto','no'},
}

def normalise(v):
    return (v or '').strip().lower().replace('\u00ed','i')   # handle í → i fallback

def is_correct(student_val, expected_key):
    sv   = normalise(student_val)
    ek   = expected_key.lower()
    accepted = ACCEPTED.get(ek, {ek})
    return normalise(sv) in {normalise(a) for a in accepted}

# ── Read filled PDF ───────────────────────────────────────────────────────────
def read_fields(pdf_path):
    reader = PdfReader(pdf_path)
    raw    = reader.get_fields() or {}
    result = {}
    for k, v in raw.items():
        val = v.get('/V', '')
        if hasattr(val, 'original_bytes'):
            val = str(val)
        result[k] = str(val).strip() if val else ''
    return result

def detect_station(pdf_path, fields):
    """Detect station number from filename or from embedded field names."""
    name = os.path.basename(pdf_path)
    m = re.search(r'Estacion[_\s]*0?(\d{1,2})', name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # Fallback: check field name prefix
    for k in fields:
        m2 = re.match(r's(\d+)_', k)
        if m2:
            return int(m2.group(1))
    return None

# ── Correction renderer ───────────────────────────────────────────────────────
class CorrectedRenderer:
    """Renders a corrected version of a station worksheet with student answers."""

    def __init__(self, station_n, student_answers, out_path, student_name=''):
        self.n    = station_n
        self.s    = STATIONS[station_n]
        self.ans  = student_answers          # dict field_name → student value
        self.keys = ANSWER_KEYS[station_n]   # list of correct answers for pred rows
        self.c    = canvas.Canvas(out_path, pagesize=A4)
        self.y    = H - M
        self.pg   = 1
        self.name = student_name
        # Scoring
        self.pred_correct = 0
        self.pred_total   = 0
        self.q_filled     = 0
        self.q_total      = 0

    def _footer(self):
        self.c.setFont('Reg', 7.5)
        self.c.setFillColor(rgb('9E9E9E'))
        label = f"Estación {self.n}  ·  {self.s['title']}  ·  CORRECCIÓN"
        if self.name:
            label += f"  ·  {self.name}"
        self.c.drawCentredString(W/2, 8*mm, label + f"  ·  Pág. {self.pg}")

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

    # ── Banner ────────────────────────────────────────────────────────────────
    def draw_banner(self):
        bh = 27 * mm
        col = rgb(self.s['color'])
        self.c.setFillColor(col)
        self.c.rect(M, self.y - bh, CW, bh, fill=1, stroke=0)
        # Station label
        self.c.setFillColor(colors.white)
        self.c.setFont('Bold', 18)
        self.c.drawString(M + 5*mm, self.y - 9*mm, f"ESTACIÓN {self.n}")
        self.c.setFont('Bold', 13)
        self.c.drawString(M + 5*mm, self.y - 17*mm, self.s['title'])
        self.c.setFont('Reg', 9)
        self.c.setFillColor(rgb('DDDDDD'))
        self.c.drawString(M + 5*mm, self.y - 24*mm, f"· {self.s['sub']}")
        # CORRECTION badge (top-right)
        bx = M + CW - 36*mm
        self.c.setFillColor(rgb('F57F17'))
        self.c.roundRect(bx, self.y - 11*mm, 36*mm, 9*mm, 2*mm, fill=1, stroke=0)
        self.c.setFillColor(colors.white)
        self.c.setFont('Bold', 10)
        self.c.drawCentredString(bx + 18*mm, self.y - 7*mm, 'CORRECCIÓN')
        if self.name:
            self.c.setFont('Reg', 7.5)
            self.c.setFillColor(rgb('EEEEEE'))
            self.c.drawCentredString(bx + 18*mm, self.y - 19*mm, self.name)
        self.y -= bh + 5*mm

    # ── Score badge (drawn at end, first page) ─────────────────────────────
    def draw_score_badge(self, pred_c, pred_t, q_filled, q_total):
        if pred_t == 0:
            return
        pct   = pred_c / pred_t
        color = ('2E7D32' if pct >= 0.75 else 'F57F17' if pct >= 0.50 else 'B71C1C')
        label = ('Excelente 🌟' if pct == 1.0 else
                 'Muy bien ✓'  if pct >= 0.75 else
                 'En proceso'  if pct >= 0.50 else 'Revisar')
        self.c.setFillColor(rgb(color))
        self.c.roundRect(M, self.y - 14*mm, CW, 14*mm, 2*mm, fill=1, stroke=0)
        self.c.setFillColor(colors.white)
        self.c.setFont('Bold', 12)
        score_txt = f"Predicción: {pred_c}/{pred_t} correctas"
        q_txt     = f"  ·  Preguntas completadas: {q_filled}/{q_total}"
        self.c.drawString(M + 6*mm, self.y - 9*mm, score_txt + q_txt)
        self.c.setFont('Ital', 10)
        self.c.drawRightString(M + CW - 4*mm, self.y - 9*mm, label)
        self.y -= 14*mm + 3*mm

    # ── Phase header ──────────────────────────────────────────────────────────
    def draw_phase(self, key):
        ph = PHASES[key]
        h  = 9 * mm
        self._need(h + 6*mm)
        self.y -= 4*mm
        col = rgb(ph['c']); bg = rgb(ph['bg'])
        self.c.setFillColor(bg)
        self.c.rect(M, self.y - h, CW, h, fill=1, stroke=0)
        self.c.setFillColor(col)
        self.c.rect(M, self.y - h, 3*mm, h, fill=1, stroke=0)
        self.c.setFillColor(col)
        self.c.setFont('Bold', 12)
        self.c.drawString(M + 6*mm, self.y - 6.5*mm, f"{ph['n']}. {ph['lbl']}")
        self.c.setFont('Ital', 9)
        self.c.drawString(M + 6*mm + 48*mm, self.y - 6.5*mm, f"({ph['desc']})")
        self.y -= h + 3*mm

    # ── Instruction text ──────────────────────────────────────────────────────
    def draw_text(self, txt):
        lines = self._wrap(txt, 'Reg', 9.5, CW - 5*mm)
        self._need(len(lines)*5*mm + 2*mm)
        self.c.setFillColor(rgb('1A1A1A'))
        for ln in lines:
            self.c.setFont('Reg', 9.5)
            self.c.drawString(M + 5*mm, self.y - 4*mm, ln)
            self.y -= 5*mm
        self.y -= 1.5*mm

    # ── Code block ───────────────────────────────────────────────────────────
    def draw_code(self, txt):
        lines = txt.split('\n')
        lh  = 5*mm; pad = 5*mm
        bh  = len(lines)*lh + 2*pad
        self._need(bh + 2*mm)
        self.c.setFillColor(rgb('ECEFF1'))
        self.c.rect(M, self.y - bh, CW, bh, fill=1, stroke=0)
        self.c.setFillColor(rgb('546E7A'))
        self.c.rect(M, self.y - bh, 3*mm, bh, fill=1, stroke=0)
        self.c.setFont('Mono', 8.5)
        self.c.setFillColor(rgb('263238'))
        cy = self.y - pad - 3.5*mm
        for ln in lines:
            self.c.drawString(M + 6*mm, cy, ln)
            cy -= lh
        self.y -= bh + 2*mm

    # ── Bullet with student answer ────────────────────────────────────────────
    def draw_bullet(self, txt, field_name, with_field=True):
        bx = M + 5*mm; tx = M + 10*mm
        lines = self._wrap(txt, 'Reg', 9.5, CW - 10*mm)
        lh = 5*mm; fh = 14*mm
        needed = len(lines)*lh + (fh + 3*mm if with_field else 2*mm)
        self._need(needed)

        self.c.setFillColor(rgb('37474F'))
        self.c.setFont('Bold', 12)
        self.c.drawString(bx, self.y - 4.5*mm, '•')
        self.c.setFont('Reg', 9.5)
        self.c.setFillColor(rgb('1A1A1A'))
        for i, ln in enumerate(lines):
            self.c.drawString(tx, self.y - 4*mm, ln)
            if i < len(lines)-1:
                self.y -= lh
        self.y -= lh

        if with_field:
            self.q_total += 1
            student_val = self.ans.get(field_name, '')
            filled = bool(student_val.strip())
            if filled:
                self.q_filled += 1
            bg_color = rgb('F1F8E9') if filled else rgb('FFF8E1')
            border_c = rgb('81C784') if filled else rgb('FFB300')

            # Draw static answer box
            self.c.setFillColor(bg_color)
            self.c.setStrokeColor(border_c)
            self.c.setLineWidth(0.7)
            self.c.roundRect(tx, self.y - fh, CW - 10*mm, fh, 1.5*mm, fill=1, stroke=1)

            if filled:
                # Student's answer text
                self.c.setFillColor(rgb('1B5E20'))
                ans_lines = self._wrap(student_val, 'Reg', 8.5, CW - 14*mm)
                ay = self.y - fh/2 + (len(ans_lines)-1)*2.2*mm
                for al in ans_lines[:3]:  # max 3 lines shown
                    self.c.setFont('Reg', 8.5)
                    self.c.drawString(tx + 2*mm, ay, al)
                    ay -= 4.5*mm
            else:
                self.c.setFillColor(rgb('BF8C00'))
                self.c.setFont('Ital', 8)
                self.c.drawString(tx + 2*mm, self.y - fh/2 - 1.5*mm, '— sin completar —')

            self.y -= fh + 3*mm
        else:
            self.y -= 1*mm

    # ── Prediction table with correction ─────────────────────────────────────
    def draw_pred_table(self, inputs, out_label, rows):
        n_in   = len(inputs)
        n_cols = n_in + 2

        if n_in == 1:
            cws = [CW*0.30, CW*0.35, CW*0.35]
        elif n_in == 2:
            cws = [CW*0.18, CW*0.18, CW*0.32, CW*0.32]
        else:
            cws = [CW*0.145, CW*0.145, CW*0.145, CW*0.145, CW*0.21, CW*0.21]

        ROW_H  = 7.5 * mm
        n_rows = 2 + len(rows)
        total  = ROW_H * n_rows + 2*mm
        self._need(total)

        tx = M; ty = self.y
        hdr_fill = [*[rgb('37474F')]*n_in, rgb('7B5E00'), rgb('1A5E20')]
        headers  = [*inputs, 'Mi predicción', '¿Qué pasó realmente?']

        # Header row
        x = tx
        for ci in range(n_cols):
            cw = cws[ci]
            self.c.setFillColor(hdr_fill[ci])
            self.c.rect(x, ty - ROW_H, cw, ROW_H, fill=1, stroke=0)
            self.c.setFillColor(colors.white)
            fs = 7.5 if ci < n_in else 7
            lns = self._wrap(headers[ci], 'Bold', fs, cw - 3*mm)
            by = ty - ROW_H/2 + (len(lns)-1)*2*mm
            for ln in lns:
                self.c.setFont('Bold', fs)
                self.c.drawCentredString(x + cw/2, by, ln)
                by -= 3.8*mm
            x += cw

        # Sub-header row
        sy = ty - ROW_H; x = tx
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
            by = sy - ROW_H/2 + (len(lns)-1)*1.8*mm
            for ln in lns:
                self.c.drawCentredString(x + cw/2, by, ln)
                by -= 3.2*mm
            x += cw

        # Data rows
        for ri, row in enumerate(rows):
            ry     = ty - ROW_H * (ri + 2)
            row_bg = rgb('F5F8FA') if ri % 2 == 0 else rgb('FFFFFF')
            expected = self.keys[ri] if ri < len(self.keys) else None

            pred_val = self.ans.get(f"s{self.n}_pred_{ri}", '')
            real_val = self.ans.get(f"s{self.n}_real_{ri}", '')

            pred_ok  = is_correct(pred_val, expected) if expected else None
            real_ok  = is_correct(real_val, expected) if expected else None

            # Count scoring for prediction column
            self.pred_total += 1
            if pred_ok:
                self.pred_correct += 1

            x = tx
            for ci in range(n_cols):
                cw = cws[ci]
                if ci < n_in:
                    # Fixed input cell
                    self.c.setFillColor(row_bg)
                    self.c.rect(x, ry - ROW_H, cw, ROW_H, fill=1, stroke=0)
                    self.c.setFillColor(rgb('212121'))
                    self.c.setFont('Reg', 7.5)
                    lns = self._wrap(row[ci], 'Reg', 7.5, cw - 2*mm)
                    by = ry - ROW_H/2 + (len(lns)-1)*1.8*mm
                    for ln in lns:
                        self.c.drawCentredString(x + cw/2, by, ln)
                        by -= 3.2*mm

                elif ci == n_in:
                    # Prediction cell — colour-coded
                    if pred_val:
                        cell_bg = rgb('C8E6C9') if pred_ok else rgb('FFCDD2')
                    else:
                        cell_bg = rgb('FFF9C4')   # no answer: yellow
                    self.c.setFillColor(cell_bg)
                    self.c.rect(x, ry - ROW_H, cw, ROW_H, fill=1, stroke=0)

                    # Student's answer
                    if pred_val:
                        self.c.setFillColor(rgb('1B5E20') if pred_ok else rgb('B71C1C'))
                        self.c.setFont('Bold', 8)
                        self.c.drawCentredString(x + cw/2, ry - ROW_H*0.55, pred_val[:20])
                        # Tick or cross indicator
                        icon = '✓' if pred_ok else '✗'
                        self.c.setFont('Bold', 9)
                        self.c.drawString(x + cw - 5*mm, ry - ROW_H*0.55, icon)
                    else:
                        self.c.setFillColor(rgb('9E6E00'))
                        self.c.setFont('Ital', 7)
                        self.c.drawCentredString(x + cw/2, ry - ROW_H*0.55, '—')

                    # Show correct answer if wrong
                    if pred_val and not pred_ok and expected:
                        self.c.setFillColor(rgb('B71C1C'))
                        self.c.setFont('Ital', 6.5)
                        self.c.drawCentredString(x + cw/2, ry - ROW_H*0.85,
                                                 f'→ {expected}')

                else:
                    # Reality cell — colour-coded
                    if real_val:
                        cell_bg = rgb('C8E6C9') if real_ok else rgb('FFCDD2')
                    else:
                        cell_bg = rgb('F1F8E9')
                    self.c.setFillColor(cell_bg)
                    self.c.rect(x, ry - ROW_H, cw, ROW_H, fill=1, stroke=0)

                    if real_val:
                        self.c.setFillColor(rgb('1B5E20') if real_ok else rgb('B71C1C'))
                        self.c.setFont('Bold', 8)
                        self.c.drawCentredString(x + cw/2, ry - ROW_H*0.55, real_val[:20])
                        icon = '✓' if real_ok else '✗'
                        self.c.setFont('Bold', 9)
                        self.c.drawString(x + cw - 5*mm, ry - ROW_H*0.55, icon)
                    else:
                        self.c.setFillColor(rgb('4CAF50'))
                        self.c.setFont('Ital', 7)
                        self.c.drawCentredString(x + cw/2, ry - ROW_H*0.55, '—')

                x += cw

        # Grid lines
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

    # ── Height estimation (same as original) ──────────────────────────────────
    def _est_elem(self, t, *args):
        if t == 'ph':   return 4*mm + 9*mm + 3*mm
        if t == 't':    return len(self._wrap(args[0],'Reg',9.5,CW-5*mm))*5*mm + 1.5*mm
        if t == 'b':    return len(self._wrap(args[0],'Reg',9.5,CW-10*mm))*5*mm + 14*mm + 3*mm
        if t == 'bi':   return len(self._wrap(args[0],'Reg',9.5,CW-10*mm))*5*mm + 1*mm
        if t == 'code': return len(args[0].split('\n'))*5*mm + 10*mm + 2*mm
        if t == 'pt':   return (len(args[2])+2)*7.5*mm + 4*mm
        return 5*mm

    # ── Render ────────────────────────────────────────────────────────────────
    def render(self, content):
        self.draw_banner()
        full_page = H - M - BLIMIT

        # Group by phase for keep-together logic
        groups, cur = [], []
        for elem in content:
            if elem[0] == 'ph' and cur:
                groups.append(cur); cur = [elem]
            else:
                cur.append(elem)
        if cur: groups.append(cur)

        # Track question field counter — must match _fid('q') in primm_pdf.py
        # which produces  s{n}_q_{counter}  (underscore before number)
        q_counter = [0]

        def next_q():
            q_counter[0] += 1
            return f"s{self.n}_q_{q_counter[0]}"

        first_group = True
        for group in groups:
            group_h   = sum(self._est_elem(*e) for e in group)
            available = self.y - BLIMIT
            if group_h > available:
                if group_h <= full_page or available < full_page * 0.40:
                    self._newpage()

            # Insert score badge after first group (PREDICT)
            if first_group and not groups.index(group) == 0:
                pass  # handled below
            first_group = False

            for elem in group:
                t = elem[0]
                if   t == 'ph':   self.draw_phase(elem[1])
                elif t == 't':    self.draw_text(elem[1])
                elif t == 'b':    self.draw_bullet(elem[1], next_q(), with_field=True)
                elif t == 'bi':   self.draw_bullet(elem[1], None,     with_field=False)
                elif t == 'code': self.draw_code(elem[1])
                elif t == 'pt':   self.draw_pred_table(elem[1], elem[2], elem[3])

        # Score badge at bottom of last page
        self._need(17*mm)
        self.y -= 3*mm
        self.draw_score_badge(self.pred_correct, self.pred_total,
                               self.q_filled, self.q_total)
        self._footer()
        self.c.save()
        return {
            'pred_correct': self.pred_correct,
            'pred_total':   self.pred_total,
            'q_filled':     self.q_filled,
            'q_total':      self.q_total,
        }


# ── Content (same as primm_pdf.py) ───────────────────────────────────────────
from primm_pdf import CONTENT   # reuse the content definitions


# ── Main corrector ────────────────────────────────────────────────────────────
def correct_one(pdf_path, out_dir, student_name=''):
    """Correct a single filled PDF and save the result."""
    fields  = read_fields(pdf_path)
    station = detect_station(pdf_path, fields)
    if station is None or station not in STATIONS:
        print(f"  ✗ No se pudo detectar la estación en: {os.path.basename(pdf_path)}")
        return None

    base   = os.path.splitext(os.path.basename(pdf_path))[0]
    suffix = f"_{student_name}" if student_name else ''
    out    = os.path.join(out_dir, f"{base}_corregido{suffix}.pdf")

    renderer = CorrectedRenderer(station, fields, out, student_name)
    scores   = renderer.render(CONTENT[station])
    pct      = scores['pred_correct']/scores['pred_total']*100 if scores['pred_total'] else 0
    print(f"  ✓ Est.{station:02d}  pred: {scores['pred_correct']}/{scores['pred_total']}"
          f" ({pct:.0f}%)  preguntas: {scores['q_filled']}/{scores['q_total']}"
          f"  →  {os.path.basename(out)}")
    return {**scores, 'station': station, 'file': os.path.basename(pdf_path),
            'pct': pct, 'student': student_name}


def correct_folder(folder, student_name=''):
    """Correct all filled PDFs in a folder."""
    out_dir = os.path.join(folder, 'corregidos')
    os.makedirs(out_dir, exist_ok=True)
    pdfs    = sorted(f for f in os.listdir(folder) if f.lower().endswith('.pdf')
                     and 'corregido' not in f.lower())
    if not pdfs:
        print("No se encontraron archivos PDF en la carpeta.")
        return

    print(f"\nCorrigiendo {len(pdfs)} archivo(s)...\n")
    results = []
    for f in pdfs:
        r = correct_one(os.path.join(folder, f), out_dir, student_name)
        if r:
            results.append(r)

    # CSV summary
    if results:
        csv_path = os.path.join(out_dir, f'resumen_{datetime.now():%Y%m%d_%H%M}.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=['student','station','file',
                                               'pred_correct','pred_total','pct',
                                               'q_filled','q_total'])
            w.writeheader()
            w.writerows(results)
        print(f"\n✓ Resumen guardado en: {csv_path}")

    total_pred = sum(r['pred_correct'] for r in results)
    total_max  = sum(r['pred_total']   for r in results)
    if total_max:
        print(f"\nPromedio predicciones: {total_pred}/{total_max} "
              f"({total_pred/total_max*100:.0f}%)")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    target = sys.argv[1]
    name   = sys.argv[2] if len(sys.argv) > 2 else ''

    if os.path.isdir(target):
        correct_folder(target, name)
    elif os.path.isfile(target):
        out_dir = os.path.dirname(target) or '.'
        correct_one(target, out_dir, name)
    else:
        print(f"Error: no existe '{target}'")
        sys.exit(1)
