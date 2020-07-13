# Neuropsikiatri: Deteksi gangguan motorik halus pada pasien skizofrenia

Aplikasi ini dibuat untuk mendukung riset "Neuropsikiatri: Deteksi gangguan motorik halus pada pasien skizofrenia". Dalam repository ini terdapat Legacy Code untuk software yang pernah dikembangkan sebelumnya.

```
...
neuropsikiatri-deteksi-gangguan-motorik-halus-pada-pasien-skizofrenia  
-- Legacy Code/1D tracking task original code
-- src
-- tests
...
```

## Pre-instalasi

Untuk melakukan instalasi dibutuhkan ``Python 3.x``. Sebelum melakukan instalasi, direkomendasikan untuk membuat local virtual environment terlebih dahulu.

```bash
python3 -m venv env
```
Untuk memasuki local virtual environment di linux

```bash
source env/bin/activate
```

Untuk memasuki local virtual environment di windows

```bash
\env\Scripts\activate.bat
```

## Instalasi

Untuk menjalankan proyek, perlu melakukan instalasi requirements modul/library terlebih dahulu. Pastikan sudah ada file ``requirements.txt`` dalam proyek

```bash
pip instal -r requirements.txt
```

## Usage

Untuk melakukan unit testing:

```bash
pytest [test_dir|*optional] [src_dir|*optional]
```
Untuk melakukan linter testing:

```bash
pylint [src_dir|*optional]
```
Untuk mengubah source test untuk linter bisa dengan mengubah file ``pytest.ini``
