# Compilatore (usa g++ di MinGW-w64)
CXX = g++

# Flags: 
# -O3: Ottimizzazione massima (fondamentale per le immagini)
# -fopenmp: Abilita il parallelismo (OpenMP)
# -Wall: Mostra tutti i warning
CXXFLAGS = -std=c++17 -O3 -fopenmp -Wall

# Nome dell'eseguibile
PARALLEL_ESE = binning_parallelo.exe
SEQUENTIAL_ESE = binning_sequenziale.exe
# File sorgente
SRCS_PARA = binning_parallelo.cpp
SRCS_SEQU = binning_sequenziale.cpp

# Output benchmark
CSV ?= benchmark_results.csv
PLOT ?= benchmark_plot.png


PYTHON ?= python3

# Modalita binning: nocollapse | collapse
MODE ?= nocollapse


# Regola di default
all: $(PARALLEL_ESE) $(SEQUENTIAL_ESE)

# Compilazione
$(PARALLEL_ESE): $(SRCS_PARA)
	$(CXX) $(CXXFLAGS) $(SRCS_PARA) -o $(PARALLEL_ESE)

$(SEQUENTIAL_ESE): $(SRCS_SEQU)
	$(CXX) $(CXXFLAGS) $(SRCS_SEQU) -o $(SEQUENTIAL_ESE)

# Pulizia
clean:
	del $(PARALLEL_ESE)
	del $(SEQUENTIAL_ESE)
	del $(CSV)
	del $(PLOT)

# Compila ed esegue
run: $(PARALLEL_ESE)
	./$(PARALLEL_ESE) $(MODE)

# Esegue benchmark per vari numeri di thread e scheduler

test: $(PARALLEL_ESE) $(SEQUENTIAL_ESE)
	@echo "mode,scheduler,threads,time_seconds,width,height" > $(CSV)
	@output_sequenziale=$$(./$(SEQUENTIAL_ESE) 2>&1 | tee /dev/stderr); \
		time_sequenziale=$$(printf '%s\n' "$$output_sequenziale" | sed -nE 's/.*Tempo binning: ([0-9.]+) secondi.*/\1/p' | head -n 1); \
		seq_width=$$(printf '%s\n' "$$output_sequenziale" | sed -nE 's/.*Immagine caricata: ([0-9]+)x([0-9]+), canali: ([0-9]+).*/\1/p' | head -n 1); \
		seq_height=$$(printf '%s\n' "$$output_sequenziale" | sed -nE 's/.*Immagine caricata: ([0-9]+)x([0-9]+), canali: ([0-9]+).*/\2/p' | head -n 1); \
		echo "sequenziale,none,1,$$time_sequenziale,$$seq_width,$$seq_height" >> $(CSV)



		
	@for m in nocollapse collapse; do \
		for s in static dynamic guided; do \
			for t in 2 4 8 16 32 64 128 ; do \
				echo "Test mode=$$m, scheduler=$$s, thread=$$t"; \
				output=$$(OMP_NUM_THREADS=$$t OMP_SCHEDULE=$$s ./$(PARALLEL_ESE) $$m 2>&1 | tee /dev/stderr); \
				tempo=$$(printf '%s\n' "$$output" | sed -nE 's/.*Tempo di esecuzione del binning: ([0-9.]+) secondi.*/\1/p' | head -n 1); \
				width=$$(printf '%s\n' "$$output" | sed -nE 's/.*Immagine caricata: ([0-9]+)x([0-9]+), canali: ([0-9]+).*/\1/p' | head -n 1); \
				height=$$(printf '%s\n' "$$output" | sed -nE 's/.*Immagine caricata: ([0-9]+)x([0-9]+), canali: ([0-9]+).*/\2/p' | head -n 1); \
				echo "$$m,$$s,$$t,$$tempo,$$width,$$height" >> $(CSV); \
			done; \
		done; \
	done
	@echo "CSV benchmark salvato in $(CSV)"
	$(PYTHON) "elaborazione.py" "$(CSV)"
elaborazione:
	$(PYTHON) "elaborazione.py" "$(CSV)"
