
;============================================================
; Rebuild an IDL structure while preserving tag order
;============================================================

FUNCTION rebuild_structure, original, replacements

    COMPILE_OPT IDL2

    tags = TAG_NAMES(original)
    replace_tags = TAG_NAMES(replacements)

    FOR j = 0, N_ELEMENTS(tags)-1 DO BEGIN

        idx = WHERE(replace_tags EQ tags[j], count)

        IF count GT 0 THEN BEGIN
            value = replacements.(idx[0])
        ENDIF ELSE BEGIN
            value = original.(j)
        ENDELSE

        IF j EQ 0 THEN BEGIN
            result = CREATE_STRUCT(tags[j], value)
        ENDIF ELSE BEGIN
            result = CREATE_STRUCT(result, tags[j], value)
        ENDELSE

    ENDFOR

    RETURN, result

END


;============================================================
; Read an HDF5 dataset if it exists
;============================================================

FUNCTION read_h5_optional, fid, dataset_name, found=found

    COMPILE_OPT IDL2

    found = 0B

    CATCH, error_status

    IF error_status NE 0 THEN BEGIN
        CATCH, /CANCEL
        RETURN, !NULL
    ENDIF

    did = H5D_OPEN(fid, dataset_name)
    value = H5D_READ(did)
    H5D_CLOSE, did

    CATCH, /CANCEL

    found = 1B

    RETURN, value

END

;============================================================
; Read a root-level HDF5 attribute
;============================================================

FUNCTION read_h5_attribute, fid, attribute_name

    COMPILE_OPT IDL2

    aid = H5A_OPEN_NAME(fid, attribute_name)
    value = H5A_READ(aid)
    H5A_CLOSE, aid

    RETURN, value

END

;============================================================
; Main procedure
;============================================================

