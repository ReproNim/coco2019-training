class: center middle

# Nipype and plugins

#### CoCo 2019

---
name: footer
layout: true

<div class="slide-slug">Coastal Coding - Miami, FL - Jan 2019</div>
---

## Diversity in running workflows

- `Nipype` supports a plugin architecture for running workflows


  - These support both local and distributed execution


- MultiProc, SGE, PBS, HTCondor, LSF, OAR, and SLURM


- Factor in pros/cons

---

## Setup

```shell

# spin up a docker image and start in home directory
docker run --rm -it -w /home/neuro kaczmarj/coco2019:day1

# and set up some git credentials
git config --global user.name "nipyper"
git config --global user.email "pyper@ni"

# install an openneuro dataset
datalad install ///openneuro/ds000001
# and fetch all T1s
datalad get ds000001/sub-*/*/*T1w*

# download a test workflow
curl -qO https://raw.githubusercontent.com/mgxd/coco2019-training/gh-pages/presentations/nipype-cloud/sample_workflow.py

# look at the workflow in detail
cat sample_workflow.py

# and then run it!
python sample_workflow.py
```

---

## Good, not great

- There is a bottleneck in execution - only one subject's T1 is processed at a time.

---

## Good, not great

- There is a bottleneck in execution - only one subject's T1 is processed at a time.

- There's a plugin for that: `MultiProc`

- First, let's remove our previous conversion to avoid caching:
```shell
rm -r ~/map-wf
```
- Now, rerun the script with an added flag `-p MultiProc` That will add the following line to
the script
```python
# will make life much faster
wf.run(plugin='MultiProc')
```

---

## From local to cloud

- For bigger workflows (increased # nodes, large amount of subjects), you may want to try running
 on some form of "cloud" - whether it's your lab/institutional HPC *(High Performance Cluster)* or
 some commercial service (Amazon EC2, Google Cloud Platform)

- Many HPC resource managers (SLURM, SGE) have `Nipype` plugins, which can be used to
distribute your workflow across many computers.

- Let's see how submission through SLURM goes
---

## Future Plans

- **Pydra** aims to include support for:

  - Containers (Docker, Singularity)

  - Compute Cloud (AWS, GCP, Azure)
