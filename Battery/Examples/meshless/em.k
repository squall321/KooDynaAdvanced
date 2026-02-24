$-----------------------------------------------------------------------------
$
$ Example provided by Pierre (LSTC)
$
$ E-Mail: info@dynamore.de
$ Web: http://www.dynamore.de
$
$ Copyright, 2015 DYNAmore GmbH
$ Copying for non-commercial usage allowed if
$ copy bears this notice completely.
$
$X------------------------------------------------------------------------------
$X
$X 1. Run file as is.
$X    Requires LS-DYNA Beta version 119000 (or higher) with double precision 
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
         3                                                           2         2
*EM_CONTROL_CONTACT
1,1,1,1,,,,0.0002
*EM_CONTROL_TIMESTEP
1,&em_dt
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId                              randletype
        11         1      6.e7                                                 1
        12         1                                                           2
        13         1                                                           3
        14         1                                                           4
        15         1      3.e7                                                 5
         1         2      1.e7
         2         2      1.e7
         3         4      1.e7
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
*SET_PART
30
31
*EM_CONTACT
1,1,20,30,,,,0.0002
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         1         0        
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         2         0        
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         3         0  
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         4         0        
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         5         0       
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         6         0       
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         7         0       
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         8         0       
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
         9         0        
$        Q        cQ   SOCinit    SOCtoU
       20.  2.777e-2      100.      -444
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1         0
$  useSocS   tauSocS  lcidSocS
         0        0.         0
*EM_RANDLES_MESHLESS
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId   rdlArea
        10         0       
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
         1         2         1         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         2         2         2        
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         3         2         3         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         4         2         4         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         5         2         5         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         6         2         6         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         7         2         7         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         8         2         8         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         9         2         9         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        10         2        10         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        11         2        11         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        12         2        12         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        13         2        13         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        14         2        14         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        15         2        15         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        16         2        16         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        17         2        17         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        18         2        18         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        19         2        19         
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        20         2        20        
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
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         5         1        11                   1  
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         3         5         2        12                   2
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         4         5         3        13                   3 
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         5         5         4        14                   4 
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         6         5         5        15                   5 
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         7         5         6        16                   6 
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         8         5         7        17                   7 
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         9         5         8        18                   8 
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
        10         5         9        19                   9
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
        11         5        10        20                  10
$*EM_ISOPOTENTIAL_CONNECT
$$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
$         2         4        21        22                 
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             SHORT CIRCUIT                                    $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$*EM_RANDLE_SHORT
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$ areaType   functId
$         2       501
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
*EM_OUTPUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         4         4         4         4                                       0
$      mf2       gmv                                            randle
$                   1                                                 0
*END
