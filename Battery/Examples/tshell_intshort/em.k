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
EM: Fall of a sphere on a 10 cells battery
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            ELECTROMAGNETISM                                  $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_CONTROL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    emsol     numls  emdtinit   emdtmax   emtinit    emtend  ncyclFem  ncyclBem
         3                                                        -200      -200
*EM_CONTROL_TIMESTEP
1, &em_dt
*EM_OUTPUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         2         2         2         2                                       0
$      mf2       gmv                                            randle
$                   1                                                 0
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId                              randletype
        11         2      6.e7                                                 1
*EM_MAT_001
        12         1                                                           2
*EM_MAT_001
        13         1                                                           3
*EM_MAT_001
        14         1                                                           4
*EM_MAT_001
        15         2      3.e7                                                 5
*EM_MAT_001
         1         2      1.e7
*EM_MAT_001
         2         2      1.e7
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         1         1         2         1
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
         2         1         2         2
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
         3         1         2         3
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
         4         1         2         4
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
         5         1         2         5
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
         6         1         2         6
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
         7         1         2         7
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
         8         1         2         8
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
         9         1         2         9
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
        10         1         2        10
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
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
        21         2        21
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        22         2        22
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        22                  0.
$*EM_ISOPOTENTIAL_CONNECT
$$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
$         2         4        21        22                 555
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             SHORT CIRCUIT                                    $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_RANDLES_SHORT
$--------1---------2---------3---------4---------5---------6---------7---------8
$ areaType   functId
         3       501
*DEFINE_FUNCTION_TABULATED
$#     fid     definition
       502     (thick,res) pair data
$# title
$--------1---------2---------3---------4---------5---------6---------7---------8
resistanceVsThickSep
                  0.               5.e-5
               1.e-3               5.e-5
               3.e-3               5.e-5
                  2.               5.e-5
                1.e2               5.e-5
*DEFINE_FUNCTION
501
float resistance_short_randle(float time,
                             float x_sep, float y_sep, float z_sep,
                             float x_sen, float y_sen, float z_sen,
                             float x_ccp, float y_ccp, float z_ccp,
                             float x_ccn, float y_ccn, float z_ccn)
{ 
  float distCC;
  float distSEP;
  distCC=sqrt(
     pow((x_ccp-x_ccn),2.)+pow((y_ccp-y_ccn),2.)+pow((z_ccp-z_ccn),2.));
  distSEP=sqrt(
     pow((x_sep-x_sen),2.)+pow((y_sep-y_sen),2.)+pow((z_sep-z_sen),2.));
  if (distCC < 0.000117) {
     return resistanceVsThickSep(distSEP) ;
  } else {
    return -1. ;
  }
}
*DEFINE_CURVE
200
0,50
0.0049,50
0.1,2
*END
