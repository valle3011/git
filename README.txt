Git: Hoch- und Runterladen

1 Änderungen hochladen (Push)
Wenn du etwas geändert hast und es auf GitHub speichern willst:

cd "Pfad\zu\deinem\Projekt"   # In den Projektordner wechseln
git add .                      # Alle Änderungen vormerken
git commit -m "Beschreibung"   # Änderungen lokal speichern 
git push                       # Änderungen auf GitHub hochladen


Beispiel:

git add README.txt
git commit -m "Textdatei aktualisiert" wichtig damit die änderung auch wirklich verschickt wird
git push


2️ Änderungen herunterladen (Pull)
Wenn andere etwas geändert haben oder du auf einem anderen PC weiterarbeitest:

cd "Pfad\zu\deinem\Projekt"
git pull                       # Alle neuen Änderungen von GitHub herunterladen


Kurzversion:

Hochladen: git add . → git commit -m "..." → git push

Runterladen: git pull