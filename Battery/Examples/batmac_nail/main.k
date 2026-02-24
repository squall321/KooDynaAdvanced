*KEYWORD
*TITLE
Fall of a sphere on a 10 cells battery
*INCLUDE
mesh8_1.k
em.k
uVsSoc.k
current.k
thermal.k
*CONTROL_ACCURACY
                   4                   1
*PARAMETER
$--------1---------2---------3---------4---------5---------6---------7---------8
R    tDtoR    12.e-3
R   tDtoR1   12.1e-3
*CONTROL_TERMINATION
$--------1---------2---------3---------4---------5---------6---------7---------8
$#  endtim    endcyc     dtmin    endeng    endmas      
      100.         0     0.000     0.000
*DEFINE_CURVE
26
0.,1.e-4
&tDtoR,1.e-4
&tDtoR1,1.
100.,1.
1000.,1.
*DEFINE_CURVE
30
0.,0.   
&tDtoR,0.
&tDtoR1,1.0
100.,1.
1000.,1.
*DEFINE_CURVE
31
0.,0.   
&tDtoR,1.   
1000.,1.
*DEFINE_CURVE
32
0.,0.
1000.,0.
*BOUNDARY_PRESCRIBED_MOTION_RIGID
        10       1         0        32        1.                          &tDtoR
        10       2         0        32        1.                          &tDtoR
        10       3         0        32        1.                          &tDtoR
        10       5         0        32        1.                          &tDtoR
        10       6         0        32        1.                          &tDtoR
        10       7         0        32        1.                          &tDtoR
*CONTROL_IMPLICIT_GENERAL
$--------1---------2---------3---------4---------5---------6---------7---------8
       -30     0.001
*CONTROL_IMPLICIT_DYNAMICS
         1      0.55   0.27563
*CONTROL_IMPLICIT_AUTO
         1                                     1.0
*COMMENT *LOAD_BODY_Y
        31      9.81
*DATABASE_BINARY_D3PLOT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt      lcdt      beam     npltc    psetid      
     5.e-4        14         0         0         0
$#   ioopt     
         0
*DEFINE_CURVE
14
0.,5.e-4
&tDtoR,5.e-4
&tDtoR1,1.
100.,1.
1000.,1.
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         1         1         1         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         2         1         2         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         3         1         3         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         4         1         4         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         5         1         5         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         7         1         7         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         8         1         8         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         9         1         9         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        10         1        10         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        12         1        12         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        13         1        13         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        14         1        14         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        15         1        15         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        16         1        16         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        17         1        17         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        18         1        18         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        19         1        19         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        20         1        20         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        21         1        21         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        22         1        22         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        23         1        23         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        24         1        24         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        25         1        25         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        26         1        26         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        27         1        27         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        28         1        28         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        29         1        29         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        30         1        30         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        31         1        31         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        32         1        33         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        33         1        33         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
       100         1       100         0         0         0         0         1
*PART
$#                                                                         title
                                                                                
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
       200         1       200         0         0         0         0         1
$
*PART_MOVE
10,0,0,0.0045
$ ****************************************************************************
$ CONTROL
$ ****************************************************************************
*CONTROL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$     1.e-5                                   1.e-6        13
     1.e-5                                                13      
*DEFINE_CURVE
13
0.,1.e-6
&tDtoR,1.e-6
&tDtoR1,1.e-1
100.,1.e-1
1000.,1.e-1
*CONTROL_HOURGLASS
$--------1---------2---------3---------4---------5---------6---------7---------8
$#     ihq        qh  
         6  0.100000
*CONTROL_CONTACT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#  slsfac    rwpnal    islchk    shlthk    penopt    thkchg     orien    enmass
       0.1       1.0         0         0         0         0         0         0
$#  usrstr    usrfrc     nsbcs    interm     xpene     ssthk      ecdt   tiedprj
         0         0         0         0       0.0         0         0         0
$#   sfric     dfric       edc       vfc        th     th_sf    pen_sf      
       0.0       0.0       0.0       0.0       0.0       0.0       0.0
$#  ignore    frceng   skiprwg    outseg   spotstp   spotdel   spothin       
         1         0         0         0         0         0       0.0
$#    isym    nserod    rwgaps    rwgdth     rwksf      icov    swradf    ithoff
         0         0         1       0.0       1.0         0       0.0         0
$#  shledg    pstiff    ithcnt    tdcnof     ftall    unused    shltrw      
         0         0         0         0         0                 0.0
