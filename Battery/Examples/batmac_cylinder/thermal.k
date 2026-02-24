*KEYWORD
$ ****************************************************************************
$ thermal
$ ****************************************************************************
$--------1---------2---------3---------4---------5---------6---------7---------8
*CONTROL_SOLUTION
2
*CONTROL_THERMAL_SOLVER
1,1,11,1.e-04
*INITIAL_TEMPERATURE_SET
0,25.0
*CONTROL_THERMAL_TIMESTEP
$0,1.,1.,1.,,,,17
0,1.,1.,0.01,1.
*DEFINE_CURVE
17,,,1.0
0.,1.e-2
0.1,0.2
0.6,1.0
5.0,10.0
20.0,100.0
200.0,1.e3
1.e6,1.e3
*MAT_THERMAL_ISOTROPIC_TITLE
isotropic_thermal
$#    tmid       tro     tgrlc    tgmult      tlat      hlat    
         1      2560       0.0       0.0       0.0       0.0
$#      hc        tc  
     1000.      250.
$*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_MORTAR_ID
$         1
$$#    SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR
$       101         1         3         3                             1         1
$$#      FS        FD        DC        VC       VDC    PENCHK        BT        DT
$ 3.0000E-1                                                                      
$$#     SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF
$                                        
$$#       K      FRAD        H0      LMIN      LMAX      CHLM    BC_FLG      ALGO
$$      1.e8       0.0      1.e8   1.00e-3     5.e-3
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_MORTAR_THERMAL_ID
         1
$#    SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR
       101         1         3         3                             1         1
$#      FS        FD        DC        VC       VDC    PENCHK        BT        DT
        0.                                                                      
$ 3.0000E-1                                                                      
$#     SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF
       1.0       1.0       0.0       0.0       1.0       1.0       1.0       1.0
$        1.                                
$#       K      FRAD        H0      LMIN      LMAX      CHLM    BC_FLG      ALGO
      1.e5       0.0      1.e5        0.     5.e-3
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_MORTAR_THERMAL_ID
         2
$#    SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR
       201         1         3         3                             1         1
$#      FS        FD        DC        VC       VDC    PENCHK        BT        DT
        0.                                                                      
$ 3.0000E-1                                                                      
$#     SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF
       1.0       1.0       0.0       0.0       1.0       1.0       1.0       1.0
$        1.                                
$#       K      FRAD        H0      LMIN      LMAX      CHLM    BC_FLG      ALGO
      1.e5       0.0      1.e5        0.     5.e-3
$*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_MORTAR_THERMAL_ID
$         3
$$#    SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR
$       201       500         3         3                             1         1
$$#      FS        FD        DC        VC       VDC    PENCHK        BT        DT
$        0.                                                                      
$$ 3.0000E-1                                                                      
$$#     SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF
$       1.0       1.0       0.0       0.0       1.0       1.0       1.0       1.0
$$        1.                                
$$#       K      FRAD        H0      LMIN      LMAX      CHLM    BC_FLG      ALGO
$      1.e5       0.0      1.e5        0.     5.e-3
$*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_THERMAL_ID
$$#     cid                                                                 title
$         1                                                                      
$$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
$       101         1         3         3         0         0         0         0
$$#      fs        fd        dc        vc       vdc    penchk        bt        dt
$       0.0       0.0       0.0       0.0       0.0         0       0.01.00000E20
$$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
$       1.0       1.0       0.0       0.0       1.0       1.0       1.0       1.0
$$#      cf      frad       htc      lmin      lmax    ftoslv    bc_flg      algo
$       0.0       0.0     100.0       0.0       0.0       0.5         0         0
$*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_THERMAL_ID
$$#     cid                                                                 title
$         2                                                                      
$$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
$       201         1         3         3         0         0         0         0
$$#      fs        fd        dc        vc       vdc    penchk        bt        dt
$       0.0       0.0       0.0       0.0       0.0         0       0.01.00000E20
$$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
$       1.0       1.0       0.0       0.0       1.0       1.0       1.0       1.0
$$#      cf      frad       htc      lmin      lmax    ftoslv    bc_flg      algo
$       0.0       0.0     100.0       0.0       0.0       0.5         0         0
$*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_THERMAL_ID
$$#     cid                                                                 title
$         3                                                                      
$$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
$       500       201         3         3         0         0         0         0
$$#      fs        fd        dc        vc       vdc    penchk        bt        dt
$       0.0       0.0       0.0       0.0       0.0         0       0.01.00000E20
$$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
$       1.0       1.0       0.0       0.0       1.0       1.0       1.0       1.0
$$#      cf      frad       htc      lmin      lmax    ftoslv    bc_flg      algo
$       0.0       0.0     100.0       0.0       0.0       0.5         0         0
$*DEFINE_CURVE_TITLE
$Upside Convection
$$#    lcid      sidr       sfa       sfo      offa      offo    dattyp
$        41         0  1.000000  1.000000    298.15     0.000         0
$$#                a1                  o1
$          20.0000000                10.0
$         100.0000000                10.0
$         140.0000000                10.0
$         180.0000000                10.0
$         260.0000000                10.0
$         300.0000000                10.0
$         380.0000000                10.0
$         480.0000000                10.0
$        1000.                       10.0
$        5000.                       10.0
*END
