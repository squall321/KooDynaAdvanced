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
$X    Requires LS-DYNA Beta version 141900 (or higher) with double precision 
$X
$ Cyindrical battery model modelled using composite thick shells undergoing
$ an internal short
*INCLUDE
mesh.k  
$ ****************************************************************************
$ UNITS: kg/m/s
$ ****************************************************************************
$ ****************************************************************************
$ CONTROL
$ ****************************************************************************
*CONTROL_TERMINATION
$--------1---------2---------3---------4---------5---------6---------7---------8
$   endtim
         5
*CONTROL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$   dtinit                                   dt2ms      lctm
     1.e-2                                   1.e-2         1
*DEFINE_CURVE
1
0.,1.e-2
10.,1.e-2
*DATABASE_BINARY_D3PLOT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt      lcdt      beam     npltc    psetid      
     2.e-2         0         0         0         0
$#   ioopt     
         0
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
         0        1.     1.e-2     1.e-2     1.e-2        1.       0.5         0
*INITIAL_TEMPERATURE_SET
$--------1---------2---------3---------4---------5---------6---------7---------8
$      nid      temp 
         0       25.
*MAT_THERMAL_ISOTROPIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$     tmid       tro     tgrlc    tgmult      tlat      hlat    
         1     2223.       0.0       0.0       0.0       0.0
$       hc        tc  
     1420.        3.
$ ****************************************************************************
$ CELL
$ ****************************************************************************
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         3         1         3         0         0         0         0         1
*PART
$#                                                                         title
boxsolid
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         4         1         4         0         0         0         0         1
*CONTROL_SHELL
$#  wrpang     esort     irnxx    istupd    theory       bwc     miter      proj
 20.000000         0        -1         0         2         2         1         0
$# rotascl    intgrd    lamsht    cstyp6    tshell      
  1.000000         0         4         1         0
$# psstupd   sidt4tu     cntco    itsflg    irquad      
         0         0         0         0         2
$#  nfail1    nfail4   psnfail    keepcs     delfr   drcpsid    drcprm      
         0         0         0         0         0         0  1.000000
*PART_COMPOSITE_TSHELL
Layered_Solid
$#     pid    elform      shrf    unused    unused      hgid    unused    tshear
         2         5  0.833000                             0                   0
$#    mid1    thick1        b1    ithid1      mid2    thick2        b2    ithid2
        12    0.5e-3     0.000         1        11    0.8e-3     0.000         1
        12    0.5e-3     0.000         1        13    0.2e-3     0.000         1
        14    0.5e-3     0.000         1        15    0.8e-3     0.000         1
        14    0.5e-3     0.000         1        13    0.2e-3     0.000         1
        12    0.5e-3     0.000         1        11    0.8e-3     0.000         1
        12    0.5e-3     0.000         1        13    0.2e-3     0.000         1
        14    0.5e-3     0.000         1        15    0.8e-3     0.000         1
        14    0.5e-3     0.000         1        13    0.2e-3     0.000         1
*SECTION_SOLID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      sid    elform
         1         1
*MAT_ELASTIC   
         3     2223.    1.e+09        .3
*MAT_ELASTIC
         4     2223.    1.e+09        .3 
*MAT_CRUSHABLE_FOAM_TITLE
$--------1---------2---------3---------4---------5---------6---------7---------8
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        11     2223. 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        12     2223. 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        13     2223. 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        14     2223. 1.0000E+9  0.050000        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
        15     2223. 1.0000E+9  0.050000        33 3.0000E+9  0.100000
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
$ ****************************************************************************
$ MECA
$ ****************************************************************************
*BOUNDARY_PRESCRIBED_MOTION_SET
$#    nsid       dof       vad      lcid        sf       vid     death     birth
         6         2         2        49  1.000000         01.0000E+28     0.000
*DEFINE_CURVE
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp
        49         0  1.000000         2     0.000     0.000         0
$#                a1                  o1
               0.000                  0.
                  1.             -0.1e-3
                  2.             -1.0e-3 
                 10.             -1.0e-3              
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
         7         0         1         1         1         1         1         1
$ ****************************************************************************
$ ELECTROMAGMETISM
$ ****************************************************************************
*EM_CONTROL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    emsol     numls  emdtinit  
         3                                                           5         5
*EM_CONTROL_TIMESTEP
1,1.e-2                                     
*SET_PART
10
2
*EM_RANDLES_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$ randleId randlType partSetId  areaType
         1         1         2        10
$--------1---------2---------3---------4---------5---------6---------7---------8
$        Q        cQ   SOCinit    SOCtoU
        1.     3.e-2       10.      -444
$--------1---------2---------3---------4---------5---------6---------7---------8
$    r0cha     r0dis    r10cha    r10dis    c10cha    c10dis
      0.02      0.02     0.008     0.008      100.      100.
$--------1---------2---------3---------4---------5---------6---------7---------8
$     temp fromTherm r0ToTherm      dUdT
$       25.                   1  
$--------1---------2---------3---------4---------5---------6---------7---------8
$  useSocS   tauSocS  lcidSocS
$         0
*DEFINE_CURVE
$uVsSoc
444
0.,3.
1.,3.2
100,4.
200,4.
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$#   isoid   settype     setid  randType    
         1         2         1         
*EM_ISOPOTENTIAL
$#   isoid   settype     setid     
         2         2         2         
*EM_ISOPOTENTIAL
$#   isoid   settype     setid     
         3         2         3         5         
*EM_ISOPOTENTIAL
$#   isoid   settype     setid     
         4         2         4         1 
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         1         2         1                0.05  
$*EM_ISOPOTENTIAL_CONNECT
$$#   conid   contype    isoid1    isoid2       val      lcid    
$         1         4         1                           555  
*EM_ISOPOTENTIAL_CONNECT
$#   conid   contype    isoid1    isoid2       val      lcid    
         2         3         2         0       0.0         0
*DEFINE_CURVE
$currentVsTime
555                              
0.,200.
20.,200.
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId                              randletype
        11         2    5.88e7                                                 1
*EM_MAT_001
        12         1                                                           2
*EM_MAT_001
        13         1                                                           3
*EM_MAT_001
        14         1                                                           4
*EM_MAT_001
        15         2    3.70e7                                                 5
*EM_MAT_001
         3         2    5.88e7
*EM_MAT_001
         4         2    3.70e7
*EM_OUTPUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         2         2         2         2                                       0
$      mf2       gmv                                            randle
$                   1                                                 0
*EM_RANDLES_SHORT
$--------1---------2---------3---------4---------5---------6---------7---------8
$ areaType   functId
         1       501
*DEFINE_FUNCTION_TABULATED
$#     fid     definition
       502     (thick,res) pair data
$# title
$--------1---------2---------3---------4---------5---------6---------7---------8
resistanceVsThickSep
$#             thick                 res
                  0.               2.e-3
              0.2e-3		   2.e-3
               1.e-3               2.e-3
                 0.1               2.e-3
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
  if (distCC < 1.e-3) {
     return resistanceVsThickSep(distSEP) ;
  } else {
    return -1. ;
  }
}
*END
