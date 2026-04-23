
/*AGGIUNGI TEST PER COLLAPSE*/
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image.h"
#include "stb_image_write.h"
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <omp.h>

void binning_no_collapse(const unsigned char* immagine, unsigned char* output,
                         int width, int height, int channels, int bin_factor) {
    int new_width = width / bin_factor;
    int new_height = height / bin_factor;

#pragma omp parallel for schedule(runtime)
    for (int ny = 0; ny < new_height; ny++) {
        for (int nx = 0; nx < new_width; nx++) {
            for (int c = 0; c < channels; c++) {
                int sum = 0;
                for (int dy = 0; dy < bin_factor; dy++) {
                    for (int dx = 0; dx < bin_factor; dx++) {
                        int orig_x = nx * bin_factor + dx;
                        int orig_y = ny * bin_factor + dy;
                        int orig_idx = (orig_y * width + orig_x) * channels + c;
                        sum += immagine[orig_idx];
                    }
                }
                int out_idx = (ny * new_width + nx) * channels + c;
                output[out_idx] = (unsigned char)(sum / (bin_factor * bin_factor));
            }
        }
    }
}

void binning_with_collapse(const unsigned char* immagine, unsigned char* output,
                           int width, int height, int channels, int bin_factor) {
    int new_width = width / bin_factor;
    int new_height = height / bin_factor;

#pragma omp parallel for schedule(runtime) collapse(2)
    for (int ny = 0; ny < new_height; ny++) {
        for (int nx = 0; nx < new_width; nx++) {
            for (int c = 0; c < channels; c++) {
                int sum = 0;
                for (int dy = 0; dy < bin_factor; dy++) {
                    for (int dx = 0; dx < bin_factor; dx++) {
                        int orig_x = nx * bin_factor + dx;
                        int orig_y = ny * bin_factor + dy;
                        int orig_idx = (orig_y * width + orig_x) * channels + c;
                        sum += immagine[orig_idx];
                    }
                }
                int out_idx = (ny * new_width + nx) * channels + c;
                output[out_idx] = (unsigned char)(sum / (bin_factor * bin_factor));
            }
        }
    }
}

int main(int argc, char* argv[]) {
int width, height, channels;
/*caricamento immagine*/
unsigned char* immagine = stbi_load("input.jpg", &width, &height, &channels, 0);
if (immagine == nullptr) {
    std::cerr << "Errore: impossibile caricare l'immagine\n";
    return 1;}
else {
    std::cout << "Immagine caricata: " << width << "x" << height << ", canali: " << channels << std::endl;
}

/*binning*/

int bin_factor = 4; // esempio di fattore di binning
int new_width = width / bin_factor;
int new_height = height / bin_factor;
unsigned char* output = new unsigned char[new_width * new_height * channels];
/*fine allocazione e inizializzazione*/

const char* mode = (argc > 1) ? argv[1] : std::getenv("BINNING_MODE");
bool use_collapse = (mode != nullptr && std::strcmp(mode, "collapse") == 0);

std::cout << "Modalita binning: " << (use_collapse ? "collapse(2)" : "no collapse") << std::endl;

double t1, t2;
if (use_collapse) {
     t1 = omp_get_wtime();
    binning_with_collapse(immagine, output, width, height, channels, bin_factor);
} else {
     t1 = omp_get_wtime();
    binning_no_collapse(immagine, output, width, height, channels, bin_factor);
}
 t2 = omp_get_wtime();
/*binning finito*/
/*stampo nuova immagine*/

stbi_write_jpg("output.jpg", new_width, new_height, channels, output, 100);

/*libero memoria*/
stbi_image_free(immagine);
delete[] output;

std::cout<< "Tempo di esecuzione del binning: " << (t2 - t1) << " secondi"<<std::endl<<std::endl;


return 0;
}
