*KEYWORD
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            CONTROL                                           $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*CONTROL_TERMINATION
$--------1---------2---------3---------4---------5---------6---------7---------8
$   endtim    endcyc     dtmin    endeng    endmas      
    &T_end
*CONTROL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
 &struc_dt                                                
*CONTROL_SHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$#  wrpang     esort     irnxx    istupd    theory       bwc     miter      proj
 20.000000         0        -1         0         2         2         1         0
$# rotascl    intgrd    lamsht    cstyp6    tshell      
  1.000000         0         4         1         0
$# psstupd   sidt4tu     cntco    itsflg    irquad      
         0         0         0         0         2
$#  nfail1    nfail4   psnfail    keepcs     delfr   drcpsid    drcprm      
         0         0         0         0         0         0  1.000000
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
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                                 CONTACTS                                     $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
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
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
$--------1---------2---------3---------4---------5---------6---------7---------8
$     ssid      msid     sstyp     mstyp
        31        10         3         3
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
       0.2       0.2       0.0       0.0       0.0         0       0.01.00000E20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
      10.0      10.0       0.0       0.0       1.0       1.0       1.0       1.
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                                SPHERE                                        $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*PART
$#                                                                         title
spheresolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        31         3         3         0         0         0         0         3
*SECTION_SOLID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      sid    elform
         3         1
*MAT_RIGID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         e        pr
         3     4000. 1.0000E+9  0.050000


*INITIAL_VELOCITY_RIGID_BODY
$--------1---------2---------3---------4---------5---------6---------7---------8
$      pid        vx        vy        vz       vxr       vyr       vzr      icid
        31        0.        0.     -11.7 
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            SOLID TABS                                        $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        11         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        12         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        13         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        14         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        15         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        16         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        17         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        18         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        19         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        20         1         1         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        21         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        22         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        23         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        24         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        25         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        26         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        27         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        28         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        29         2         2         0         0         0         0         2
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        30         2         2         0         0         0         0         2
*SECTION_SOLID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      sid    elform
         1         1
*SECTION_SOLID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      sid    elform
         2         1
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
         1   8928.57  200.e+09        .3
*MAT_ELASTIC
         2   8928.57  200.e+09        .3
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                                 SHELLS                                       $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         1         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         2         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         3         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         4         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         5         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         6         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         7         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         8         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         9         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*PART_COMPOSITE_TSHELL
$#                                                                         title
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
        10         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1        12    5.4e-5     0.000         1
        13    1.7e-5     0.000         1        14    5.8e-5     0.000         1
        15    2.8e-5     0.000         1        14    5.8e-5     0.000         1
        13    1.7e-5     0.000         1        12    5.4e-5     0.000         1
        11    2.4e-5     0.000         1
*MAT_CRUSHABLE_FOAM_TITLE
$--------1---------2---------3---------4---------5---------6---------7---------8
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        11      2223 1.0000E+9  0.050000        33 3.0000E+9  0.100000
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
*DEFINE_CURVE
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp
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
*BOUNDARY_SPC_SET
$--------1---------2---------3---------4---------5---------6---------7---------8
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        31         0         1         1         1         1         1         1
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        32         0         1         1         1         1         1         1
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        33         0         1         1         1         1         1         1
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        34         0         1         1         1         1         1         1
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
        35         0         1         1         1         1         1         1
*SET_PART
1
1
*SET_PART
2
2
*SET_PART
3
3
*SET_PART
4
4
*SET_PART
5
5
*SET_PART
6
6
*SET_PART
7
7
*SET_PART
8
8
*SET_PART
9
9
*SET_PART
10
10
*SET_PART
20
11,12,13,14,15,16,17,18
19,20,21,22,23,24,25,26
27,28,29,30
*END
