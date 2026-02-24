*KEYWORD
*INCLUDE
soc.k
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            ELECTROMAGNETISM                                  $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_CONTROL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    emsol     numls  emdtinit   emdtmax   emtinit    emtend  ncyclFem  ncyclBem
         3              &em_dt                                    5000      5000
*EM_RANDLES_SOLID
$--------1---------2---------3---------4---------5---------6---------7---------8
$#   rdlid   rdltype   rdlarea   ccppart   ccnpart   seppart poselpart negelpart
         1         0         2         1         5         3         2         4
$#       q        cq   socinit    soctou      
       20.   0.02777     100.0      -444
$#   r0cha     r0dis    r10cha    r10dis    c10cha    c10dis      
      0.02      0.02   0.00001   0.00001     500.0     500.0
$#    temp   frtherm    r0toth      dudt     tempu     
      25.0         0         1       0.0         0
$# usesocs   tausocs  sicslcid        
         1      1000      -400    
*DEFINE_CURVE
400
0,20
1000,20     
*DEFINE_CURVE
$uVsSoc
444
0,2.8
10,3.655
100,4.15
200,4.15
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$#   isoid   settype     setid     
         1         2         1
*EM_ISOPOTENTIAL
$#   isoid   settype     setid     
         2         2         2
*EM_ISOPOTENTIAL
$#   isoid   settype     setid     
         3         2         3
*EM_ISOPOTENTIAL
$#   isoid   settype     setid     
         4         2         4
*EM_ISOPOTENTIAL_CONNECT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#   conid   contype    isoid1    isoid2       val      lcid    
         1         2         1         2      0.05        
$*EM_ISOPOTENTIAL_CONNECT
$$#   conid   contype    isoid1    isoid2       val      lcid    
$         2         3         2         0       0.0         
*DEFINE_CURVE
$currentVsTime
555                              
0.,-200
20.,-200
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId          
         1         2    5.88e7
         2         1    
         3         1
         4         1
         5         2    3.70e7
*EM_OUTPUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         2         2         2         2                                       0
$      mf2       gmv                                            randle
$                                                                     0
*END