PRO make_idl_format

    COMPILE_OPT IDL2

    base_file = './../effective_area/SSW_tresp/aia_tresp_May012010_temp.sav'

    hdf_file = 'aia_tresp_sun_photospheric_2021_asplund_EA01May2010'
    ;hdf_file = 'aia_tresp_sun_coronal_1992_feldman_ext_EA01May2010'
    ;hdf_file = 'aia_tresp_sun_photospheric_2015_scott_EA01May2010'
    ;hdf_file = 'aia_tresp_sun_coronal_2021_chianti_EA01May2010'

    h5_path = './../outputs/' + hdf_file + '.h5'
    sav_path = './../outputs/' + hdf_file + '.sav'

    ;--------------------------------------------------------
    ; 1. Restore original response
    ;--------------------------------------------------------

    RESTORE, base_file

    original = tresp

    PRINT, 'Original response:'
    HELP, original.all
    HELP, original.logte

    ;--------------------------------------------------------
    ; 2. Open HDF5 file and read temperature grid
    ;--------------------------------------------------------

    fid = H5F_OPEN(h5_path)

    did = H5D_OPEN(fid, 'logT')
    logT_raw = H5D_READ(did)
    H5D_CLOSE, did

    PRINT, 'HDF5 temperature grid:'
    HELP, logT_raw

    PRINT, 'First five temperature values:'
    PRINT, logT_raw[0:4]

    IF (MIN(logT_raw) GT 4.0) AND $
       (MAX(logT_raw) LT 9.0) THEN BEGIN

        logT_new = FLOAT(logT_raw)

    ENDIF ELSE BEGIN

        MESSAGE, 'Temperature grid is not in expected log10(T) range.'

    ENDELSE

    nT = N_ELEMENTS(logT_new)

    ;--------------------------------------------------------
    ; 3. Read modified channel responses
    ;--------------------------------------------------------

    channels = ['A94', 'A131', 'A171', 'A193', $
                'A211', 'A304', 'A335']

    nCh = N_ELEMENTS(channels)

    M_new = DBLARR(nT, nCh)

    FOR i = 0, nCh-1 DO BEGIN

        did = H5D_OPEN(fid, channels[i])
        response = DOUBLE(H5D_READ(did))
        H5D_CLOSE, did

        IF N_ELEMENTS(response) NE nT THEN $
            MESSAGE, 'Dimension mismatch for ' + channels[i]

        M_new[*, i] = REFORM(response, nT)

    ENDFOR

    ;--------------------------------------------------------
    ; 4. Read optional new metadata from HDF5
    ;--------------------------------------------------------
    ; Convention:
    ;
    ; /metadata/NAME
    ;

    metadata_names = ['CHIANTI_VERSION', 'ABUNDANCE', $
                      'IONIZATION', 'DATE']

    metadata_replacements = !NULL
    original_tags = TAG_NAMES(original)

    FOR k = 0, N_ELEMENTS(metadata_names)-1 DO BEGIN

        tag = metadata_names[k]

        idx = WHERE(original_tags EQ tag, count)

        IF count EQ 1 THEN BEGIN

            metadata_path = '/metadata/' + tag

            value = read_h5_optional( $
                fid, metadata_path, found=found)

            IF found THEN BEGIN

                ; Construct metadata replacements
                IF SIZE(metadata_replacements, /TYPE) EQ 0 THEN BEGIN
                    metadata_replacements = CREATE_STRUCT( $
                        tag, value)
                ENDIF ELSE BEGIN
                    metadata_replacements = CREATE_STRUCT( $
                        metadata_replacements, tag, value)
                ENDELSE

                PRINT, 'New metadata: ', tag

            ENDIF

        ENDIF

    ENDFOR

    ;============================================================
    ; Read all metadata from root-level HDF5 attributes
    ;============================================================
    
    metadata = CREATE_STRUCT( $
        'INSTRUMENT', STRING(read_h5_attribute(fid, 'INSTRUMENT')), $
        'DESCRIPTION', STRING(read_h5_attribute(fid, 'DESCRIPTION')), $
        'ABUNDANCE_MODEL', STRING(read_h5_attribute(fid, 'ABUNDANCE_MODEL')), $
        'CREATED_UTC', STRING(read_h5_attribute(fid, 'CREATED_UTC')), $
        'CREATOR', STRING(read_h5_attribute(fid, 'CREATOR')), $
        'CREATOR_EMAIL', STRING(read_h5_attribute(fid, 'CREATOR_EMAIL')), $
        'N_CHANNELS', LONG(read_h5_attribute(fid, 'N_CHANNELS')), $
        'N_TEMPERATURE', LONG(read_h5_attribute(fid, 'N_TEMPERATURE')), $
        'TEMPERATURE_UNITS', STRING(read_h5_attribute(fid, 'TEMPERATURE_UNITS')), $
        'RESPONSE_UNITS', STRING(read_h5_attribute(fid, 'RESPONSE_UNITS')), $
        'PURPOSE', STRING(read_h5_attribute(fid, 'PURPOSE')) $
    )
    
    PRINT, '-------------------------------------'
    PRINT, 'Imported HDF5 metadata:'
    HELP, metadata, /STRUCTURE
    
    ; Check metadata against reconstructed arrays
    IF metadata.n_channels NE nCh THEN $
        MESSAGE, 'Metadata channel count mismatch.'
    
    IF metadata.n_temperature NE nT THEN $
        MESSAGE, 'Metadata temperature count mismatch.'
    
    H5F_CLOSE, fid

    ;--------------------------------------------------------
    ; 5. Rebuild individual channel structures
    ;--------------------------------------------------------

    FOR i = 0, nCh-1 DO BEGIN

        idx = WHERE(original_tags EQ channels[i], count)

        IF count NE 1 THEN $
            MESSAGE, 'Channel not found: ' + channels[i]

        old_channel = original.(idx[0])

        response = REFORM(M_new[*, i], nT)

        channel_replacements = CREATE_STRUCT( $
            'LOGTE', logT_new, $
            'TRESP', response)

        new_channel = rebuild_structure( $
            old_channel, channel_replacements)

        IF i EQ 0 THEN BEGIN

            new_channels = CREATE_STRUCT( $
                channels[i], new_channel)

        ENDIF ELSE BEGIN

            new_channels = CREATE_STRUCT( $
                new_channels, channels[i], new_channel)

        ENDELSE

    ENDFOR

    ;--------------------------------------------------------
    ; 6. Rebuild top-level structure
    ;--------------------------------------------------------

    replacements = CREATE_STRUCT( $
        'LOGTE', logT_new, $
        'ALL', M_new)

    channel_tags = TAG_NAMES(new_channels)

    FOR i = 0, nCh-1 DO BEGIN

        replacements = CREATE_STRUCT( $
            replacements, channel_tags[i], new_channels.(i))

    ENDFOR

    ; Include new metadata replacements
    IF SIZE(metadata_replacements, /TYPE) EQ 8 THEN BEGIN

        meta_tags = TAG_NAMES(metadata_replacements)

        FOR k = 0, N_ELEMENTS(meta_tags)-1 DO BEGIN

            replacements = CREATE_STRUCT( $
                replacements, meta_tags[k], $
                metadata_replacements.(k))

        ENDFOR

    ENDIF

    tresp = rebuild_structure(original, replacements)

    ;--------------------------------------------------------
    ; 7. Validate dimensions and temperature values
    ;--------------------------------------------------------

    PRINT, '-------------------------------------'
    PRINT, 'Original ALL:'
    HELP, original.all

    PRINT, 'Modified ALL:'
    HELP, tresp.all

    PRINT, 'Modified LOGTE:'
    HELP, tresp.logte

    PRINT, 'Modified A94 response:'
    HELP, tresp.a94.tresp

    PRINT, 'Modified temperature range:'
    PRINT, MIN(tresp.logte), MAX(tresp.logte)

    dims = SIZE(tresp.all, /DIMENSIONS)

    IF (dims[0] NE nT) OR (dims[1] NE nCh) THEN $
        MESSAGE, 'Combined response dimensions incorrect.'

    ;--------------------------------------------------------
    ; 8. Save new IDL file
    ;--------------------------------------------------------

    ;SAVE, tresp, FILENAME=sav_path
    SAVE, tresp, metadata, FILENAME=sav_path

    PRINT, 'Saved: ', sav_path

END

