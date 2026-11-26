"""INHALT: Texte, Zeitpunkte und Hervorhebungen. Hier wird normalerweise geändert, nicht in build.py.

Aufbau eines Abschnitts (SPEC_B / SPEC_C / SPEC_D):
  clips : Ausschnitte der Aufnahme.  src=(von, bis) in Sekunden der Aufnahme, out=Dauer im Video
          (out größer als bis-von = Zeitlupe; freeze=True = Standbild).
  beats : Stationen mit Zeiten im Abschnitt (t0/t1 in Sekunden, gerechnet ab Abschnittsbeginn)
          zoom=Bereich, auf den die Kamera fährt   rects=Rahmen   say=Text der Blase (Liste = Zeilen)
          side=Lage der Blase (below/above/left/right/bottom)   callout=kleines Etikett oben
          dim=False -> Umgebung wird nicht abgedunkelt   col=Rahmenfarbe
TEMPO (ganz unten): TEMPO_FAKTOR=2.0 heißt, die Aufnahme läuft halb so schnell; alle Zeiten (out, t0, t1)
werden unten automatisch umgerechnet. Die Zeiten in den Abschnitten unten sind die ursprünglichen "schnellen" Werte.
Rechtecke werden mit R(x0, y0, x1, y1) in Pixeln des Original-Bildes (1920x1080) angegeben.
"""
from engine import R, union, GREEN, RED, ACC

DAUER = dict(einstieg=7.4, abfrage=25.0, abspann=8.4)   # Sekunden; Datenabschnitte ergeben sich aus den clips

T = dict(
    siegel='TAGESAKTUELL', hinweis='Synthetische Beispieldaten',
    eyebrow='Management-Cockpit', titel='SALES INTELLIGENCE',
    claim='Ihr Vertrieb kann mehr. Ihre Daten zeigen, wo.',
    frage1='Sie kennen Ihre Umsätze. Aber wissen Sie auch,', frage2='wo Ihr Vertrieb als Nächstes ansetzen sollte?',
    cta1='Entdecken Sie,', cta2='was in Ihren Vertriebsdaten steckt.', cta3='Tagesaktuell. Jederzeit abrufbar.',
    button='30-Minuten-Dashboard-Schulterblick vereinbaren', domain='betterdecisionsfaster.de',
    ask_kicker='KURZ INNEHALTEN', ask_q1='Welcher Aspekt hat für Ihre Situation', ask_q2='die höchste Relevanz?',
    ask_warte='Nehmen Sie sich 10 Sekunden.', ask_antwort='Antworten Sie einfach mit der Nummer:',
    ask_mail='kontakt@betterdecisionsfaster.de',
    ask_dank='Als Dankeschön: Ihre persönliche Kurz-Einschätzung zu diesem Thema.',
)

OPTS = ['Tagesaktuelle Zahlen statt Excel-Aufwand', 'Kundenverluste früher erkennen',
        'Verkaufschancen gezielt nutzen', 'Mehr Überblick für die Geschäftsführung']

# ------------------------------------------------------------ source rects (raw frame coordinates)
P1 = dict(kpi=R(540, 15, 1090, 155), slider=R(1590, 20, 1910, 85), top20=R(1066, 396, 1792, 1024),
          bar1=R(1080, 476, 1785, 502), chart=R(108, 222, 890, 520), mix=R(108, 580, 872, 1024), insight=R(1066, 222, 1782, 360))
P3 = dict(kpi=R(628, 8, 1505, 145), table=R(80, 193, 950, 838), slicer=R(978, 193, 1124, 402), tops=R(1172, 188, 1900, 537), flops=R(1172, 610, 1900, 988))
P4 = dict(t1=R(432, 10, 705, 152), t2=R(728, 10, 1000, 152), t3=R(1035, 10, 1308, 152), t4=R(1326, 10, 1598, 152),
          gap=R(738, 168, 1360, 302), cross=R(208, 830, 1766, 1008), kunde=R(95, 200, 335, 250), tiles=R(432, 10, 1598, 152),
          texts=R(85, 320, 1878, 460))



CL_B = [dict(src=(1.0, 4.2), out=4.0), dict(src=(5.0, 12.6), out=9.5), dict(src=(22.5, 31.0), out=10.6)]
ALL = [P1['chart'], P1['mix'], P1['kpi'], P1['top20']]
SPEC_B = dict(label='01 · DER ÜBERBLICK', title='Ihr Vertriebs-Cockpit', clips=CL_B, beats=[
    dict(t0=0.6, t1=3.8, say=['Tagesaktuell – und', 'jederzeit abrufbar.'], side='bottom', say_d=0.3),
    dict(t0=4.1, t1=13.0, zoom=union([P1['kpi'], P1['slider']]), rects=[P1['kpi'], P1['slider']], anchor=[P1['kpi']], dim=False, say=['Zeitraum wählen –', 'alle Kennzahlen reagieren sofort.'], side='below'),
    dict(t0=15.0, t1=18.6, rects=[P1['bar1']], dim=False, say=['Ein Klick auf einen Kunden …'], side='above'),
    dict(t0=18.6, t1=24.0, rects=ALL, dim=False, say=['… und alle Auswertungen', 'passen sich an.'], side='below', say_d=0.2)])

