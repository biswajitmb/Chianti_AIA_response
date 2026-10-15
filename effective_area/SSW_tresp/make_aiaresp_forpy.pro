pro make_aiaresp_forpy

  ; IDL script to produce the AIA temeprature response functions,
  ; then output it is a simple format that python will be happy with.
  ;
  ; This is the V9, t0 responses with no degradation correction in them.
  ;
  ; So need to degradation correct your AIA data (using ssw or aiapy)
  ; before combining with these responses
  ;
  ; 17-Aug-2020 IGH
  ; 25-Feb-2021 IGH - Renamed output file as not necessarily v9
  ;~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  ;  tresp=aia_get_response(/temperature,/dn,/eve,timedepend_date='01-Jul-2010')
  ;tresp=aia_get_response(/temperature,/dn,/evenorm)
  tresp=aia_get_response(/temperature,/dn,timedepend_date='1-May-2010');,/area);,/chiantifix);,/evenorm

  ;ids=[0,1,2,3,4,6,7]
  ;channels=tresp.channels[ids]
  ;logt=tresp.logte
  ;tr=tresp.all[*,ids]
  ;units=tresp.units

  save,file='aia_tresp_May012010_temp_nochiantifix_noevnorm'+'.sav',tresp

  stop
end
