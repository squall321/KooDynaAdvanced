*KEYWORD
*TITLE
EM: Battery simulation
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            CONTROL                                           $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*CONTROL_TERMINATION
$--------1---------2---------3---------4---------5---------6---------7---------8
$   endtim    endcyc     dtmin    endeng    endmas      
    &T_end
*CONTROL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$   dtinit                                   dt2ms      lctm
 &struc_dt                               &struc_dt         1
*DEFINE_CURVE
1
0.,&struc_dt
10.,&struc_dt
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                               CELL                                           $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*SECTION_SOLID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      sid    elform
         1         1
*PART
$#                                                                         title
ccp                                                                            
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         1         1         1         0         0         0         0         1
*PART
$#                                                                         title
cathode                                                                        
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         2         1         2         0         0         0         0         1
*PART
$#                                                                         title
separator                                                                      
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         3         1         3         0         0         0         0         1
*PART
$#                                                                         title
anode                                                                       
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         4         1         4         0         0         0         0         1
*PART
$#                                                                         title
ccn                                                                    
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         5         1         5         0         0         0         0         1
*PART
$#                                                                         title
positive tab                                                  
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         6         1         1         0         0         0         0         1
*PART
$#                                                                         title
negative tab                                                       
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         7         1         5         0         0         0         0         1
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         e        pr       
         1      8930  200.e+09        .3
*MAT_ELASTIC
         2      4880  200.e+09        .3
*MAT_ELASTIC
         3      4880  200.e+09        .3
*MAT_ELASTIC
         4      4880  200.e+09        .3
*MAT_ELASTIC
         5      2700  200.e+09        .3 
*END