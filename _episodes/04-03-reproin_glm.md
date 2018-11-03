---
title: "ReproIn/DataLad: A Reproducible GLM Demo Analysis"
teaching: 15
exercises: 20
questions:
- "How to implement a basic GLM Demo Analysi with complete and unambiguous provenance tracking of all actions?"
objectives:
- this comprehensive capture facilitates re-use of units, and enables computational
  reproducibility
- carefully validated intermediate results (captured as a DataLad dataset) are
  a candidate for publication with minimal additional effort
- the outcome of this demo is available as a demo DataLad dataset from
  [GitHub](https://github.com/myyoda/demo-dataset-glmanalysis)
keypoints:
- we can implement a complete imaging study using DataLad datasets to represent
  units of data processing
- each unit comprehensively captures all inputs and data processing leading up to
  it
- this comprehensive capture facilitates re-use of units, and enables computational
  reproducibility
- carefully validated intermediate results (captured as a DataLad dataset) are
  a candidate for publication with minimal additional effort

---

## A Reproducible GLM Demo Analysis

With our raw data prepared in BIDS format, we can now conduct an analysis.
We will implement a very basic first-level GLM analysis using FSL that runs
in just a few minutes. We will follow the same principles that we already
applied when we prepared the `localizer_scans` dataset: the complete capture of
all inputs, computational environments, code, and outputs.

Importantly, we will conduct our analysis in a new dataset. The raw
`localizer_scans` dataset is suitable for many different analysis that can all
use that dataset as input. In order to avoid wasteful duplication and to improve
the modularity of our data structures, we will merely use the `localizer_scans`
dataset as an input, but we will *not* modify it in any way.

> ## Task: Create a new DataLad dataset called `glm_analysis`
>
> Use the [datalad create] command. Then change into the root directory of the
> newly created dataset.
>
> > ## Solution
> > ~~~
> > % datalad create glm_analysis
> > % cd glm_analysis
> > ~~~
> > {: .bash}
> {: .solution}
>
{: .challenge}

Following the same logic and commands as before, we will add the
`localizer_scans` dataset as a subdataset of the new `glm_analysis` dataset to
enable comprehensive tracking of all input data within the analysis dataset.

> ## Task: Add `localizer_scans` data as a subdataset in `inputs/rawdata`
>
> Use the [datalad install] command. Make sure to identify the analysis dataset
> (the current directory) as the dataset to operate on in order to register the
> `localizer_scans` dataset as a subdataset (and not just as a standalone
> dataset). Then, use the [datalad subdatasets] command to verify the result.
>
> > ## Solution
> > ~~~
> > % datalad install --dataset . --source ../localizer_scans inputs/rawdata
> > % datalad subdatasets
> > ~~~
> > {: .bash}
> {: .solution}
>
{: .challenge}

Regarding the layout of this analysis dataset, we unfortunately cannot yet rely
on automatic tools and a comprehensive standard (but such guidelines are
actively being worked on). However, DataLad nevertheless aids efforts to bring
order to the chaos. Anyone can develop their own ideas on how a dataset should
be structured and implement these concepts in *dataset procedures* that can be
executed using the [datalad run-procedure] command.

We are going to adopt the YODA principles: a set of simple rules on how to
structure analysis dataset(s) to facilitate their reuse and
reproducibility of the results
(see [OHBM 2018 YODA
poster](https://github.com/myyoda/poster/blob/master/ohbm2018.pdf) for
more information). Here, the only relevant aspects
is that we want to keep all analysis scripts in the `code/` subdirectory of
this dataset and later enhance it with full analysis environment
images. We can get a readily configured dataset by running the YODA
setup procedure:

> ## Task: Run the `setup_yoda_dataset` procedure
>
> Use the [datalad run-procedure] command. Check what has changed in the dataset.
>
> > ## Solution
> > ~~~
> > % datalad run-procedure setup_yoda_dataset
> > ~~~
> > {: .bash}
> {: .solution}
>
{: .challenge}

Before we can fire up FSL for our GLM analysis, we need two pieces of custom
code:

1. a small script that can convert BIDS events.tsv files into the EV3 format that
   FSL can understand, available at <https://raw.githubusercontent.com/ReproNim/sfn2018-training/master/section23/scripts/events2ev3.sh>

2. an FSL analysis configuration template script available at <https://raw.githubusercontent.com/ReproNim/sfn2018-training/master/section23/scripts/ffa_design.fsf>

Any custom code needs to be tracked if we want to achieve a complete record of
how an analysis was conducted. Hence we will store those scripts in our analysis
dataset.

> ## Download the Scripts and Include Them in the Analysis Dataset
>
> Use the [datalad download-url] command. Place the scripts in the `code/` directory
> under their respective names. Check `git log` to confirm that the commit message
> shows the URL where each script has been downloaded from.
>
> > ## Solution
> > ~~~
> > % datalad download-url --path code \
> >   https://raw.githubusercontent.com/ReproNim/sfn2018-training/master/section23/scripts/events2ev3.sh \
> >   https://raw.githubusercontent.com/ReproNim/sfn2018-training/master/section23/scripts/ffa_design.fsf
> > % git log
> >
> > ~~~
> > {: .bash}
> {: .solution}
>
{: .challenge}

At this point, our analysis dataset contains all of the required inputs. We only
have to run our custom code to produce the inputs in the format that FSL
expects. First, let's convert the events.tsv file into EV3 format files.

> ## Task: Run the converter script for the event timing information
>
> Use the [datalad run] command to execute the script at `code/events2ev3.sh`.
> It requires the name of the output directory (use `sub-02`) and the location
> of the BIDS events.tsv file to be converted. Use the `--input` and `--output`
> options to let DataLad automatically manage these files for you.
> **Important**: The subdataset does not actually have the content for the
> events.tsv file yet. If you use `--input` correctly, DataLad will obtain the
> file content for you automatically. Check the output carefully, the script is
> written in a sloppy way that will produce some output even when things go
> wrong. Each generated file must have three numbers per line.
>
> > ## Solution
> > {% raw %}
> > ~~~
> > % datalad run -m 'Build FSL EV3 design files' \
> >       --input inputs/rawdata/sub-02/func/sub-02_task-oneback_run-01_events.tsv \
> >       --output 'sub-02/onsets' \
> >       bash code/events2ev3.sh sub-02 {inputs}
> > ~~~
> > {: .bash}
> > {% endraw %}
> {: .solution}
>
{: .challenge}

Now we're ready for FSL! And since FSL is certainly not a simple, system
program, we will again use it in a container and add that container to this
analysis dataset. A ready-made container with FSL (~260 MB) is available from
shub://ReproNim/ohbm2018-training:fsln (a local copy is available at
`~/images/fsl.simg` in the training VM).

> ## Task: Add a container with FSL
>
> Use the [datalad containers-add] command to add this container under the name
> `fsl`. Then use the [datalad containers-list] command to verify that
> everything worked.
>
> > ## Solution
> > ~~~
> > % # regular call
> > % datalad containers-add fsl --url shub://ReproNim/ohbm2018-training:fsln
> > % # BUT in the training VM do this to save on downloads
> > % datalad containers-add fsl --url ~/images/fsl.simg \
> >       --call-fmt 'singularity exec {img} {cmd}'
> > %
> > % datalad containers-list
> > ~~~
> > {: .bash}
> {: .solution}
>
{: .challenge}

With this we have completed the analysis setup. At such a milestone it can be
useful to label the state of a dataset that can be referred to later on. Let's
add the label `ready4analysis` here.

{% raw %}
> ~~~
> % datalad save --version-tag ready4analysis
> ~~~
> {: .bash}
{% endraw %}

All we have left is to configure the desired first-level GLM analysis with FSL.
The following command will create a working configuration from the template we
stored in `code/`. It uses the arcane, yet powerful `sed` editor. We will again
use [datalad run] to invoke our command so that we store in the history
*how* this template was generated (so that we may audit, alter, or regenerate
this file in the future — fearlessly).

{% raw %}
> ~~~
> datalad run \
>     -m "FSL FEAT analysis config script" \
>     --output sub-02/1stlvl_design.fsf \
>     bash -c 'sed -e "s,##BASEPATH##,{pwd},g" -e "s,##SUB##,sub-02,g" \
>         code/ffa_design.fsf > {outputs}'
> ~~~
> {: .bash}
{% endraw %}

The command that we will run now in order to compute the analysis results is a
simple `feat sub-02/1stlvl_design.fsf`. However, in order to achieve the most
reproducible and most portable execution, we should tell the [datalad
containers-run] command what the inputs and outputs are.  DataLad will then be
able to obtain the required NIfTI time series file from the `localizer_scans`
raw subdataset.

Please run the following command as soon as possible; it takes around 5 minutes
to complete on an average system.

{% raw %}
> ~~~
> datalad containers-run --container-name fsl -m "sub-02 1st-level GLM" \
    --input sub-02/1stlvl_design.fsf \
    --input sub-02/onsets \
    --input inputs/rawdata/sub-02/func/sub-02_task-oneback_run-01_bold.nii.gz \
    --output sub-02/1stlvl_glm.feat \
    feat {inputs[0]}
> ~~~
> {: .bash}
{% endraw %}

Once this command finishes, DataLad will have captured the entire FSL output,
and the dataset will contain a complete record all the way from the input BIDS
dataset to the GLM results (which, by the way, performed an FFA localization on
a real BOLD imaging dataset, take a look!). The BIDS subdataset in turn has a
complete record of all processing down from the raw DICOMs onwards.


## Get Ready for the Afterlife

Once a study is complete and published it is important to archive data and
results, for example, to be able to respond to inquiries from readers of an
associated publication. The modularity of the study units makes this
straightforward and avoid needless duplication. We now that the raw data for
this GLM analysis is tracked in its own dataset (`localizer_scans`) that only
needs to be archived once, regardless of how many analyses use it as input.
This means that we can "throw away" this subdataset copy *within* this
analysis dataset. DataLad can re-obtain the correct version at any point in
the future, as long as the recorded location remains accessible.

> ## Task: Verify that the `localizer_scans` subdataset is unmodified and uninstall it
>
> Use the [datalad diff] command and `git log` to verify that the subdataset is
> in the same state as when it was initially added.  Then use [datalad
> uninstall] to delete it.
>
> > ## Solution
> > ~~~
> > % datalad diff -- inputs
> > % git log -- inputs
> > % datalad uninstall --dataset . inputs --recursive
> > ~~~
> > {: .bash}
> {: .solution}
>
{: .challenge}

Before we archive these analysis results, we can go one step further and verify
their computational reproducibility. DataLad provides a `rerun` command that is
capable of "replaying" any recorded command. The following command we
re-execute the FSL analysis (the command that was recorded since we tagged the
dataset as "ready4analysis"). It will record the recomputed results in a
separate Git branch named "verify" of the dataset. We can then automatically
compare these new results to the original ones in the "master" branch. We
will see that all outputs can be reproduced in bit-identical form. The only
changes are observed in log files that contain volatile information, such
as time steps.

> {% raw %}
> ~~~
> # rerun FSL analysis from scratch (~5 min)
> % datalad rerun --branch verify --onto ready4analysis --since ready4analysis
> % # check that we are now on the new `verify` branch
> % git branch
> % # compare which files have changes with respect to the original results
> % git diff master --stat
> % # switch back to the master branch and remove the `verify` branch
> % git checkout master
> % git branch -D verify
> ~~~
> {: .bash}
> {% endraw %}

[datalad add-sibling]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-add-sibling.html
[datalad add]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-add.html
[datalad annotate-paths]: http://docs.datalad.org/en/latest/generated/man/datalad-annotate-paths.html
[datalad clean]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-clean.html
[datalad clone]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-clone.html
[datalad copy_to]: http://docs.datalad.org/en/latest/_modules/datalad/support/annexrepo.html?highlight=%22copy_to%22
[datalad create-sibling-github]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-create-sibling-github.html
[datalad create-sibling]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-create-sibling.html
[datalad create]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-create.html
[datalad download-url]: http://docs.datalad.org/en/latest/generated/man/datalad-download-url.html
[datalad diff]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-diff.html
[datalad drop]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-drop.html
[datalad export]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-export.html
[datalad export_tarball]: http://docs.datalad.org/en/latest/generated/datalad.plugin.export_tarball.html
[datalad get]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-get.html
[datalad install]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-install.html
[datalad ls]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-ls.html
[datalad metadata]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-metadata.html
[datalad plugin]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-plugin.html
[datalad publish]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-publish.html
[datalad remove]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-remove.html
[datalad run]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-run.html
[datalad run-procedure]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-run-procedure.html
[datalad rerun]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-rerun.html
[datalad save]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-save.html
[datalad search]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-search.html
[datalad siblings]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-siblings.html
[datalad sshrun]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-sshrun.html
[datalad subdatasets]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-subdatasets.html
[datalad uninstall]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-uninstall.html
[datalad update]: http://datalad.readthedocs.io/en/latest/generated/man/datalad-update.html
[datalad containers-add]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-containers-add.html
[datalad containers-list]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-containers-list.html
[datalad containers-run]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-containers-run.html

[ReproIn]: http://reproin.repronim.org
[ReproIn heuristic]: https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/reproin.py
[DataLad]: http://datalad.org
[datalad-neuroimaging]: https://github.com/datalad/datalad-neuroimaging
[datalad-container]: https://github.com/datalad/datalad-container
[HeuDiConv]: http://github.com/nipy/heudiconv
[BIDS]: http://bids.neuroimaging.io
[singularity-hub]: https://singularity-hub.org/
[singularity]: http://singularity.lbl.gov/

[Git submodule]: https://git-scm.com/docs/git-submodule
[Git]: https://git-scm.com
[Git annex]: https://git-annex.branchable.com/
