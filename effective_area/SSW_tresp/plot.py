from scipy.io import readsav
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np

Observed_image_directory = '/Users/bmondal/BM_Works/MaGIXS/MaGIXS_1/XBP_1/data_old/'

XRT_response_file = Observed_image_directory+'temperature_response/xrt_tresp_300720021.sav'
AIA_response_file = Observed_image_directory+'temperature_response/aia_tresp_30072021.sav'
MAG_response_file = Observed_image_directory+'temperature_response/magixs_tresp_30072021.sav'

#AIA
aia_tresp = readsav(AIA_response_file)
for fil_aia in np.arange(len(aia_tresp['channels'])):
    aia_tresp['channels'][fil_aia] = aia_tresp['channels'][fil_aia].decode('utf-8')
chans=np.array(aia_tresp['channels'])
aia_tresp_logT = aia_tresp['logt']

#chans = np.array(list(chans[0:3]) + list(chans[3::])) #remove a few chhanels
#aia_tresp['tr'] = np.array(list(aia_tresp['tr'][0:3]) + list(aia_tresp['tr'][3::]))

for fil_aia in range(len(chans)):
    plt.plot(aia_tresp_logT,aia_tresp['tr'][fil_aia,:],label=chans[fil_aia][1::])

plt.yscale('log')
plt.xlabel('logT')
plt.xlim([5.5,7.5])
plt.ylim([1.0e-28,1.0e-24])
plt.ylabel('DN cm$^{-5}$ s$^{-1}$ px$^{-1}$')
plt.legend()
plt.show()


#load XRT TStore_outputsresp:
xrt_tresp = readsav(XRT_response_file)
filters = np.array(xrt_tresp['filters'])
filters[0]=filters[0].decode('utf-8')
filters[1]=filters[1].decode('utf-8')
filters[2]=filters[2].decode('utf-8')
filters[3]=filters[3].decode('utf-8')
filters[4]=filters[4].decode('utf-8')
filters[5]=filters[5].decode('utf-8')
units = xrt_tresp['units'].decode('utf-8')
xrt_tresp_logT = xrt_tresp['logt']

filters = np.array(list(filters[1:3]) + [filters[5]]) #consider only 'Al-poly', 'Be-thin', 'Be-thick'
xrt_tresp['tr'] = np.array(list(xrt_tresp['tr'][1:3]) + [xrt_tresp['tr'][5]])

for fil_xrt in range(len(filters)):
    plt.plot(xrt_tresp_logT,xrt_tresp['tr'][fil_xrt,:],label=filters[fil_xrt])

plt.yscale('log')
plt.xlabel('logT')
plt.xlim([5.5,7.5])
plt.ylim([1.0e-28,1.0e-24])
plt.ylabel('DN cm$^{-5}$ s$^{-1}$ px$^{-1}$')
plt.legend()
plt.show()

