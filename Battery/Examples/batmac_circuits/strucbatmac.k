*KEYWORD
*INCLUDE
meshbatmac.k
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                            SOLID TABS                                        $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*SET_PART
8
8
*PART
$#                                                                         title
ccp                                                                            
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         8        80         9         0         0         0         0         1
*PART
$#                                                                         title
positive tab                                                  
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        14        80        80         0         0         0         0         1
*PART
$#                                                                         title
negative tab                                                       
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        24        80        80         0         0         0         0         1              
*SECTION_SOLID
$--------1---------2---------3---------4---------5---------6---------7---------8
$      sid    elform
        80         1
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         8 &rho_foam   &E_foam  &pr_foam        33 3.0000E+9  0.100000
*MAT_CRUSHABLE_FOAM_TITLE
Cu active
$#     mid        ro         e        pr      lcid       tsc      damp
         9 &rho_foam   &E_foam  &pr_foam        33 3.0000E+9  0.100000
*MAT_RIGID
        80  &rho_tab    &E_tab   &nu_tab
1,7,7

*END
