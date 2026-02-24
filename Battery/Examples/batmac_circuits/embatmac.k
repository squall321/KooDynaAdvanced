*KEYWORD
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            ELECTROMAGNETISM                                  $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_MAT_006
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid     mtype    sigmaP      eosP    sigmaN      eosN
         9         5 &sigmaXXP           &sigmaXXN
*EM_MAT_005
$--------1---------2---------3---------4---------5---------6---------7---------8
$#intramid     mtype   sigmaXX   sigmaYY   sigmaZZ      beta        Cm
         8         5 &sigmaXXP &sigmaYYP &sigmaZZP      0.14      0.01
$--------1---------2---------3---------4---------5---------6---------7---------8
$# sigmaXY   sigmaXZ   sigmaYX   sigmaYZ   sigmaZX   sigmaZY
                                                                   
$--------1---------2---------3---------4---------5---------6---------7---------8
$#extra               sigmaXXb  sigmaYYb  sigmaZZb
                     &sigmaXXN &sigmaYYN &sigmaZZN    
$--------1---------2---------3---------4---------5---------6---------7---------8
$#sigmaXYb  sigmaXZb  sigmaYXb  sigmaYZb  sigmaZXb  sigmaZYb
               
$--------1---------2---------3---------4---------5---------6---------7---------8
$#    AOPT        XP        YP        ZP        A1        A2        A3      MACF
        2.                             0         1                 
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      V1        V2        V3        D1        D2        D3
                                                 1
*EM_MAT_001
$--------1---------2---------3---------4---------5---------6---------7---------8
$   em_mid     mtype     sigma     eosId                              randletype   
        80         4 &sigmaTab   
*EM_RANDLES_BATMAC
$--------1---------2---------3---------4---------5---------6---------7---------8
$#   rdlid   rdltype   rdlarea   ccppart   ccnpart   seppart poselpart negelpart
         4         0         2         8       
$#       q        cq   socinit    soctou      
 &cell_cap   0.02777     100.0      -444
$#   r0cha     r0dis    r10cha    r10dis    c10cha    c10dis      
  &cell_r0  &cell_r0  
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        27         2        27               
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
        28         2        28
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         4         2         4               
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        14         2        14         
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
         5         2         5         5               
*EM_ISOPOTENTIAL
$--------1---------2---------3---------4---------5---------6---------7---------8
$    isoId   setType     setId  randType
        15         2        15         1
*EM_ISOPOTENTIAL_CONNECT
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         5         2        27        28    &r_ext
*EM_ISOPOTENTIAL_CONNECT
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         6         3         4         5      0.00
*EM_ISOPOTENTIAL_CONNECT
$   connid  connType isoPotId1 isoPotId2     R,V,I      lcid
         7         3        14        15      0.00                                                                
*END
