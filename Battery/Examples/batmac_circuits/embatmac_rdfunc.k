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
         4        -1         2         8       
$#       q        cq   socinit    soctou      
     
$#   r0cha     r0dis    r10cha    r10dis    c10cha    c10dis      
       -10       -11
$ The following two define functions show how a Randles circuit order 2  
$ can be defined using a user-defined-circuit. Define function 10
$ defines the term sent to the left hand side of the stiffness matrix 
$ (unit : resistance)
$ while Define function 11 defines the term sent to the right hand side
$ of the stiffness matrix (unit: current)
*DEFINE_FUNCTION
10
float randleLHS(float time,float efstrain,
                             float x_sep, float y_sep, float z_sep,
                             float x_sen, float y_sen, float z_sen,
                             float x_ccp, float y_ccp, float z_ccp,
                             float x_ccn, float y_ccn, float z_ccn,
                             float areaCircuit, float areaCell,float soc)
{ 
  float r00;
  float factor;
  r00=0.02;
  factor=areaCircuit/areaCell;
  return 1./(factor*1./r00) ;
} 
*DEFINE_FUNCTION
11
$ save1, save2 and save3 are internal variables
$ that are locally saved by the define_function
$ (up to save10)
$ save1 represents the SOC
$ save2 represents the Vc
$ save3 represents the Vc2
float randleRHS(float time,float efstrain,
                             float x_sep, float y_sep, float z_sep,
                             float x_sen, float y_sen, float z_sen,
                             float x_ccp, float y_ccp, float z_ccp,
                             float x_ccn, float y_ccn, float z_ccn,
                             float areaCircuit, float areaCell,
                             float emdt, float current, float soc,
                             float *save1, float *save2, float *save3)
{ 
  float u0;
  float volt;
  float factor;
  float Q;
  float Cq;
  float r00;
  float c10;
  float r10;
  float c20;
  float r20;
  float rhs;
  u0=4.15;
  r00=0.02;
  Q=20.;
  r10=0.002;
  c10=500.;
  r20=0.001;
  c20=1000.;
  Cq=1./36.;
  float vc=0.;
  float vc2=0.;
  factor=areaCircuit/areaCell;
  Q=factor*Q;
  r10=r10/factor;
  c10=factor*c10;
  r20=r20/factor;
  c20=factor*c20;
  r00=r00/factor;
  *save1=*save1-emdt*current*cq/Q;
  if(time<emdt){
  *save1=100;
  *save2=0.;
  *save3=0.;
  rhs=u0/(r00);
  return rhs;}
  *save2=(*save2-r10*current)*exp(-emdt/(r10*c10))+current*r10;
  *save3=(*save3-r20*current)*exp(-emdt/(r20*c20))+current*r20;
  if (*save1>10.){
   volt=3.6+0.55*(*save1)/100.;
   rhs=(volt-*save2-*save3)/(r00);
   return rhs;}
   if (*save1<0.){
     volt=2.8;
     return 0.;}
   volt=2.8+0.855*(*save1)/10.;
   rhs=(volt-*save2-*save3)/(r00);
   return rhs; 
}  
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
