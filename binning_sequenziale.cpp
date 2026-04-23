#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#include <iostream>
#include <omp.h>

int main() {
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

int bin_factor = 4;
int new_width = width / bin_factor;
int new_height = height / bin_factor;
unsigned char* output = new unsigned char[new_width * new_height * channels];
/*fine allocazione e inizializzazione, inizio codice binning da rivedere*/
double t1, t2;
t1= omp_get_wtime();
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
t2= omp_get_wtime();
std::cout << "Tempo binning: " << (t2 - t1) << " secondi\n";

/*stampo nuova immagine*/
stbi_write_jpg("output.jpg", new_width, new_height, channels, output, 100);


/*libero memoria*/
stbi_image_free(immagine);
delete[] output;
return 0;
}
