# Pixel Binning — README

## Descrizione
Implementazione dell'algoritmo di pixel binning in C++ con OpenMP.
Il programma riduce la risoluzione di un'immagine JPEG calcolando la media
di blocchi di pixel adiacenti (bin_factor x bin_factor).

Sono presenti due versioni:
- `binning_sequenziale.cpp` — versione single-thread
- `binning_parallelo.cpp`   — versione parallelizzata con OpenMP (static/dynamic/guided, con e senza collapse)

---


## File inclusi

| File                        | Descrizione                                      |
|-----------------------------|--------------------------------------------------|
| `binning_sequenziale.cpp`   | Codice sorgente versione sequenziale             |
| `binning_parallelo.cpp`     | Codice sorgente versione parallela (OpenMP)      |
| `stb_image.h`               | Libreria per il caricamento di immagini JPEG     |
| `stb_image_write.h`         | Libreria per la scrittura di immagini JPEG       |
| `elaborazione.py`           | Script Python per calcolo speedup ed efficienza  |
| `makefile`                  | Script di compilazione e benchmark               |
| `Report_progetto_1_informatica.pdf` | Report completo del progetto            |

### File di input
I programmi si aspettano un file immagine chiamato **`input.jpg`** nella stessa cartella.

> ⚠️ I file di input usati per i benchmark sono inclusi ma vanno rinominati a turno per eseguire il codice sul file corretto. Altrimenti è sufficiente rinominare qualsiasi immagine JPEG
> rinominare come `input.jpg` per eseguire il codice.

---

## Compilazione

```bash
make
elaborazione per avere i grafici della singola run