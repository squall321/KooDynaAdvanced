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
$X    Requires LS-DYNA Beta version 132836 (or higher) with double precision 
$X
$X------------------------------------------------------------------------------
$# UNITS: (kg/m/s) 
$X------------------------------------------------------------------------------
$X
*KEYWORD
*TITLE
EM: External short with composite thick shells
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            ELECTROMAGNETISM                                  $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            EM CONTROL/CONTACT                                $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_CONTROL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    emsol     numls  emdtinit   emdtmax   emtinit    emtend  ncyclFem  ncyclBem
         3                                                           2         2
*EM_CONTROL_CONTACT
         1         1         1         1                                  0.0002
*EM_CONTROL_TIMESTEP
1,&em_dt
*EM_CONTACT
         1         1        20        30                                  0.0002
*EM_OUTPUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         2         2         2         2                                       0
$      mf2       gmv                                            randle
$                   1                                                 0
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            EM MAT                                            $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId                              randletype
        11         2      6.e9                                                 1
        12         1                                                           2
        13         1                                                           3
        14         1                                                           4
        15         2      3.e9                                                 5
         1         2      1.e7
         2         2      1.e7
         3         4      1.e7
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            EM RANDLES                                        $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         1         0         2         1
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         2         0         2         2
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         3         0         2         3
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         4         0         2         4
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         5         0         2         5
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         6         0         2         6
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         7         0         2         7
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         8         0         2         8
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         9         0         2         9
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
        10         0         2        10
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            EM ISOPOTENTIALS                                  $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         1         2         1         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         2         2         2         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         3         2         3         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         4         2         4         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         5         2         5         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         6         2         6         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         7         2         7         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         8         2         8         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         9         2         9         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        10         2        10         1
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        11         2        11         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        12         2        12         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        13         2        13         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        14         2        14         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        15         2        15         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        16         2        16         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        17         2        17         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        18         2        18         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        19         2        19         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        20         2        20         5
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        37         2        37
$*EM_ISOPOTENTIAL
$$    isoId   setType     setId  randType
$        22         2        22
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        37                  0.
*END
