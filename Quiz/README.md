# Anleitung um ein Quiz zu spielen:

## Aufbau
Verbinde Knöpfe und Leds wie im Schaublid mit einem Aruidno Mega.
Lade die arduino_code.ino Datei aus dem arduino Ordner auf dem Arduino.

## Starten ohne Computer
Wenn du beim an Strom anschließen den einzelnen Knopf drückst, 
startet der Arduino in einem Modus, in dem gar kein Computer für die 
Verwendung benötigt wird. Es kann dann einfach mit dem Knopf immerwieder eine
neue Fragerunde gestartet werden.

## Verwenden des Quiz-Spiels
Verbinde den Arduino per USB mit deinem Computer und starte dann 
(z.B über den Launcher) das Quiz Spiel. Wähle im Menu den Anschluss aus,
an den du den Arduino angeschlossen hat. 
Wähle dann an welchen Ports du ein Buzzer eingesteckt hast und gib den Spielern
ein Name sowie deren Teamaufteilung. 
Wähle jetzt noch das gewünschte Quiz und schon kann es los gehen.

## Eigenes Quiz erstellen
Füge dem Ordner 'questions' eine neue .json Datei hin zu oder kopiere ein
bereits vorhandenes Quiz.

### Für das Quiz hast du folgende Einstellungsmöglichkeiten:

```
  "Name": "<< Name des Quizes >>",
  "Questions Random": true,
  "ask wrong questions again": true,
  "Number asked questions": 10,
  "Background file": "<< Bilddateiname für Hintergrundbild >>",
  "Text color": [255,255,255],
  "Rect color": [150,150,150],
  "Text on Rect color": [0,0,0],
```

- Name: ist der Name des Quizes im Auswahlmenu
- Questions Random: 'true', wenn die Fragen in zufälliger Reihenfolge gestellt 
  werden sollen, ansonsten 'false'
- ask wrong questions again: 'true', damit falsch beantwortete Fragen nochmals 
  gestellt werden, ansonsten 'false'
- Number asked questions: Anzahl der gefragten Fragen
- Background file: Dateiname für den Hintergrund (Datei muss im Ordner 'img' liegen).
  Nichts übergeben ("") für den Standarthintergrund
- Text color: Farbe der Text, die direkt aud fem Hintergrund zu sehen sind
- Rect color: Farbe der Rechtecke (für z.B. Antowrtmöglichkeiten oder Spielernamen)
- Text on Rect color: Farbe für die Texte, die auf den Rechtecken zu sehen sind

Farben sind rgb Werte (also 3 Zahlen von 0 bis 255 für Rot-Gelb-Grün)

### Fragen

Lege die Fragen in einem Feld ab:

```
"Questions": [
    { << Frage 1 >>},
    { << Frage 2 >>},
    { ... }
]
```

Jede Frage hat den Wert 'Type', der bestimmt was für eine Frage es ist.
Sowie den Werte 'Points mode', für die Punktevergabe
```
{
    "Type": "<< Fragetyp (Multiple Choice, Building up Image, Question) >>",
    << andere Werte >>

    "Points mode": "<< Punktesystem (Add/remove points, Time points) >>",
    << andere Werte >>
}
```

#### Multiple Choice
Frage mit beliebig vielen Antwortmöglichkeiten.
```
"Type": "Multiple Choice",
"Question": "<< Frage >>",
"Question read time": 2,
"Answers": ["<< Antwort 1 >>", "<< Antowrt 2 >>", "..."],
"Correct Answer": 0,
"Shuffle Answers": true,
```
- Question: Die Frage
- Question read time: Bevor die Antwortmöglichkeiten erscheinen wird erst nur
  die Frage dargestellt, um diese zu lesen. Die Angabe gibt an, wie viele 
  Sekunden man zum Lesen hat.
- Answers: Antwortmäglichkeiten in einem Feld
- Correct Answer: Die Nummer der richtigen Antwort (mit 0 anfangen zu zählen)
- Shuffle Answers: Wenn 'true' werden die Antworten in zufälliger Reihenfolge angezeigt,
  ansonsten bei 'false' in der vorgegebenen Reihenfolge

#### Building up Image
Bild, dass sich Stück für Stück aufbaut.
```
"Type": "Building up Image",
"Image": "<< Dateiname des Bildes >>",
"Answer": "<< Antowrt >>",
"Building Type": "Rect",
"Building Size": 25,
"Building Time": 8,
"Top Color": [30,30,30],
```
- Image: Dateiname für das Bild (Datei muss im Ordner 'img' liegen)
- Answer: richtige Antwort
- Building Type: Art, wie das Bild Stück für Stück auftaucht
  ('Random': eines der nachfolgenden zufällig,
  'Rect': in Rechtecken, 'Dots': durch zufällig plazierte Kreise)
- Building Size: Größe der Objekte, die das Bild Sichtbarmachen
  (bei 'Rect' Anzahl der Quadrate auf über die Bildbreite, 
  bei 'dots' wird die Bildbreite durch diessen Wert als Durchmesser genommen)
- Building Time: Zeit bis das Bild komplett zu sehen ist
- Top Color: Farbe, die das Bild vor dem Enthüllen hat

#### einfache Frage
```
"Type": "Question",
"Question": "<< Frage >>",
"Answer": "<< Antwort >>",
( "Image": "example_building_up.png", )
```
- Question: Die Frage
- Answer: Die Antwort
- Image: Wenn dieser Wert vorhanden ist wird zusätzlich zur Frage noch ein Bild
  gezeigt (Datei muss im Ordner 'img' liegen)
  
### Punkte Systeme
Wird eine FRage beantwortet, werden dem Spieler je nach Ergebniss Punkte
abgetogen oder hinzugefügt

#### Punkte abziehen/hinzufügen
Abzug bei falschen Antworten, Pluspunkte für Richtige.
```
"Points mode": "Add/remove points",
"reduction for wrong answer": 20,
"points for right answer": 60
```
- reduction for wrong answer: Abzug für falsche Antworten
- points for right answer: Punkte für richtige Antworten

#### Punkte auf Zeit
Punkte je nachdem wie schnell geantwortet wurde.
```
"Points mode": "Time points",
"start points": 150,
"point reduction per second": 10,
"min points": 30
```
- start points: Punktzahl am Anfang (maximal erreichbar)
- point reduction per second: Weniger Punkte pro Sekunde
- min points: Mindest Anzahl an Punkten, nachdem der Wert nicht weiter sinkt