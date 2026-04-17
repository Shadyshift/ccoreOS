import os
import sys
import shutil
if shutil.which("x86_64-elf-gcc"):
    CC = "x86_64-elf-gcc"
    LD = "x86_64-elf-ld"
else:
    CC = "gcc"
    LD = "ld"

CFLAGS = (
    "-I src "
    "-I src/term/flanterm/src "
    "-I src/term "
    "-Wall -Wextra -std=gnu99 "
    "-ffreestanding -nostdlib "
    "-fno-stack-protector -fno-stack-check -fno-PIC "
    "-ffunction-sections -fdata-sections "
    "-m64 -mcmodel=kernel -mno-red-zone"
)
LDFLAGS = "-T linker.ld -m elf_x86_64 -nostdlib"

SOURCES = [
    "src/boot.c",
    "src/kmain.c",
    "src/term/term.c",
    "src/utils/string.c",
    "src/term/flanterm/src/flanterm.c",
    "src/term/flanterm/src/flanterm_backends/fb.c"
]

def run(cmd):
    print(cmd)
    ret = os.system(cmd)
    if ret != 0:
        import sys
        print(f"Warning: Command failed with exit code {ret >> 8}", file=sys.stderr)
def run_required(cmd):
    print(cmd)
    if os.system(cmd) != 0:
        sys.exit(1)

def build_kernel():
    print("Building kernel...")

    os.makedirs("build", exist_ok=True)
    objects = []

    for src in SOURCES:
        obj = "build/" + src.replace("/", "_").replace(".c", ".o")
        objects.append(obj)
        run_required(f"{CC} -c {CFLAGS} {src} -o {obj}")

    run_required(f"{LD} {LDFLAGS} -o kernel " + " ".join(objects))

def build_image():
    build_kernel()

    os.makedirs("iso_root/boot/limine", exist_ok=True)
    os.makedirs("iso_root/EFI/BOOT", exist_ok=True)

    run_required("cp kernel iso_root/boot/kernel")
    run_required("cp limine.conf iso_root/boot/limine.conf")

    run_required("cp limine/limine-bios.sys iso_root/boot/limine/")
    run_required("cp limine/limine-bios-cd.bin iso_root/boot/limine/")
    run_required("cp limine/limine-uefi-cd.bin iso_root/boot/limine/")
    run_required("cp limine/BOOTX64.EFI iso_root/EFI/BOOT/")
    run_required("cp limine/BOOTIA32.EFI iso_root/EFI/BOOT/")

    print("Creating ISO image...")
    run(
        "xorriso -as mkisofs -R -r -J "
        "-b boot/limine/limine-bios-cd.bin "
        "-no-emul-boot -boot-load-size 4 -boot-info-table "
        "-hfsplus -apm-block-size 2048 "
        "--efi-boot boot/limine/limine-uefi-cd.bin "
        "-efi-boot-part --efi-boot-image --protective-msdos-label "
        "iso_root -o kernel.iso"
    )

    print("Installing Limine bootloader...")
    run("./limine/limine bios-install kernel.iso")
    
    print("Build complete! Kernel: kernel.elf, ISO: kernel.iso")

def clean():
    os.system("rm -rf build iso_root kernel kernel.iso")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python build.py image|clean")
        sys.exit(1)

    if sys.argv[1] == "image":
        build_image()
    elif sys.argv[1] == "clean":
        clean()