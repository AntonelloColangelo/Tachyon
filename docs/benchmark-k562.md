# K562 benchmark: historical Tachyon 0.4 comparison

This page records the author's benchmark against STAR 2.7.11b. It describes a historical Tachyon 0.4 build, not a direct benchmark of Tachyon 0.4.1. The author ran the tests; there has been no independent validation.

## Input and hardware

The dataset was ENCODE K562 poly(A)+ paired-end RNA-seq, experiment [ENCSR000AEM](https://www.encodeproject.org/experiments/ENCSR000AEM/), replicate 1, SRA run SRR3192408. The test used the first 5,000,000 read pairs of the two FASTQ files [ENCFF001RED](https://www.encodeproject.org/files/ENCFF001RED/) and [ENCFF001RDZ](https://www.encodeproject.org/files/ENCFF001RDZ/). These reads come from the beginning of the sequencing run and may not represent the whole sample. The recorded MD5 checksums for the complete ENCODE source files were `0e88b38c8d48806ee98929a5bad06fc4` (ENCFF001RED) and `3a25713488522b0ea8a4d9635b5afa41` (ENCFF001RDZ); these are not checksums of the 5-million-pair subsets.

The index used GRCh38 primary assembly, Ensembl release 115 annotation, `--sjdbOverhang 149`, and `--genomeSAindexNbases 14`. The machine was a Google Cloud c2d-standard-32 VM with an AMD EPYC 7B13 processor, 32 vCPUs and 128 GB RAM. The runs used 16 threads pinned to 16 physical cores. The test was single-pass, with FASTQ decompression, coordinate-sorted BAM and transcriptome BAM output; index preparation and the separate TK-table construction were outside the measured time.

The index-generation log recorded the following command, with local paths replaced by placeholders:

```bash
STAR --runMode genomeGenerate --runThreadN 8 \
  --genomeDir /path/to/index \
  --genomeFastaFiles /path/to/Homo_sapiens.GRCh38.dna.primary_assembly.fa \
  --sjdbGTFfile /path/to/Homo_sapiens.GRCh38.115.gtf \
  --sjdbOverhang 149 --genomeSAindexNbases 14 --genomeSAsparseD 1 \
  --outFileNamePrefix /path/to/index/
```

## Versions and settings

STAR was 2.7.11b, commit `b1edc1208d91a53bf40ebae8669f71d50b994851`, using `--genomeLoad NoSharedMemory`. Tachyon was the historical 0.4 build using `--genomeLoad Mmap` and a prebuilt auxiliary index table of approximately 4 GiB.
The shared alignment options were:

```text
--outSAMunmapped Within --outFilterType BySJout
--outSAMattributes NH HI AS NM MD --outFilterMultimapNmax 20
--outFilterMismatchNmax 999 --outFilterMismatchNoverReadLmax 0.04
--alignIntronMin 20 --alignIntronMax 1000000 --alignMatesGapMax 1000000
--alignSJoverhangMin 8 --alignSJDBoverhangMin 1 --sjdbScore 1
--readFilesCommand zcat --runThreadN 16 --limitBAMsortRAM 10000000000
--outSAMtype BAM SortedByCoordinate --quantMode TranscriptomeSAM
--outSAMheaderHD @HD VN:1.4 SO:coordinate
```

Both commands also used the same index, FASTQ inputs and ENCODE-style BAM header-comment file. The index differed from the original ENCODE pipeline reference: the test used Ensembl 115 and `sjdbOverhang 149`, rather than ENCODE's GENCODE annotation and `sjdbOverhang 100`.

## Measurements

The STAR reference runs were performed earlier on the same VM and reused; a sentinel run checked machine drift. The Tachyon runs used a verified warm cache. Warm cache for the historical STAR reference was inferred from its index-loading time rather than directly recorded. Each version has two valid measured runs:

| Program | Run | Wall time (s) | Peak RSS (KiB) |
| --- | --- | ---: | ---: |
| STAR 2.7.11b | 1 | 112.89 | 34,520,300 |
| STAR 2.7.11b | 2 | 114.29 | 34,520,088 |
| Tachyon 0.4 | 1 | 24.35 | 39,424,880 |
| Tachyon 0.4 | 2 | 24.34 | 39,481,248 |

Median elapsed times are 113.59 and 24.345 seconds; throughput in the README is 5,000,000 pairs divided by those medians. The median peak RSS values are 32.92 and 37.63 GiB. RSS includes resident file-backed index pages. The reported peak anonymous-memory medians were 32.87 and 5.05 GiB; anonymous memory alone is not a measure of total RAM needed for the run. The different genome-loading modes and the extra prebuilt table are part of the comparison.

## Output comparison

For the 5-million-pair runs, the recorded fingerprints of the genomic alignment records and splice-junction output matched the reference in both Tachyon repetitions. Fingerprint matches are reported as such; the test did not record an individual per-alignment concordance percentage.

In a separate 500,000-pair K562 test at 32 threads, the full comparator reported 1,689,542 matching decoded genomic BAM records and identical `SJ.out.tab` files containing 76,736 lines. It compared sorted decoded records and ignored the expected `@PG` and `@CO` header differences. Transcriptome BAM comparison was separate: records matched after excluding the primary-alignment flag bit, whose selection can vary across multithreaded STAR runs.

These checks cover the reported inputs and settings, not every STAR mode, platform or dataset. Compressed BAM bytes, checksums and the order of records at the same coordinate can differ.

## Reproduction status

The public ENCODE files, versions, hardware class and principal options above allow a comparable new experiment. Complete SHA-256 hashes of the historical FASTQ subsets were not recorded for the reused STAR reference, and the benchmark harness and reference-input hashes are not published here. Therefore the historical run is not yet independently reproducible byte for byte. A new run should retain the FASTQ and index hashes, full command lines, binary hashes, per-run timings and memory measurements, comparator, and raw outputs; it should report cold- and warm-cache behavior separately.

Use of the Tachyon executable is governed by the [license](../LICENSE) and [README](../README.md) for current installation and validation guidance.
