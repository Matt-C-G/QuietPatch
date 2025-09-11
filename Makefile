# ===== QuietPatch Makefile =====
VERSION ?= 0.4.0
TAG := v$(VERSION)
REPO ?= Matt-C-G/QuietPatch
DIST := dist
REL := release

.PHONY: all clean build package checksums sign release

all: clean build package checksums

clean:
	rm -rf $(DIST) $(REL) AppDir || true

build:
	pyinstaller build/quietpatch_wizard.spec
	pyinstaller build/quietpatch_cli.spec

package: package-win package-mac package-linux
	@echo "Packaging complete"

package-win:
	mkdir -p $(REL)
	# Inno Setup must be installed; path may differ.
	"C:/Program Files (x86)/Inno Setup 6/ISCC.exe" installer/windows/QuietPatch.iss
	cp Output/QuietPatch-Setup-v$(VERSION).exe $(REL)/ || true
	cd dist && 7z a ../$(REL)/quietpatch-cli-v$(VERSION)-win64.zip quietpatch/*

package-mac:
	mkdir -p $(REL) dist/macos
	create-dmg --volname "QuietPatch v$(VERSION)" --window-size 600 400 \
	  --icon-size 100 --app-drop-link 450 200 \
	  dist/macos/QuietPatch-v$(VERSION).dmg dist/macos/ || true
	cp dist/macos/QuietPatch-v$(VERSION).dmg $(REL)/ || true
	cd dist && tar -czf ../$(REL)/quietpatch-cli-v$(VERSION)-macos-universal.tar.gz quietpatch

package-linux:
	mkdir -p $(REL) AppDir/usr/bin
	cp dist/QuietPatchWizard AppDir/usr/bin/QuietPatch
	printf "[Desktop Entry]
Type=Application
Name=QuietPatch
Exec=QuietPatch
Icon=QuietPatch
Categories=Utility;System;
" > AppDir/QuietPatch.desktop
	cp assets/QuietPatch.png AppDir/QuietPatch.png || true
	appimagetool AppDir QuietPatch-v$(VERSION)-x86_64.AppImage
	mv QuietPatch-v$(VERSION)-x86_64.AppImage $(REL)/
	cd dist && tar -czf ../$(REL)/quietpatch-cli-v$(VERSION)-linux-x86_64.tar.gz quietpatch

checksums:
	cd $(REL) && (command -v sha256sum >/dev/null && sha256sum * || shasum -a 256 *) > SHA256SUMS.txt

sign:
	# Requires MINISIGN_SECRET_KEY pointing to your secret key file
	cd $(REL) && minisign -Sm SHA256SUMS.txt -s $$MINISIGN_SECRET_KEY

release: all sign
	gh release create $(TAG) $(REL)/* -t "QuietPatch $(TAG)" -n "Download-ready release"