CL_C = [dict(src=(63.5, 67.0), out=4.4), dict(src=(67.6, 77.0), out=11.75), dict(src=(93.4, 101.6), out=10.25)]
SPEC_C = dict(label='02 · KUNDENBEWEGUNGEN', title='Wer wächst – und wo gibt es Rückgänge?', clips=CL_C, beats=[
    dict(t0=1.0, t1=4.2, zoom=union([P3['tops'], P3['flops']]), rects=[P3['tops'], P3['flops']], col=GREEN, say=['Wer legt zu – und wo', 'entstehen Rückgänge?'], side='bottom'),
    dict(t0=4.6, t1=16.0, zoom=union([P3['slicer'], P3['table']]), rects=[P3['slicer']], dim=False, say=['Nach Kundenstatus filtern –', 'die Tabelle folgt sofort.'], side='bottom', say_d=0.5),
    dict(t0=16.5, t1=21.2, rects=[P3['tops']], dim=False, col=GREEN, say=['Klick auf einen Kunden –', 'alles zeigt nur noch ihn.'], side='left', dy=90),
    dict(t0=21.6, t1=26.2, rects=[P3['flops']], dim=False, col=RED, say=['Ein Klick auf einen Rückgang', 'macht die Ursache sichtbar.'], side='left')])

CL_D = [dict(src=(128.3, 128.3), out=36.0, freeze=True), dict(src=(157.2, 164.0), out=9.7)]
SPEC_D = dict(label='03 · VERKAUFSCHANCEN', title='Wo liegen die nächsten Verkaufschancen?', clips=CL_D, beats=[
    dict(t0=0.6, t1=4.2, say=['Aus Zahlen werden', 'konkrete Verkaufschancen.'], side='bottom', say_d=0.3),
    dict(t0=4.6, t1=9.4, zoom=P4['t1'], rects=[P4['t1']], say=['Bestehendes Geschäft sichern.'], side='below', callout='36 offene Erneuerungen'),
    dict(t0=9.4, t1=14.2, zoom=P4['t2'], rects=[P4['t2']], say=['Rückläufiges Geschäft', 'zurückgewinnen.'], side='below', callout='62 Recovery-Chancen', col=(255, 170, 120)),
    dict(t0=14.2, t1=19.0, zoom=P4['t3'], rects=[P4['t3']], say=['Zusätzliches Geschäft', 'erschließen.'], side='below', callout='81 Cross-Selling-Chancen', col=GREEN),
    dict(t0=19.0, t1=23.8, zoom=P4['t4'], rects=[P4['t4']], say=['Die attraktivsten Chancen', 'zuerst nutzen.'], side='below', callout='3 Chancen mit hoher Priorität', col=GREEN),
    dict(t0=23.8, t1=30.0, zoom=P4['gap'], rects=[P4['gap']], say=['Identifiziertes Erneuerungs- und', 'Recovery-Potenzial.'], side='below', callout='1,61 Mio. € Opportunity-Lücke'),
    dict(t0=30.0, t1=36.0, zoom=P4['cross'], rects=[P4['cross']], say=['Welcher Kunde? Welches Format?', 'Was konkret anbieten?'], side='above', callout='Konkreter Vertriebsansatz'),
    dict(t0=36.6, t1=45.4, rects=[P4['kunde']], dim=False, say=['Einen Kunden auswählen –', 'die Chancen bei ihm sofort sehen.'], side='right')])




# ------------------------------------------------------------ TEMPO
# Alle Zeiten oben sind im ursprünglichen Tempo geschrieben. Hier werden sie gestreckt:
TEMPO_FAKTOR = 2.0        # Aufnahme-Clips: 2.0 = halb so schnell wie zuvor
STANDBILD_FAKTOR = 1.5    # Standbild-Abschnitte (nur Lesezeit für Texte)
MIND_START = 5.0          # Sekunden, die die Übersicht mit Abschnittsnummer und Titel mindestens stehen bleibt, bevor die Kamera zoomt

def _tempo(clips, spec):
    segs = []; a_alt = 0.0; a_neu = 0.0
    for c in clips:
        f = STANDBILD_FAKTOR if c.get('freeze') else TEMPO_FAKTOR
        segs.append((a_alt, a_alt + c['out'], a_neu, f)); a_alt += c['out']; a_neu += c['out'] * f
    def m(t):
        for a0, a1, n0, f in segs:
            if t <= a1: return n0 + (t - a0) * f
        a0, a1, n0, f = segs[-1]; return n0 + (t - a0) * f
    for c, sg in zip(clips, segs): c['out'] = round(c['out'] * sg[3], 2)
    for b in spec['beats']:
        b['t0'] = round(m(b['t0']), 2); b['t1'] = round(m(b['t1']), 2)
    zooms = [b['t0'] for b in spec['beats'] if b.get('zoom')]
    delta = round(MIND_START - min(zooms), 2) if zooms else 0
    if delta > 0:   # Übersicht mit Titel zuerst länger als Standbild zeigen
        for b in spec['beats']: b['t0'] = round(b['t0'] + delta, 2); b['t1'] = round(b['t1'] + delta, 2)
        s0 = clips[0]['src'][0]; clips.insert(0, dict(src=(s0, s0), out=delta, freeze=True))

for _cl, _sp in ((CL_B, SPEC_B), (CL_C, SPEC_C), (CL_D, SPEC_D)): _tempo(_cl, _sp)
