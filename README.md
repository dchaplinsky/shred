shred
=====

Simple tool to generate ground truth dataset for [unshred](https://github.com/dchaplinsky/unshred) project.

It takes bunch of scanned documents, dozen of read shreds mask and producing as many realisticly looking shreds
as you want, cut under random position and angle.

This shreds can be then used to test features detectors (think base line angle detection, lines fragment detection)
of unshred project.

### Requirements
In addition to stuff from requirements.txt script also relies on OpenCV (2.4.9+)
Use your package manager to get a copy

### Acknowledgments
Dear @xa4a and @fednep, this little script is for you :)