*KEYWORD
*EM_CONTROL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    emsol     numls  emdtinit   emdtmax   emtinit    emtend  ncyclFem  ncyclBem
         3                                                          10        10
*EM_CONTROL_TIMESTEP
1,5.e-4
*EM_OUTPUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         2         2         2         2                                       0
$      mf2       gmv                                            randle
                                                                     0
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ em_mat definitions
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId                              randletype
         1         4      1.e6
*EM_MAT_001
         2         4      2.e6
*EM_MAT_001
         3         1
*PARAMETER
R  sigmaXX      5.e5
R  sigmaYY      5.e5
R  sigmaZZ      5.e5
*EM_MAT_006
         4        5   &sigmaXX            &sigmaZZ
*EM_MAT_005
$--------1---------2---------3---------4---------5---------6---------7---------8
$#intramid     mtype   sigmaXX   sigmaYY   sigmaZZ      beta        Cm
        40         5  &sigmaXX  &sigmaYY  &sigmaZZ      0.14      0.01
$--------1---------2---------3---------4---------5---------6---------7---------8
$# sigmaXY   sigmaXZ   sigmaYX   sigmaYZ   sigmaZX   sigmaZY
                                                                   
$--------1---------2---------3---------4---------5---------6---------7---------8
$#extra               sigmaXXb  sigmaYYb  sigmaZZb
                      &sigmaXX  &sigmaYY  &sigmaZZ    
$--------1---------2---------3---------4---------5---------6---------7---------8
$#sigmaXYb  sigmaXZb  sigmaYXb  sigmaYZb  sigmaZXb  sigmaZYb
               
$--------1---------2---------3---------4---------5---------6---------7---------8
$#    AOPT        XP        YP        ZP        A1        A2        A3      MACF
        2.                             0         1                 
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      V1        V2        V3        D1        D2        D3
                                                 1
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ battery
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
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
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         1         1         2         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         2         1         2         2
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         3         1         2         3
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         4         1         2         4
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         5         1         2         5
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         6         1         2         6
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         7         1         2         7
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         8         1         2         8
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         9         1         2         9
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
        10         1         2        10
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ isopotentials
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         1         2         1         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         2         2         2         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         3         2         3         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         4         2         4         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         5         2         5         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         6         2         6         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         7         2         7         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         8         2         8         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         9         2         9         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        10         2        10         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        11         2        11         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        12         2        12         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        13         2        13         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        14         2        14         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        15         2        15         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        16         2        16         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        17         2        17         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        18         2        18         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        19         2        19         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        20         2        20         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        21         2        21         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        22         2        22         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        23         2        23         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        24         2        24         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        25         2        25         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        26         2        26         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        27         2        27         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        28         2        28         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        29         2        29         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        30         2        30         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        31         2        31         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        32         2        32         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        33         2        33         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        34         2        34         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        35         2        35         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        36         2        36         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        37         2        37         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        38         2        38         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        39         2        39         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        40         2        40         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        41         2        41         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        42         2        42         
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ isopotentials_connect
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        42                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         2        41        42     0.001
$         2         4        41        42                 555
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         3         1         1        21       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         4         1         2        22       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         5         1         3        23       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         6         1         4        24       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         7         1         5        25       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         8         1         6        26       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         9         1         7        27       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        10         1         8        28       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        11         1         9        29       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        12         1        10        30       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        13         1        11        31       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        14         1        12        32       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        15         1        13        33       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        16         1        14        34       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        17         1        15        35       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        18         1        16        36       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        19         1        17        37       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        20         1        18        38       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        21         1        19        39       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
        22         1        20        40       0.0         0
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ short circuit
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_RANDLE_SHORT
$--------1---------2---------3---------4---------5---------6---------7---------8
$ areaType   functId
         3       501
*DEFINE_FUNCTION_TABULATED
$#     fid     definition
       502     (thick,res) pair data
$# title
$--------1---------2---------3---------4---------5---------6---------7---------8
resistanceVsThickSep
$#             thick                 res
$                  0.               5.e-3
$               1.e-3               5.e-3
$               3.e-3               5.e-3
$                  2.               5.e-3
$                1.e2               5.e-3
                  0.               1.e-3
               1.e-3               1.e-3
               3.e-3               1.e-3
                  2.               1.e-3
                1.e2               1.e-3
*DEFINE_FUNCTION
501
float resistance_short_randle(float time,float efstrain,
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
  if (efstrain > 0.25) {
     return 0.1 ;
  } else {
    return -0.1 ;
  }
}
*END
