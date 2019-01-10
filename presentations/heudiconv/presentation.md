name: inverse
layout: true
class: center, middle, inverse
---
# Heudiconv
### Coastal Coding 2019

---
layout: false

## Heudi-what?

- `Heudiconv` is a Python library to facilitate conversion of DICOM files to NIfTI.
- Highly customizable, but can be set conform to existing data standards (BIDS).
- Integration with `DataLad` allows for easy versioning and sharing of data!

---
## Tutorial and Requirements

- In this live tutorial, we will be using publicly
 available DICOM data and
 converting with `Heudiconv`. The data comes
 preloaded in the Docker image, but
 can be fetched easily with `DataLad`.

** To ensure you can follow along, please check
 that you have:
* Docker + `mgxd/heudiconv:cc19-demo` image

---
### Setup

- By default, running the container will trigger a
 `heudiconv` build. We will override this and enter
 the container interactively with the following
 command:

```
docker run --rm -it --entrypoint=bash mgxd/heudiconv:cc19-demo
```

- To test you are in the proper environment, try
 running the following commands

```
heudiconv --version;
ls /examples;
```

---
### Usage

Here are a few basic `heudiconv` flags to be familiar with:

* First, pick one of these flags to input data
  - `--files` : Files (tarballs, dicoms) or
   directories containing files to process.
  - `-d, --dicom_dir_template` : string path
   to DICOMs. Requires "{subject}" formatting
   within path.
     - `-s, --subjects` : one or more subjects to
     substitute to path in `--dicom_dir_template`

* `-f, --heuristic` : Python script used to set
  conversion rules.
* `-o, --outdir` : Location to store output

---
### Reproin - for the ~~lazy~~ easy converter

- `Heudiconv` includes a variety of built-in
 heuristics (`heudiconv --command heuristics`)

- The [`reproin`](https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/reproin.py) heuristic is an effort to automate
 DICOM conversions straight to compliant (but not
 complete) BIDS datasets*.
  - Requires scanner sequences to be structured in
   a particular format

---
### Reproin - for the ~~lazy~~ easy converter

- Lets use some data that was already structured in
 the reproin format

 ```bash
 heudiconv --files /examples/phantom-1 -f reproin -o /output --bids
 ```

- Check validity of the conversion
 ```bash
 bids-validator /output/Halchenko/Yarik/950_bids_test4/
 ```

---
### Custom Conversion

- What if you are working with data that was not
 structured to `reproin` on the scanner?

- We'll just have to make our own structure / rules!

- We will run `heudiconv` twice:
  - dry pass (no conversion), which will stack
   and group the DICOMs into series. This step will
   let us view information per series and define
   rules.
   - conversion, as we saw with the `reproin`

---
### Custom Conversion

```bash
heudiconv -d "/examples/{subject}/*/*/*/*IMA" -s PHANTOM1_3 -c none -f convertall -o /output2
```

Run the command!

---
### Sample conversion

- After running the command, there will be a
 hidden folder within output directory to keep track of metadata. `/output/.heudiconv/`.

- Within `.heudiconv`, there will be a directory
 with your subject ID, and a subdirectory `info`. Inside this, you can see a `dicominfo.tsv` - we'll be using the information here to convert to a file structure (BIDS)

- Let's visualize the `dicominfo`.

---
### Dive into a heuristic file

