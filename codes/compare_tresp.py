import matplotlib
matplotlib.use('QtAgg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import readsav
from scipy import interpolate
import os, glob


DataDir = './../outputs/'
new_tresp_files = glob.glob(os.path.join(DataDir,'*.sav'))

ssw_aia_resp_file = './../effective_area/SSW_tresp/aia_tresp_May012010_temp_nochiantifix_noevnorm.sav'
#ssw_aia_resp_file = './../effective_area/SSW_tresp/aia_tresp_Oct012026.sav'

ssw_aia_tresp = readsav(ssw_aia_resp_file)

for fil_aia in np.arange(len(ssw_aia_tresp['tresp'].channels[0])):
    ssw_aia_tresp['tresp'].channels[0][fil_aia] = ssw_aia_tresp['tresp'].channels[0][fil_aia].decode('utf-8')
chans=np.array(ssw_aia_tresp['tresp'].channels[0])
ssw_aia_tresp_logT = ssw_aia_tresp['tresp'].logte[0]

new_resp_name = []
for i in new_tresp_files:
    namestr = os.path.basename(i).split('.')[0]
    aia_tresp = readsav(i)
    for fil_aia in np.arange(len(aia_tresp['tresp'].channels[0])):
        aia_tresp['tresp'].channels[0][fil_aia] = aia_tresp['tresp'].channels[0][fil_aia].decode('utf-8')
    chans=np.array(aia_tresp['tresp'].channels[0])
    aia_tresp_logT = aia_tresp['tresp'].logte[0]
    globals()['logT_%s'%namestr] = aia_tresp_logT
    globals()['%s'%namestr] = aia_tresp
    new_resp_name += [namestr]

for i in range(len(chans)):

    plt.figure()
    logt_aia__ = ssw_aia_tresp['tresp'][chans[i]][0][0][2]
    unit = ssw_aia_tresp['tresp'][chans[i]][0][0][1]
    tresp__ = ssw_aia_tresp['tresp'][chans[i]][0][0][3]
    line,=plt.plot(logt_aia__,tresp__,'-',label=chans[i])
    #plt.plot(logT,np.sum(M[:,:,i],axis=1),'--')

    for j in new_resp_name:
        logT_new = globals()['%s'%j]['tresp'][chans[i]][0][0][2]
        tresp_new = globals()['%s'%j]['tresp'][chans[i]][0][0][3] 
        plt.plot(logT_new,tresp_new,'--',label=j)

    plt.yscale('log')
    plt.ylabel('DN cm$^5$ s$^{-1}$')
    plt.xlabel('logT')
    plt.ylim([1.0e-29,5.0e-24])
    plt.xlim([4.5,8.5])
    plt.legend()
    plt.savefig(os.path.join('plots',chans[i]+'.png'))
    plt.show()



