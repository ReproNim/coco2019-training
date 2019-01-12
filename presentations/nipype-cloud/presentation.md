class: center middle

# Nipype and plugins

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
datalad get ds000001/sub-*/*/*T1w*  # fetch all T1s
curl -qO https://raw.githubusercontent.com/mgxd/coco2019-training/gh-pages/presentations/nipype-cloud/sample_workflow.py
```

---
## The Power of MultiProc
