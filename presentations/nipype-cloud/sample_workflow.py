from nipype.pipeline import engine as pe
from nipype.interfaces import utility as niu
from nipype.interfaces import fsl

from glob import

# define a workflow
wf = Workflow(name='map-wf')

# fetch 5 T1w images
inputnode = pe.Node(niu.IdentityInterface(['in_files']), name='inputnode')
inputnode.inputs.in_files = sorted(glob('/home/neuro/ds000001/sub-0[1-5]/*/*T1w.nii.gz'))

# run bet for each image
bet = pe.MapNode(fsl.Bet(), iterfield=['in_file'], name='bet')
wf.connect(inputnode, 'in_files', bet, 'in_file')

# run the workflow
wf.run()
