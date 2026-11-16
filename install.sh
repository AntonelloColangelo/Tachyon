#!/bin/bash
## TACHYON INSTALLER
# Checks this computer, downloads the latest Tachyon release, verifies it and installs the "Tachyon" command.
# Use:   curl -fsSL https://raw.githubusercontent.com/AntonelloColangelo/Tachyon/tachyon-0.4.1/install.sh | bash
#        (or, from a copy of this file:   bash install.sh)
# It needs no GitHub account and no GitHub CLI.
# It installs into ~/.local/bin and needs no administrator rights.
# Another folder:   TACHYON_PREFIX=/some/folder bash install.sh   (the command goes into /some/folder/bin)
# Run it again at any time: it replaces the installed copy with the latest release.

REPO=AntonelloColangelo/Tachyon
PREFIX=${TACHYON_PREFIX:-$HOME/.local}

## 1. THIS COMPUTER

# Tachyon runs on 64-bit Linux
if [ "$(uname -s)" != "Linux" ] || [ "$(uname -m)" != "x86_64" ]; then
    echo "STOP: Tachyon needs 64-bit Linux on an x86-64 processor. This computer is: $(uname -s) $(uname -m)."
    exit 1
fi

# the processor must support AVX2 (Intel Haswell or newer, AMD Zen or newer)
if ! grep -q -w avx2 /proc/cpuinfo; then
    echo "STOP: this processor does not support AVX2, which Tachyon needs."
    exit 1
fi

## 2. TOOLS AND ACCESS

# curl, tar and sha256sum
for TOOL in curl tar sha256sum; do
    if ! command -v $TOOL > /dev/null; then
        echo "STOP: the command '$TOOL' is missing. Install it, then run this installer again."
        exit 1
    fi
done

# name of the latest release (the repository and its releases are public)
TAG=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" < /dev/null 2> /dev/null | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | head -n 1)
if [ -z "$TAG" ]; then
    echo "STOP: cannot read the latest Tachyon release from github.com/$REPO. Check the network and run this installer again."
    exit 1
fi
echo "Latest release: $TAG"

## 3. DOWNLOAD AND VERIFY

WORK=$(mktemp -d)
cd "$WORK" || exit 1

# the program and its checksums
BASE="https://github.com/$REPO/releases/download/$TAG"
ARCHIVE="tachyon-${TAG#tachyon-}-linux-x86_64.tar.gz"
if ! curl -fsSL -O "$BASE/$ARCHIVE" -O "$BASE/SHA256SUMS" < /dev/null; then
    echo "STOP: the download failed. Check the network and run this installer again."
    exit 1
fi

tar xzf tachyon-*-linux-x86_64.tar.gz

# archive and program must match the published checksums
if ! sha256sum --check --quiet SHA256SUMS; then
    echo "STOP: the downloaded files do not match their checksums. Nothing was installed. Run this installer again."
    exit 1
fi
echo "Checksums: OK"

## 4. INSTALL

mkdir -p "$PREFIX/bin"
if ! install -m 755 tachyon-*-linux-x86_64/Tachyon "$PREFIX/bin/Tachyon"; then
    echo "STOP: cannot write into $PREFIX/bin. Choose another folder: TACHYON_PREFIX=/some/folder bash install.sh"
    exit 1
fi

# licence and notices next to the program
mkdir -p "$PREFIX/share/tachyon"
cp tachyon-*-linux-x86_64/LICENSE tachyon-*-linux-x86_64/THIRD_PARTY_NOTICES.md tachyon-*-linux-x86_64/CHANGES.md "$PREFIX/share/tachyon/" 2> /dev/null

cd /
rm -r "$WORK"

## 5. CHECK THAT IT RUNS

if ! "$PREFIX/bin/Tachyon" --version > /dev/null; then
    echo "STOP: Tachyon was copied to $PREFIX/bin but does not start on this computer."
    exit 1
fi
echo
"$PREFIX/bin/Tachyon" --version

# the folder must be in the PATH, so that typing Tachyon is enough
case ":$PATH:" in
    *":$PREFIX/bin:"*)
        READY="Tachyon is ready. Type: Tachyon --version"
        ;;
    *)
        # default folder: add it to the PATH of new terminals
        if [ "$PREFIX" = "$HOME/.local" ] && ! grep -q 'HOME/.local/bin' "$HOME/.bashrc" 2> /dev/null; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        fi
        READY="Tachyon is ready. Open a new terminal, or run this line now:  export PATH=\"$PREFIX/bin:\$PATH\""
        ;;
esac

echo
echo "Installed: $PREFIX/bin/Tachyon"
echo "$READY"
echo
echo "How to use it: write Tachyon where you would write STAR, with the same options. Example:"
echo "  Tachyon --runThreadN 8 --genomeDir /path/to/index --readFilesIn reads_1.fastq.gz reads_2.fastq.gz --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate"
echo "Tachyon is free for individual, non-commercial use; other uses need a license from the author (see $PREFIX/share/tachyon/LICENSE)."