$ ****************************************************************************
$ SPHERE
$ ****************************************************************************
*INITIAL_VELOCITY_RIGID_BODY
$--------1---------2---------3---------4---------5---------6---------7---------8
$      pid        vx        vy        vz       vxr       vyr       vzr      icid
        10        0.        0.       10. 
$*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$     ssid      msid     sstyp     mstyp
$        31        10         3         3
$$#      fs        fd        dc        vc       vdc    penchk        bt        dt
$       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
$      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.
$ ****************************************************************************
$ SOLID TABS
$ ****************************************************************************
*SECTION_SOLID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      sid    elform
         1         1
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
       100   8928.57  200.e+09        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
       200   8928.57  200.e+09        .3
*MAT_RIGID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         e        pr
        10      2000 1.0000E+9  0.050000


*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         1      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         2      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         3      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         4      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         5      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         7      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         8      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         9      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        12      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        13      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        14      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        15      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        16      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        17      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        18      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        19      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        20      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        21      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        22      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        23      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        24      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        25      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        26      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        27      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        28      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        29      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        30      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        31      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        32      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        33      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
         1       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
         2       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
         3       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
         4       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
         5       0.0       0.0       0.0       0.3       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
         7       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
         8       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
         9       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
        12       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*MAT_ADD_EROSION
$#     mid      excl    mxpres     mneps    effeps    voleps    numfip       ncs
        13       0.0       0.0       0.0      0.35       0.0       1.0       1.0
$#  mnpres     sigp1     sigvm     mxeps     epssh     sigth   impulse    failtm
       0.0       0.0      0.00       0.0       0.0       0.0       0.0       0.0
$#    idam         -         -         -         -         -         -    lcregd
         0         0         0         0         0         0         0         0
$#   lcfld      nsff   epsthin    engcrt    radcrt   lceps12   lceps13   lcepsmx
         0        10       0.0       0.0       0.0         0         0         0
$#  dteflt    unused     mxtmp     dtmin     
       0.0                 0.0       0.0
$
$
*DEFINE_CURVE
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp
$test        33         0  1.100000 5.0000E+4     0.000     0.000         0
        33         0  1.100000 1.0000E+3     0.000     0.000         0
$#                a1                  o1
               0.000               0.000
            0.087948            4.800000
            0.163637            9.600000
            0.259893           18.799999
            0.321019           49.360001
            0.500000           138.05350
            0.900000           338.89008
            0.990000           383.89008
            1.010000           1000.0000
$*MAT_024
$$--------1---------2---------3---------4---------5---------6---------7---------8
$         4   2.829e3      1.e9        .2     1.e12                
$                             
$         0
$         0
*DEFINE_CURVE
183
0.,5.
0.035,5.
0.0351,0.
0.2,0.
100.,0.
*COMMENT c:*DEFORMABLE_TO_RIGID_AUTOMATIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$    swset      code     time1     time2
         1         0    &tDtoR
$                                              d2r       r2d
                                                33
         1         
         2         
         3
         4
         5
         7
         8
         9
        10
        12
        13
        14
        15
        16
        17
        18
        19
        20
        21
        22
        23
        24
        25 
        26
        27
        28
        29
        30
        31
        32
        33
       100
       200
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$
$$$$  Define Contacts - Sliding Interfaces
$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$
$...>....1....>....2....>....3....>....4....>....5....>....6....>....7....>....8
$
$*CONTACT_ERODING_SINGLE_SURFACE
*CONTACT_AUTOMATIC_SINGLE_SURFACE_MORTAR
$     ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         0                   5
$       fs        fd        dc        vc       vdc    penchk        bt        dt
      0.08      0.08
$      sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf

$$#    isym    erosop      iadj
$                   1
$$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
$         2                                       3        23
$*CONTACT_AUTOMATIC_SINGLE_SURFACEL_MPP
$,10,
$
$$     ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
$         0
$$  Equating ssid to zero means that all segments are included in the contact
$$  
$$       fs        fd        dc        vc       vdc    penchk        bt        dt
$      0.08      0.08
$$
$$      sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
$
$$#       K      FRAD        H0      LMIN      LMAX      CHLM    BC_FLG      ALGO
$$      1.e9       0.0      1.e9   1.00e-3     5.e-3
$*CONTACT_AUTOMATIC_SINGLE_SURFACE_MORTAR_THERMAL
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
$         0
$$#      fs        fd        dc        vc       vdc    penchk        bt        dt
$       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
$      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
$         2       0.1         0     1.025       2.0        35         0         1
$$#       K      FRAD        H0      LMIN      LMAX      CHLM    BC_FLG      ALGO
$      1.e9       0.0      1.e9   1.00e-3     5.e-3
*END
