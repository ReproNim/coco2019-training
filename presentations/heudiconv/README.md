# [Click to visit](https://mgxd.github.io/)

# Prerequisites
* `docker pull nipype/workshops:latest-base`
* `docker pull nipy/heudiconv`
* `jupyter notebook` (for nice viewing)


```
$ docker run -it --rm -v $PWD:/data nipype/workshops:latest-base bash
# Inside container
> git clone http://datasets.datalad.org/test/dartmouth-siemens/PHANTOM1_3/.git
> cd PHANTOM1_3
> datalad get -J6 YAROSLAV_DBIC-TEST1/
> exit
```