[Link to convert all heuristic](https://raw.githubusercontent.com/mgxd/heudiconv/coco2019/heudiconv/heuristics/convertall.py)

---
### Creating heuristic keys

- Keys define type of scan

- Let's extract T1, diffusion, and rest scans

--

```python
t1w = create_key('sub-{subject}/anat/sub-{subject}_T1w')
```

--

```python
def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """
    # paths done in BIDS format
    t1w = create_key('sub-{subject}/anat/sub-{subject}_T1w')
    dwi = create_key('sub-{subject}/dwi/sub-{subject}_run-{item:01d}_dwi')
    rest = create_key('sub-{subject}/func/sub-{subject}_task-rest_rec-{rec}_run-{item:01d}_bold')

    info = {t1w: [], dwi: [], rest: []}
```
---
### Sequence Info

  - And now for each key, we will look at the `dicominfo.tsv` and set a unique criteria that only that scan will meet.


```python
for idx, s in enumerate(seqinfo):
   # s is a namedtuple with fields equal to the names of the columns
   # found in the dicominfo.txt file
```

---
### Sequence Info

  - And now for each key, we will look at the `dicominfo.tsv` and set a unique criteria that only that scan will meet.


```python
for idx, s in enumerate(seqinfo): # each row of dicominfo.tsv
    if (s.dim3 == 176) and (s.dim4 == 1) and ('t1' in s.protocol_name):
      info[t1w] = [s.series_id] # assign if a single scan meets criteria
```

---
### Handling multiple runs

```python
for idx, s in enumerate(seqinfo): # each row of dicominfo.tsv
    if (s.dim3 == 176) and (s.dim4 == 1) and ('t1' in s.protocol_name):
      info[t1w] = [s.series_id] # assign if a single scan meets criteria
```
--

- Notice there are two diffusion scans shown in DICOM info

---
### Handling multiple runs

```python
for idx, s in enumerate(seqinfo): # each row of dicominfo.tsv
    if (s.dim3 == 176) and (s.dim4 == 1) and ('t1' in s.protocol_name):
      info[t1w] = [s.series_id] # assign if a single scan meets criteria
    if (11 <= s.dim3 <= 22) and (s.dim4 == 1) and ('dti' in s.protocol_name):
      info[dwi].append(s.series_id) # append if multiple scans meet criteria
```

- Notice there are two diffusion scans shown in DICOM info

---
### Using custom formatting conditionally

```python
for idx, s in enumerate(seqinfo): # each row of dicominfo.tsv
    if (s.dim3 == 176) and (s.dim4 == 1) and ('t1' in s.protocol_name):
      info[t1w] = [s.series_id] # assign if a single scan meets criteria
    if (11 <= s.dim3 <= 22) and (s.dim4 == 1) and ('dti' in s.protocol_name):
      info[dwi].append(s.series_id) # append if multiple scans meet criteria
```

--

- Extract and label if resting state scans are not motion corrected

---
### Using custom formatting conditionally

```python
for idx, s in enumerate(seqinfo): # each row of dicominfo.tsv
    if (s.dim3 == 176) and (s.dim4 == 1) and ('t1' in s.protocol_name):
      info[t1w] = [s.series_id] # assign if a single scan meets criteria
    if (11 <= s.dim3 <= 22) and (s.dim4 == 1) and ('dti' in s.protocol_name):
      info[dwi].append(s.series_id) # append if multiple scans meet criteria
    if (s.dim4 > 10) and ('taskrest' in s.protocol_name):
      if not s.is_motion_corrected: # not motion corrected
```

- Extract and label if resting state scans are not motion corrected

---
### Using custom formatting conditionally

```python
for idx, s in enumerate(seqinfo): # each row of dicominfo.tsv
    if (s.dim3 == 176) and (s.dim4 == 1) and ('t1' in s.protocol_name):
      info[t1w] = [s.series_id] # assign if a single scan meets criteria
    if (11 <= s.dim3 <= 22) and (s.dim4 == 1) and ('dti' in s.protocol_name):
      info[dwi].append(s.series_id) # append if multiple scans meet criteria
    if (s.dim4 > 10) and ('taskrest' in s.protocol_name):
      if not s.is_motion_corrected: # not motion corrected
        info[rest].append({'item': s.series_id, 'rec': 'uncorrected'})
```

- Extract and label if resting state scans are not motion corrected

---
### Our finished heuristic (`demo_heuristic.py`)

```python
import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes

def infotodict(seqinfo):

    t1w = create_key('sub-{subject}/anat/sub-{subject}_T1w')
    dwi = create_key('sub-{subject}/dwi/sub-{subject}_run-{item:01d}_dwi')
    rest = create_key('sub-{subject}/func/sub-{subject}_task-rest_rec-{rec}_run-{item:01d}_bold')

    info = {t1w: [], dwi: [], rest: []}

    for s in seqinfo:
        if (s.dim3 == 176) and (s.dim4 == 1) and ('t1' in s.protocol_name):
          info[t1w] = [s.series_id] # assign if a single series meets criteria
        if (11 <= s.dim3 <= 22) and (s.dim4 == 1) and ('dti' in s.protocol_name):
          info[dwi].append(s.series_id) # append if multiple series meet criteria
        if (s.dim4 > 10) and ('taskrest' in s.protocol_name):
            if not s.is_motion_corrected:
                info[rest].append({'item': s.series_id, 'rec': 'uncorrected'})
    return info
```

---

### Finalize our conversion

```bash
heudiconv -d "/examples/{subject}/*/*/*/*IMA" -s PHANTOM1_3 -f demo_heuristic.py -b -o /output2
```

- You can also download the created heuristic with the command:

```bash
curl https://raw.githubusercontent.com/mgxd/heudiconv/coco2019/demo-heuristic.py -O
```
- Something missing? Double check your `heuristic` and `dicominfo.tsv`!

---

# Questions?

If something is unclear, or you would like to contribute to this guide, please open an issue or pull request on our [Github repo](https://github.com/nipy/heudiconv)
