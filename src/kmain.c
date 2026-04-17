#include <stdbool.h>
#include <limine.h>
#include <stddef.h>
#include <stdint.h>
#include "boot.h"
#include "utils/string.h"

static void hcf(void) {
    for (;;) {
        asm("hlt");
    }
}

void init_term(struct limine_framebuffer *fb);
void term_write(const char *s);

void kmain(){
    if (framebuffer_request.response == NULL || framebuffer_request.response->framebuffer_count < 1){
        while (1) {__asm__("hlt");}
    }

    struct limine_framebuffer *fb = framebuffer_request.response->framebuffers[0];
    init_term(fb);
    term_write("Welcome to cccoreOS!\n");
    term_write("*Proccessor now in hlt mode!");
    hcf();
}