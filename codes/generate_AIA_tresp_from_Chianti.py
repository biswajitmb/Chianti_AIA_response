'''
Purpose: Generate AIA temperature response using Chinativ11 specrum.
	Chianti spectrum is pre-calculated for unit abundances.
	Appropriate abundance will apply before creating AIA response.
	It will use AIA pre-calculated effective area from SSW

Note on pre-calculated AIA effective area from SSW:
	tresp=aia_get_response(/dn,/evenorm,timedepend_date='1-May-2010',/chiantifix,/area)
        - The output EA will include photon to DN conversion factor applied
 	- The EA also apply the time-dependent degradation factor
	- The EA does not apply any factor for '/chiantifix'
-Biswajit, Oct-10-2026
'''


import matplotlib
matplotlib.use('QtAgg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import readsav
from scipy import interpolate
import os, glob
from astropy.io import fits
import h5py
from datetime import datetime, timezone
###########################

#abund_file_name = 'sun_coronal_1992_feldman_ext'
abund_file_name = 'sun_photospheric_2021_asplund'
#abund_file_name = 'sun_coronal_2021_chianti'
#abund_file_name = 'sun_photospheric_2015_scott' 

abundance_file = os.path.join('/Users/bmondal/BM_Works/softwares/Chianti/CHIANTI_11.0.2_database/abundance/archive',
    r'..',
    abund_file_name+'.abund')

#abundance_file = os.path.join(abund_file_name+'.abund')

ChiantiTable = '/Users/bmondal/BM_Works/softwares/Chianti/BM_table/Chiantiv11_1to1000A_d1mA/AllSpec_formated_Chiantiv11_1to1000A_d1mA.fits'

channels = [94,131,171,193,211,304,335]
DN2Ph = [2.128,1.523,1.168,1.024,0.946,0.658,0.596] #not used. Effective area estimated from SSW (with /DN keyward) already included this conversion to the effective area.

EA_files_Dir = './../effective_area'
ssw_rsp_file = EA_files_Dir+'/SSW_tresp/aia_tresp_May012010_area_nochiantifix_noevnorm.sav' #Note: this EA was calculated using /DN, so Ph2DN is applied
plate_scale= 0.6 #in arcsec

OutDir = 'outputs'

elemZ_unknown = []#[12,13,14,16,26] #[] #elements atomic number for which different abundance will be considered.
elemZ_unknown_abund = []#[7.55, 6.43, 7.51, 7.12, 7.46] #abundances in log scales. 12 -> absolute vaue is one

dlamda_in = 0.001 #in A. Resolution of the incident wavelength array (used in 'generate_instrument_response.py') in response.

logT = np.arange(start=4.1,stop=8.9,step=0.1)

############################

A = (plate_scale*725*1.0e5)**2
sundist=1.495978707 # in 1e13 cm
sundist2=sundist*sundist #; in 1e26 cm^2
chiso_conversion_fact = sundist2*1.0e26/A #for unit of cm^-5

if len(elemZ_unknown) > 0 : FIP_var = True
else: FIP_var = False

def abund2FIP(abund,ph_abund):
    return 10**(abund-ph_abund)
def FIP2abund(FIP,ph_abund):
    return (np.log10(FIP) + ph_abund)
def abund_log2abs(abund):
    return 10**(abund-12)
def abund_abs2log(abund):
    return 12+np.log10(abund)
def kev_to_angstrom(E_keV):
    return 12.39842 / E_keV

#read abundance file
abund_data = np.loadtxt(abundance_file,max_rows=30,dtype={'names': ('Z', 'A', 'Ele_str'), 'formats': ('i2', 'f4', 'S2')})
abund = abund_log2abs(abund_data['A'])

elemZ_unknown_abund_abs = abund_log2abs(np.array(elemZ_unknown_abund))
with fits.open(ChiantiTable) as chianti_hdu:
    chianti_table = chianti_hdu[0].data #[logT, Ene_keV, Element_Z]
    ch_elem_Z = np.squeeze(chianti_hdu[3].data['Z'])
    ch_ene = chianti_hdu[2].data['E']  #uniform frid of dE = 0.001 KeV
    ch_temp_log = chianti_hdu[1].data['LOGT'] #Uniform grid of dLogT = 0.004

#select logT index for the given requirement
ind = np.where(np.isclose(ch_temp_log[:, None], logT, atol=1e-3))[0]
chianti_table = chianti_table[ind]
ch_temp_log = ch_temp_log[ind]

def cal_total_chianti_spec(spec_table,abund,elements_Z):
    #Add pre-calculated chianti spectrum for multiple elements
    spec=0
    for elem in range(len(elements_Z)):
        spec += abund[elem] * spec_table[:,:,int(elements_Z[elem]-1)] #[temp, ene]
    return spec

#Estimate which elements needs seperately calculate
elem_Z_known_abund = ch_elem_Z
known_abund = abund
if FIP_var is True :  #if any elements need to calculate seperately
    c = 0
    for i in elemZ_unknown:
        known_abund = np.delete(abund,np.where(elem_Z_known_abund == i)[0][0])
        elem_Z_known_abund = np.delete(elem_Z_known_abund,np.where(elem_Z_known_abund == i)[0][0])
        c+=1
    total_spec_Elem_LowFIP = cal_total_chianti_spec(chianti_table, elemZ_unknown_abund_abs, elemZ_unknown) #/ dlamda_in # In unit of Ph-cm3/s/A. [len(logT), len(E)]
total_spec_KnownElem = cal_total_chianti_spec(chianti_table, known_abund, elem_Z_known_abund) #/ dlamda_in # In unit of Ph-cm3/s/A. [len(logT), len(E)]

if FIP_var is True:
    spectral_comp = 2#len(elemZ_unknown)+1
    M = np.zeros([len(logT),spectral_comp,len(channels)])
else:
    M = np.zeros([len(logT),len(channels)])
    spectral_comp = 1

#Read AIA SSW response to read effective areas. 
#Note: these effective areas are apply for evenorm
aia_tresp = readsav(ssw_rsp_file)
for fil_aia in np.arange(len(aia_tresp['tresp'].channels[0])):
    aia_tresp['tresp'].channels[0][fil_aia] = aia_tresp['tresp'].channels[0][fil_aia].decode('utf-8')
chans=np.array(aia_tresp['tresp'].channels[0])
#aia_tresp_logT = aia_tresp['tresp'].logte[0]
wvl = aia_tresp['tresp'].WAVE[0]
area = aia_tresp['tresp'].ALL[0] #[wvl,channels]

for i in range(len(channels)):
    #EA_file = os.path.join(EA_files_Dir,'aia_EffArea_'+format('%d'%i)+'__A'+format('%d'%channels[i])+'__.dat')
    #wvl, EA = np.loadtxt(EA_file,unpack=True)
    c = np.where(chans == 'A'+str(channels[i]))[0][0]
    EA = area[:,c]
    EA_intpf = interpolate.interp1d(wvl, EA,bounds_error=False,fill_value=0)

    EA_spec = EA_intpf(ch_ene)
    
    for t in range(len(logT)):
        if FIP_var is True: 
            M[t,0,i] = np.sum(total_spec_KnownElem[t,:]*EA_spec) #for High-FIP
            M[t,1,i] = np.sum(total_spec_Elem_LowFIP[t,:]*EA_spec) #for low FIP
            M[t,:,i] = (M[t,:,i]/chiso_conversion_fact)#/DN2Ph[i]
        else:
            M[t,i] = np.sum(total_spec_KnownElem[t,:]*EA_spec)
            M[t,i] = (M[t,i]/chiso_conversion_fact)#/DN2Ph[i] #DN cm^-5 /s/pix

color=['r','g','b','m','k','cyan','orange']
for i in range(len(channels)):
    plt.plot(logT,M[:,i],'-',label=format('%d'%channels[i]),color=color[i])
    #plt.plot(logT,M[:,1,i],'--',color=color[i])
plt.yscale('log')
plt.ylabel('DN cm$^5$ s$^{-1}$')
plt.xlabel('logT')
plt.xlim([logT[0],logT[-1]])
plt.legend()
plt.show()

#compare with standerd AIA response:
ssw_rsp_file = EA_files_Dir+'/SSW_tresp/aia_tresp_May012010_temp_nochiantifix_noevnorm.sav'
aia_tresp = readsav(ssw_rsp_file)
for fil_aia in np.arange(len(aia_tresp['tresp'].channels[0])):
    aia_tresp['tresp'].channels[0][fil_aia] = aia_tresp['tresp'].channels[0][fil_aia].decode('utf-8')
chans=np.array(aia_tresp['tresp'].channels[0])
aia_tresp_logT = aia_tresp['tresp'].logte[0]

for i in range(len(chans)):
    logt_aia__ = aia_tresp['tresp'][chans[i]][0][0][2]
    unit = aia_tresp['tresp'][chans[i]][0][0][1]
    tresp__ = aia_tresp['tresp'][chans[i]][0][0][3]
    line,=plt.plot(logt_aia__,tresp__,'-',label=chans[i])
    #plt.plot(logT,np.sum(M[:,:,i],axis=1),'--')
    plt.plot(logT,M[:,i],'--',color=line.get_color())

    plt.yscale('log')
    plt.ylabel('DN cm$^5$ s$^{-1}$')
    plt.xlabel('logT')
#plt.plot(logT,np.sum(M[:,:,-1],axis=1),'--')

plt.legend()
plt.show()

#Save the new response in hd5, which will be use later to make .sav file in python

channels = ['A94', 'A131', 'A171', 'A193', 'A211', 'A304', 'A335']

assert logT.shape == (len(logT),)
assert M.shape == (len(logT), len(channels))

with h5py.File(os.path.join('./../outputs/','aia_tresp_'+abund_file_name+'_EA01May2010.h5'), 'w') as f:

    # ========================================================
    # Global metadata / file header
    # ========================================================
    f.attrs['INSTRUMENT'] = 'SDO/AIA'
    f.attrs['DESCRIPTION'] = 'AIA temperature response functions'
    f.attrs['ABUNDANCE_MODEL'] = abund_file_name
    f.attrs['CREATED_UTC'] = datetime.now(timezone.utc).isoformat()
    f.attrs['CREATOR'] = 'Biswajit Mondal'
    f.attrs['CREATOR_EMAIL'] = 'biswajit70mondal94@gmail.com'
    f.attrs['N_CHANNELS'] = len(channels)
    f.attrs['N_TEMPERATURE'] = len(logT)
    f.attrs['TEMPERATURE_UNITS'] = 'log10(T/K)'
    f.attrs['RESPONSE_UNITS'] = 'DN cm^5 s^-1'  # Verify units
    f.attrs['PURPOSE'] = 'Transfer to IDL for reconstruction of SSW .sav file'


    f.create_dataset('logT', data=logT)

    for i, ch in enumerate(channels):
        f.create_dataset(ch, data=M[:, i])

