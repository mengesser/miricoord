#
"""
Useful python tools for working with the MIRI LRS.
This contains cdp7 specific code.

This version of the tools hooks into the JWST Calibration
Pipeline code to do the heavy lifting.  Note that this
means performance may be affected by what version of
the pipeline you are running!!  It does, however, use
offline versions of the CRDS reference files contained
within this github repository.

Convert JWST v2,v3 locations (in arcsec) to MIRI Imager SCA x,y pixel locations.
Note that the pipeline uses a 0-indexed detector pixel (1032x1024) convention while
SIAF uses a 1-indexed detector pixel convention.  The CDP files define
the origin such that (0,0) is the middle of the lower-left light sensitive pixel
(1024x1024),therefore also need to transform between this science frame and detector frame.

Author: David R. Law (dlaw@stsci.edu)

REVISION HISTORY:
17-Dec-2018  Written by David Law (dlaw@stsci.edu)
"""

import os as os
import numpy as np
from astropy.modeling import models
from asdf import AsdfFile
from jwst import datamodels
from jwst.assign_wcs import miri
import pdb

#############################

# Return the tools version
def version():
    return 'cdp7'

#############################

# Set the relevant FITS distortion files
def get_fitsreffile():
    rootdir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    distfile=os.path.join(rootdir,'data/crds/jwst_miri_distortion_0028.asdf')
    specfile=os.path.join(rootdir,'data/crds/jwst_miri_specwcs_0003.fits')

    refs = {"distortion": distfile, "specwcs": specfile}
   
    return refs

#############################

# Function to convert input X,Y pixel coordinates
# to V2,V3,lambda given a type (slit/slitless) and the most recent reference files
def xytov2v3lam_model(stype,**kwargs):
    # Construct the reference data model in general JWST imager type
    input_model = datamodels.ImageModel()
    # Set the subarray info in the data model meta header
    if (stype.lower() == 'slit'):
        input_model.meta.subarray.name = 'FULL'
        input_model.meta.subarray.xstart = 1
        input_model.meta.subarray.ystart = 1
        input_model.meta.subarray.xsize = 1032
        input_model.meta.subarray.ysize = 1024
        input_model.data = np.zeros((1024,1032))
        input_model.meta.exposure.type = 'MIR_LRS-FIXEDSLIT'
    elif (stype.lower() == 'slitless'):
        input_model.meta.subarray.name = 'SUBPRISM'
        input_model.meta.subarray.xstart = 1
        input_model.meta.subarray.ystart = 529
        input_model.meta.subarray.xsize = 72
        input_model.meta.subarray.ysize = 416
        input_model.data = np.zeros((416,72))
        input_model.meta.exposure.type = 'MIR_LRS-SLITLESS'
    else:
        print('Invalid operation type: specify either slit or slitless')

    # If passed input refs keyword, unpack and use these reference files
    if ('refs' in kwargs):
        therefs=kwargs['refs']
    # Otherwise use default reference files
    else:
        therefs=get_fitsreffile()

    # Call the pipeline code to make a distortion object given these inputs
    distortion = miri.lrs_distortion(input_model, therefs)

    # Return the distortion object that can then be queried
    return distortion

#############################

# Function to return test data about x,y,v2,v3,lam locations
# for slit and slitless cases
def testdata():
    # Slit tests
    xy_slit=np.array([[325.13,299.7],[325.13,29.7],[345.13,379.7]])
    v2v3_slit=np.array([[-415.069,-400.5759],[-415.1946,-400.5655],[-417.237,-400.3958]])
    lam_slit=np.array([8.41039,14.05363, 5.1474])
    stype_slit=['slit' for i in range(0,v2v3_slit.shape[0])]
    
    # Slitless tests
    xy_slitless=np.array([[37.5,300],[37.5,29],[17.5,370.]])
    v2v3_slitless=np.array([[-378.832,-344.9445],[-378.9571,-344.9331],[-376.6104,-345.1475]])
    lam_slitless=np.array([8.41039,14.0694,5.7303])
    stype_slitless=['slitless' for i in range(0,v2v3_slitless.shape[0])]
    
    x=[xy_slit[:,0],xy_slitless[:,0]]
    y=[xy_slit[:,1],xy_slitless[:,1]]
    v2=[v2v3_slit[:,0],v2v3_slitless[:,0]]
    v3=[v2v3_slit[:,1],v2v3_slitless[:,1]]
    lam=[lam_slit[:],lam_slitless[:]]
    stype=['slit','slitless']

    return x,y,v2,v3,lam,stype
