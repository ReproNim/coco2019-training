class: center middle

# Nipype in the Cloud

#### CoCo 2019

---
## Roadmap

- Start with example of workflow taking too long (mapnodes, iterables??)
- Change to use MultiProc and observe the speed up
- Discuss plugins and how they can affect Nipype workflows (SLURM, SGE, etc)
- Can take advantage of plugins anywhere - HPC, AWS, etc

---
##

```shell
cd  # work in /home directory
# git credentials
git config --global user.name "nipyper"
git config --global user.name "pyper@ni"
datalad install ///openneuro/ds000001  # make dataset paths
datalad get ds000001/sub-0[1-5]/*/*T1w*  # fetch first 5 T1s
curl -O 
```

---
## The Power of MultiProc
