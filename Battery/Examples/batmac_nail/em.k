*KEYWORD
*EM_OUTPUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         4         4         4         4                                       0
$      mf2       gmv                                            randle
                                                                     0
*EM_CONTROL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    emsol     numls  emdtinit   emdtmax   emtinit    emtend  ncyclFem  ncyclBem
         3               2.e-5                                    5000      5000
*EM_CONTROL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$   tstype    dtcons      lcid    factor
         2     2.e-5        26
*EM_CONTROL_EROSION
1
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ em_mat definitions
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId                              randletype
       100         4      1.e6
*EM_MAT_001
       200         4      2.e6
*EM_MAT_001
        10         1
*PARAMETER
R  sigmaXX      5.e5
R  sigmaYY      5.e5
R  sigmaZZ      5.e5
$
$
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         1         5  &sigmaXX            &sigmaXX
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         2         5  &sigmaXX            &sigmaXX    
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         3         5  &sigmaXX            &sigmaXX    
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         4         5  &sigmaXX            &sigmaXX    
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         5         5  &sigmaXX            &sigmaXX    
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         7         5  &sigmaXX            &sigmaXX    
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         8         5  &sigmaXX            &sigmaXX    
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         9         5  &sigmaXX            &sigmaXX    
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
        12         5  &sigmaXX            &sigmaXX    
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
        13         5  &sigmaXX            &sigmaXX             
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
7
7
*SET_PART
8
8
*SET_PART
9
9
*SET_PART
12
12
*SET_PART
13
13
*SET_PART
14
14
*SET_PART
15
15
*SET_PART
16
16
*SET_PART
17
17
*SET_PART
18
18
*SET_PART
19
19
*SET_PART
20
20
*SET_PART
21
21
*SET_PART
22
22
*SET_PART
23
23
*SET_PART
24
24
*SET_PART
25
25
*SET_PART
26
26
*SET_PART
27
27
*SET_PART
28
28
*SET_PART
29
29
*SET_PART
30
30
*SET_PART
31
31
*SET_PART
32
32
*SET_PART
33
33
*SET_PART
100
1,2,3,4,5,7,8,9
12,13
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         1         1         3       100
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
     0.845  2.777e-2      100.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
       25.         1         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
         0
$  shortId
         1
$*EM_RANDLES_MESHLESS
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$ randleId randlType partSetId   rdlArea
$         2         0        
$$        Q        cQ   SOCinit    SOCtoU
$       20.  2.777e-2      100.      -444
$$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
$      0.02      0.02     0.008     0.008      110.      110.
$$     temp fromTherm r0ToTherm      dUdT
$       25.         0         1         0
$$  useSocS   tauSocS  lcidSocS
$         0        0.         0
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ isopotentials
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        11         2        11         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        12         2        12         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        13         2        13         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        14         2        14         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        15         2        15         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        16         2        16         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        17         2        17         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        18         2        18         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        19         2        19         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        20         2        20         1
$
$
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       201         2       201    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       202         2       202    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       203         2       203    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       204         2       204    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       205         2       205    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       206         2       206    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       207         2       207    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       208         2       208    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       209         2       209    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       210         2       210    
$
$
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       101         2       101         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       102         2       102         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       103         2       103         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       104         2       104         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       105         2       105         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       106         2       106         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       107         2       107         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       108         2       108         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       109         2       109         5
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       110         2       110         5
$
$
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       301         2       301    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       302         2       302    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       303         2       303    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       304         2       304    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       305         2       305    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       306         2       306    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       307         2       307    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       308         2       308    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       309         2       309    
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       310         2       310
$
$
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       401         2       401         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
       501         2       501         
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ isopotentials_connect
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        11       201                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        12       202                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        13       203                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        14       204                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        15       205                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        16       206                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        17       207                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        18       208                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        19       209                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         3        20       210                  0.
$
$
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       101       301      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       102       302      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       103       303      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       104       304      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       105       305      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       106       306      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       107       307      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       108       308      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       109       309      0.00
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3       110       310      0.00
$
$ meshless
$*EM_ISOPOTENTIAL_CONNECT
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
$         1         5        21       101                   2  
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ short circuit
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_RANDLES_SHORT_ID
$--------1---------2---------3---------4---------5---------6---------7---------8
$  shortId      type  areaType      lcid
         1                   3       501
$*EM_RANDLE_SHORT
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$ areaType   functId
$         3       501
*DEFINE_FUNCTION_TABULATED
$#     fid     definition
       502     (thick,res) pair data
$# title
$--------1---------2---------3---------4---------5---------6---------7---------8
resistanceVsThickSep
$#            strain                 res
                  0.               1.e9
                2.e4               1.e9
              2.01e4               1.e-2
              3.00e4               1.e-5
                3.e9               1.e-5
*DEFINE_FUNCTION
501
float resistance_short_randle(float time,
                             float x_sep, float y_sep, float z_sep,
                             float x_sen, float y_sen, float z_sen,
                             float x_ccp, float y_ccp, float z_ccp,
                             float x_ccn, float y_ccn, float z_ccn,
                             float pres, float rho, float vmstress,
                             float cond, float temp, float efstrain,
                             float ero)
{
  if (ero > 0.5) {
     return 1.e-1 ;
  } else {
    return -1. ;
  }
}
*end
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ exothermal reactions
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$*EM_RANDLES_EXOTHERMIC_REACTION
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$  setPart   functId
$         1       611
*DEFINE_FUNCTION_TABULATED
$#     fid     defintion
       612     (temp,H_release) pair data
$# title
$--------1---------2---------3---------4---------5---------6---------7---------8
H_releaseVsTemp
$#       Temperature           H_release
                  0.               1.e+2
                400.               1.e+2
                600.               1.e+2
               1000.               1.e+2
              10000.               1.e+2
*DEFINE_FUNCTION
611
float exothermic_reaction_randle(float time, float temp, 
                                 float SOC, float H_ex)
{ 
  float H_max=1.e5;	
  if (temp > 26.3 && H_ex < H_max) {
     return H_releaseVsTemp(temp) ;
  } else {
    return 0. ;
  }
}
*END
