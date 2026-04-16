CC=x86_64-elf-gcc
LD=x86_64-elf-ld

CFLAGS=-I src \
	-Wall -Wextra -std=gnu99 \
	-nostdlib -ffreestanding \
	-fno-stack-protector -fno-stack-check \
	-fno-PIC -ffunction-sections -fdata-sections

LDFLAGS=-T linker.ld

KERNEL=kernel
ISO=kernel.iso
OBJ=*.o

all: build

build:
	rm -rf $(OBJ)
	$(CC) -c $(CFLAGS) src/kmain.c -o kmain.o
	$(LD) -o $(KERNEL) $(LDFLAGS) *.o

limine/limine:
	git clone https://github.com/limine-bootloader/limine.git --branch=v9.x-binary --depth=1
	$(MAKE) -C limine

build-iso: limine/limine build
	rm -rf iso_root
	mkdir -p iso_root/boot
	mkdir -p iso_root/boot/limine
	mkdir -p iso_root/EFI/BOOT

	cp -v $(KERNEL) iso_root/boot/
	cp -v limine.conf iso_root/boot/limine/

	cp -v limine/limine-bios.sys iso_root/boot/limine/
	cp -v limine/limine-bios-cd.bin iso_root/boot/limine/
	cp -v limine/limine-uefi-cd.bin iso_root/boot/limine/

	cp -v limine/BOOTX64.EFI iso_root/EFI/BOOT/
	cp -v limine/BOOTIA32.EFI iso_root/EFI/BOOT/

	xorriso -as mkisofs -R -r -J \
		-b boot/limine/limine-bios-cd.bin \
		-no-emul-boot -boot-load-size 4 -boot-info-table \
		-hfsplus -apm-block-size 2048 \
		--efi-boot boot/limine/limine-uefi-cd.bin \
		-efi-boot-part --efi-boot-image \
		--protective-msdos-label \
		iso_root -o $(ISO)

	./limine/limine bios-install $(ISO)

clean:
	rm -rf *.o $(KERNEL) iso_root $(ISO) limine