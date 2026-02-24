*KEYWORD
$-----------------------------------------------------------------------------
$
$ Example provided by Iñaki (LSTC)
$
$
$ Web: https://www.dynaexamples.com/
$
$ Copyright © Livermore Software Technology Corporation
$ Copying for non-commercial usage allowed if
$ copy bears this notice completely
$
$X------------------------------------------------------------------------------
$X
$X 1. Run file as is.
$X    Requires LS-DYNA Beta version 143000 (or higher) with double precision 
$X
$X------------------------------------------------------------------------------
$# UNITS: (kg/m/s) 
$X------------------------------------------------------------------------------
$X
*TITLE
Fall of a sphere on a 10 cells battery using batmac randles cells
*INCLUDE
mesh.k
em.k
uVsSoc.k
current.k
$ ****************************************************************************
$ CONTROL
$ ****************************************************************************
*CONTROL_TERMINATION
$--------1---------2---------3---------4---------5---------6---------7---------8
$#  endtim    endcyc     dtmin    endeng    endmas      
    2.5e-2         0     0.000     0.000
*CONTROL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$     1.e-5                                   1.e-6        13
     1.e-5
*DEFINE_CURVE
13
0.,1.e-6
10.,1.e-6
*DATABASE_ELOUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt    binary      lcur     ioopt   option1   option2   option3   option4
  0.500000         0         0         1         0         0         0         0
*DATABASE_GLSTAT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt    binary      lcur     ioopt     
  0.500000         0         0         1
*DATABASE_SPCFORC
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt    binary      lcur     ioopt     
  0.500000         0         0         1
*DATABASE_BINARY_D3PLOT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt      lcdt      beam     npltc    psetid      
     5.e-4         0         0         0         0
$#   ioopt     
         0
*DATABASE_EXTENT_BINARY
$--------1---------2---------3---------4---------5---------6---------7---------8
$#   neiph     neips    maxint    strflg    sigflg    epsflg    rltflg    engflg
         0         0         4         1         1         1         1         1
$#  cmpflg    ieverp    beamip     dcomp      shge     stssz    n3thdt   ialemat
         0         0         0         1         1         1         2         1
$# nintsld   pkp_sen      sclp     hydro     msscl     therm    intout    nodout
         0         0  1.000000         0         0         0ALL       ALL
$#    dtdt    resplt      
         0         0
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
$ THERMAL
$ ****************************************************************************
*CONTROL_SOLUTION
$--------1---------2---------3---------4---------5---------6---------7---------8
$     soln
         2
*CONTROL_THERMAL_SOLVER
$--------1---------2---------3---------4---------5---------6---------7---------8
$    atype     ptype    solver     cgtol       gpt    eqheat     fwork       sbc
         1         0        11    1.e-06         8       1.0       1.0       0.0
$   msglvl    maxitr    abstol    reltol     omega                           tsf
         0       500   1.0e-10    1.0e-4       1.0                           1.0
*CONTROL_THERMAL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$       ts       tip       its      tmin      tmax     dtemp      tscp      lcts
         0        1.     5.e-4     5.e-4     5.e-4        1.       0.5         0
*INITIAL_TEMPERATURE_SET
$--------1---------2---------3---------4---------5---------6---------7---------8
$      nid      temp 
         0       25.
*MAT_THERMAL_ISOTROPIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$#    tmid       tro     tgrlc    tgmult      tlat      hlat    
         1 7860.0000     0.000     0.000     0.000     0.000
$#      hc        tc  
 460.00000 40.000000
$ ****************************************************************************
$ SPHERE
$ ****************************************************************************
*INITIAL_VELOCITY_RIGID_BODY
$--------1---------2---------3---------4---------5---------6---------7---------8
$      pid        vx        vy        vz       vxr       vyr       vzr      icid
        31        0.        0.      -7.7 
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$--------1---------2---------3---------4---------5---------6---------7---------8
$     ssid      msid     sstyp     mstyp
        31        10         3         3
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.
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
         1   8928.57  200.e+09        .3
*MAT_ELASTIC
         2   8928.57  200.e+09        .3
*MAT_RIGID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         e        pr
         3      4000 1.0000E+9  0.050000


*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         4      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
$pierre         4      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
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
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$--------1---------2---------3---------4---------5---------6---------7---------8
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         1         2         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         2         3         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         3         4         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         4         5         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         5         6         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         6         7         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         7         8         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         8         9         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         9        10         3         3         0         0         0         0
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.0
$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
         2       0.1         0     1.025       2.0         2         0         1
*BOUNDARY_SPC_SET
$--------1---------2---------3---------4---------5---------6---------7---------8
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        51         0         1         1         1         1         1         1
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        52         0         1         1         1         1         1         1
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        53         0         1         1         1         1         1         1
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        54         0         1         1         1         1         1         1
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        55         0         1         1         1         1         1         1
*END
