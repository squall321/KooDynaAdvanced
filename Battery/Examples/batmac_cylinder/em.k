*KEYWORD
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType randlArea  ccp/psid
         1         1         2         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$        q        cq   socinit    soctou
       15.  2.777e-2    100.00      -200
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
$      -110      -120      -130      -140      -150      -160
      0.05      0.05     0.008     0.008      110.      110.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
     25.00         0         1
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS      SocS
         0     
*EM_CONTROL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    emsol     numls  emdtinit   emdtmax   emtinit    emtend  ncyclFem  ncyclBem
         1                1.e2                                      10      5000
*EM_CONTROL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$   TSTYPE   DTCONST      LCID    FACTOR     DTMIN     DTMAX
         1        1.        
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         1         2      1301         6
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         2         2      1401         6
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         3         2       101         6
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         4         2      1201         6
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         5         2         1         1
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         6         2      1001         5
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         2         3         2                  0.
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         1         4         2         1      5.e1
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         3         1         3         5       0.0         0
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         4         1         4         6       0.0         0
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId          
        11         2    3.77e4
        13         1
        14         1
        15         2    5.95e4
        16         2    3.77e4
        17         2    5.95e4
*PARAMETER
R sigmaXXP    669.48
R sigmaYYP    669.48
R sigmaZZP    669.48
R sigmaXXN   1761.32
R sigmaYYN   1761.32
R sigmaZZN   1761.32
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
        12         5 &sigmaXXP           &sigmaXXN 
$*EM_EOS_TABULATED1
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$    eosid     mtype           
$         1        34    
$*EM_EOS_TABULATED1
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$    eosid     mtype           
$         2        35    
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ short circuit
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*EM_RANDLE_SHORT
$--------1---------2---------3---------4---------5---------6---------7---------8
$ areaType   functId
         1       501
*DEFINE_FUNCTION_TABULATED
$#     fid     definition
       502     (thickness,res) pair data
$# title
$--------1---------2---------3---------4---------5---------6---------7---------8
resistanceVsThickSep
$#             thick                 res
                  0.               100.0
                1.e2               100.0 
*DEFINE_FUNCTION
501
float resistance_short_randle(float time,
                             float x_sep, float y_sep, float z_sep,
                             float x_sen, float y_sen, float z_sen,
                             float x_ccp, float y_ccp, float z_ccp,
                             float x_ccn, float y_ccn, float z_ccn,
                             float pres, float rho, float vmstress,
                             float cond, float temp, float efstrain)
{ 
  float distCC;
  float distSEP;
  distCC=sqrt(
     pow((x_ccp-x_ccn),2.)+pow((y_ccp-y_ccn),2.)+pow((z_ccp-z_ccn),2.));
  distSEP=sqrt(
     pow((x_sep-x_sen),2.)+pow((y_sep-y_sen),2.)+pow((z_sep-z_sen),2.));
  if (efstrain > 4.5e-2) {
     return 12.0;
  } else {
    return -12. ;
  }
}
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ exothermal reactions
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
*DEFINE_FUNCTION_TABULATED
$#     fid     defintion
       512     (temp,H_release) pair data
$# title
$--------1---------2---------3---------4---------5---------6---------7---------8
H_releaseVsTemp
$#       Temperature           H_release
                  0.               1.e-4
                400.               1.e-4
                600.               1.e-4
               1000.               1.e-4
              10000.               1.e-4
*DEFINE_FUNCTION
511
float exothermic_reaction_randle(float time, float temp, 
                                 float SOC, float H_ex)
{ 
  float H_max=1.;
  if (temp > 400. && H_ex < H_max) {
     return H_releaseVsTemp(temp) ;
  } else {
    return 0. ;
  }
}
*EM_OUTPUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         2         2         2         2
$      mf2       gmv                                            randle
                                                                     0
*END
