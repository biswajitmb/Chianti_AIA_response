import matplotlib
matplotlib.use('QtAgg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import readsav
from scipy import interpolate
import os, glob

ssw_aia_resp_file = './SSW_tresp/aia_tresp_May012010_area.sav'

ssw_aia_tresp = readsav(ssw_aia_resp_file)

for fil_aia in np.arange(len(ssw_aia_tresp['tresp'].channels[0])):
    ssw_aia_tresp['tresp'].channels[0][fil_aia] = ssw_aia_tresp['tresp'].channels[0][fil_aia].decode('utf-8')
chans=np.array(ssw_aia_tresp['tresp'].channels[0])
#ssw_aia_tresp_logT = ssw_aia_tresp['tresp'].logte[0]

wvl = ssw_aia_tresp['tresp'].WAVE[0] 
area = ssw_aia_tresp['tresp'].ALL[0] #[wvl,channels]

ssw_aia_resp_file = './SSW_tresp/aia_tresp_May012010_area_phot.sav'

ssw_aia_tresp = readsav(ssw_aia_resp_file)

for fil_aia in np.arange(len(ssw_aia_tresp['tresp'].channels[0])):
    ssw_aia_tresp['tresp'].channels[0][fil_aia] = ssw_aia_tresp['tresp'].channels[0][fil_aia].decode('utf-8')
chans=np.array(ssw_aia_tresp['tresp'].channels[0])
#ssw_aia_tresp_logT = ssw_aia_tresp['tresp'].logte[0]

wvl2 = ssw_aia_tresp['tresp'].WAVE[0]
area2 = ssw_aia_tresp['tresp'].ALL[0] #[wvl,channels]


for i in range(len(chans)):
    plt.plot(wvl,area[:,i],label='new')
    
    peak_wvl = wvl[np.where(area[:,i] == area[:,i].max())]
    plt.xlim(peak_wvl-20,peak_wvl+20)

    area_file = 'aia_EffArea_'+format('%d'%i)+'__'+chans[i]+'__.dat'
    wvl_,a_ = np.loadtxt(area_file,unpack=True)

    #plt.plot(wvl_,a_,label=chans[i]+' :old',ls='--')

    plt.plot(wvl2,area2[:,i],label='new2',ls='--')

    plt.xlim(peak_wvl-20,peak_wvl+20)
    plt.legend()
    plt.show()




