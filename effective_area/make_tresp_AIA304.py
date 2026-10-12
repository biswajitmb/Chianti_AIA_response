import numpy as np
import matplotlib.pyplot as plt
from scipy.io import readsav
from scipy import interpolate
import os, glob

import xarray as xr
import dask
from muse.utils.utils import  read_response
from astropy.io import fits

spec_file = '/Users/bmondal/BM_Works/MUSE/codes/BM/MUSE_Synthetic/CI_Biswajit/total_spec_304.idl'
#EA_file = 'EA_195.dat'
EA_file = '/Users/bmondal/BM_Works/MaGIXS/MaGIXS_2/Model/Inversion_Tech/FakeObs/AIA_synthesis/AIA_EA/aia_EffArea_5__A304__.dat'
plate_scale= 0.6 #in arcsec

OutDir = 'outputs'

A = (plate_scale*725*1.0e5)**2

wvl, EA = np.loadtxt(EA_file,unpack=True)

EA_intpf = interpolate.interp1d(wvl, EA)


spec_da = readsav(spec_file)

spec_ = spec_da['allspec_all'] #Ph. cm3. s{-1}. * 1.0e46 #[32,1501]
wvl_spec = spec_da['allene'] #[1501]
logt_spec = np.log10(spec_da['temperature_all']) #[32]

EA_spec = EA_intpf(wvl_spec)

plt.plot(wvl,EA)
plt.plot(wvl_spec,EA_spec,'--')
plt.show()

tresp = []
for t in range(len(logt_spec)):
    tr = np.sum(spec_[t,:]*EA_spec)
    tresp += [tr]

#compare with standerd AIA response:
ssw_rsp_file = './SSW_tresp/aia_tresp_30072021.sav'

#AIA
aia_tresp = readsav(ssw_rsp_file)
for fil_aia in np.arange(len(aia_tresp['channels'])):
    aia_tresp['channels'][fil_aia] = aia_tresp['channels'][fil_aia].decode('utf-8')
chans=np.array(aia_tresp['channels'])
aia_tresp_logT = aia_tresp['logt']
plt.plot(aia_tresp_logT,aia_tresp['tr'][-2]/0.658)

tresp = A*np.array(tresp)/1.0e46 #Ph. cm5. s{-1}
plt.plot(logt_spec,tresp)
plt.yscale('log')
plt.ylabel('Ph cm$^5$ s$^{-1}$')
plt.xlabel('logT')
plt.show()



'''
#Store in a fits file:
OutFileName = 'Tresp_CI304.dat'
f = open(os.path.join(OutDir,OutFileName),'w')
f.write('# logT, Tresp (Ph cm^5 s^-1)\n')
for i in range(len(logt_spec)):
    f.write('%0.2f\t'%logt_spec[i])
    f.write('%0.4e\n'%tresp[i])
f.close()
'''
'''
resp_path_CI = '/Users/bmondal/BM_Works/MUSE/response/CI/'
rsp_files = np.sort(glob.glob(os.path.join(resp_path_CI,'*.ncdf')))
rsp_files = rsp_files[1]

## Read CI response
with dask.config.set(**{'array.slicing.split_large_chunks': False}):
    response = read_response(os.path.join(rsp_files),logTmethod='linear')
    lines = [int(response.line_wvl.data[0])]
    response = response.assign_coords(band = ('line', lines))
response = response.compute()
response = response.swap_dims({"line":"band"})

plt.plot(wvl,EA,label='EA (paul)')
plt.plot(response.SG_xpixel.data,response.effective_area.data,ls='--',label='195 response')
plt.legend()
plt.show()
'''
