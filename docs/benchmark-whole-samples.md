# Whole-sample benchmark: Tachyon 0.4.1 against STAR 2.7.11b

This page records the author's benchmark of the Tachyon 0.4.1 release against STAR 2.7.11b on eight complete human RNA-seq samples. The author ran the tests; there has been no independent validation.

## Result

| Sample | SRA run | Size | Reads | STAR 2.7.11b | Tachyon 0.4.1 | Faster by |
|---|---|---:|---:|---:|---:|---:|
| HCC1395 breast cancer cell line | SRR892393 | 156.2 M pairs | 2x100 | 18.0 min | 7.4 min | 2.4x |
| Breast tumour, FFPE | SRR7095518 | 98.7 M reads | 1x61 | 3.9 min | 1.6 min | 2.5x |
| VCaP prostate cancer cell line | SRR10913248 | 35.2 M pairs | 2x75 | 3.3 min | 1.3 min | 2.5x |
| K562 leukaemia cell line | DRR326757 | 23.9 M pairs | 2x150 | 3.8 min | 1.2 min | 3.3x |
| Colorectal tumour | SRR975561 | 23.2 M pairs | 2x101 | 3.4 min | 1.2 min | 2.7x |
| Pancreatic tumour, FFPE | SRR15319201 | 20.5 M pairs | 2x149 | 7.4 min | 2.5 min | 3.0x |
| SK-BR-3 breast cancer cell line | SRR064440 | 9.0 M pairs | 2x50 | 1.2 min | 0.3 min | 3.8x |
| MCF-7 breast cancer cell line | SRR064286 | 8.4 M pairs | 2x50 | 1.2 min | 0.3 min | 4.1x |
| **All 8 samples** | | **375 M** | | **42.2 min** | **15.7 min** | **2.7x** |

The speed-up is smallest on the largest sample (HCC1395, 2.4x) and largest on the short 2x50 reads (MCF-7 and SK-BR-3, about 4x).

## Input and hardware

Every sample is a whole sequencing run, downloaded from the public archives and used as it is: no subsetting, no filtering. Seven samples are paired-end; the FFPE breast tumour is single-end. Read counts are those reported by both programs in `Log.final.out`.

The genome index is the whole human genome: Ensembl GRCh38 primary assembly with the Ensembl release 115 annotation, `--sjdbOverhang 149`, `--genomeSAindexNbases 14`, `--genomeSAsparseD 1`. It was built once with STAR 2.7.11b and used unchanged by both programs.

The machine was a Google Cloud c2d-standard-32 VM (AMD EPYC 7B13, 32 vCPUs, 126 GB RAM), on demand, not Spot. Each run used 16 threads pinned to CPUs 0-15. The runs were made on 3 November 2026.

## Versions and settings

STAR was the official 2.7.11b, commit `b1edc1208d91a53bf40ebae8669f71d50b994851`. Tachyon was the 0.4.1 release binary, with its default settings. The two programs used exactly the same options:

```text
--runThreadN 16 --genomeDir /path/to/index
--readFilesIn reads_1.fastq.gz reads_2.fastq.gz --readFilesCommand zcat
--outSAMtype BAM SortedByCoordinate --limitBAMsortRAM 20000000000
--outSAMattributes NH HI AS nM --outSAMunmapped Within
--quantMode GeneCounts --genomeLoad NoSharedMemory --runRNGseed 777
```

## How the time was measured

The time is the wall-clock time of the whole run, from start to exit: reading and decompressing the FASTQ files, loading the index, aligning, counting genes and writing the coordinate-sorted BAM. Index generation is not included. For Tachyon the time is the median of 2 runs; STAR was run once per sample, because each STAR run takes up to 18 minutes. The two Tachyon runs of each sample differed by at most 7.4%.

## Identity with STAR

Each of the 16 Tachyon runs was compared with the STAR run on the same sample: BAM alignment records (decoded, so independent of compression), BAM header without the `@PG` line, `ReadsPerGene.out.tab`, `SJ.out.tab` and `Log.final.out` without dates and speeds. All 16 were identical. The comparison covers these outputs and options only; chimeric, transcriptome and STARsolo outputs were not part of this benchmark.

## Limitations

- One machine type and one thread count. On other processors, disks and thread counts the speed-up can be different.
- Eight human samples. Other organisms, read lengths and library types were tested by the author in separate runs not reported on this page.
- STAR was timed once per sample, Tachyon twice.
- Before relying on Tachyon, compare it with STAR 2.7.11b on a sample of your own data, with your own options.
