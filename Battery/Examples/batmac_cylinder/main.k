*KEYWORD
*TITLE
$#                                                                         title
LS-DYNA keyword deck by LS-PrePost
*CONTROL_HOURGLASS
$#     ihq        qh  
         4       0.1
*CONTROL_TERMINATION
$#  endtim    endcyc     dtmin    endeng    endmas     nosol     
     5.0e3         0       0.0       0.01.000000E8         0
*CONTROL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$                                                       LCTM
$#  dtinit    tssfac      isdo    tslimt     dt2ms      lctm     erode     ms1st
       0.0       0.9         0       0.0       0.1         0         0         0
$#  dt2msf   dt2mslc     imscl    unused    unused     rmscl     
       0.0         0         0                           0.0
*DATABASE_ELOUT
$#      dt    binary      lcur     ioopt   option1   option2   option3   option4
        10         3        16         1         0         0         0         0
*DATABASE_GLSTAT
$#      dt    binary      lcur     ioopt     
        10         3        16         1
*DATABASE_RCFORC
$#      dt    binary      lcur     ioopt     
        10         3        16         1
*DATABASE_BINARY_D3PLOT
$#      dt      lcdt      beam     npltc    psetid      
     10.e0                   0         0         0
$       0.1        16         0         0         0
$#   ioopt     
         0
*DATABASE_EXTENT_BINARY
$#   neiph     neips    maxint    strflg    sigflg    epsflg    rltflg    engflg
         0         0       150         1         1         1         1         1
$#  cmpflg    ieverp    beamip     dcomp      shge     stssz    n3thdt   ialemat
         0         0         0         1         1         1         2         1
$# nintsld   pkp_sen      sclp     hydro     msscl     therm    intout    nodout
         0         0       1.0         0         0         0ALL       STRAIN
$#    dtdt    resplt     neipb     
         0         0         0
*DATABASE_FORMAT
$#   iform   ibinary       
         0         1
$*BOUNDARY_SPC_SET_BIRTH_DEATH
$$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
$         7         0         1         1         1         1         1         1
$$#   birth     death     
$     0.4991.00000E20
$*CONTACT_INTERIOR
$$#    psid    
$         1
$*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_ID
$$#     cid                                                                 title
$         1cell_sphere
$$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
$         1       100         0         0         0         0         0         0
$$#      fs        fd        dc        vc       vdc    penchk        bt        dt
$       0.1       0.1       0.0       0.0       0.0         0       0.01.00000E20
$$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
$       1.0       1.0       0.0       0.0       1.0       1.0       1.0       1.0
$$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq
$         2       0.1         0     1.025       3.0         2         0         1
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
        16      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
        17      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
       110      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
       130      4.e6      1.e6        .2
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
       500      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
        11      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
        12      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
        13      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
        14      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
        15      4.e6      1.e6        .3
*MAT_ELASTIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$      mid        ro         E        pr 
       140      4.e6      1.e6        .3
$*MAT_CRUSHABLE_FOAM_TITLE
$Crushable-Foam-Cathode
$$#     mid        ro         e        pr      lcid       tsc      damp    
$        11      4.e6      1.e6      0.01         3       1.0      0.05
$*MAT_CRUSHABLE_FOAM_TITLE
$Crushable-Foam-Cathode
$$#     mid        ro         e        pr      lcid       tsc      damp    
$        12      4.e6      1.e6      0.01         3       1.0      0.05
$*MAT_CRUSHABLE_FOAM_TITLE
$Crushable-Foam-Cathode
$$#     mid        ro         e        pr      lcid       tsc      damp    
$        13      4.e6      1.e6      0.01         3       1.0      0.05
$*MAT_CRUSHABLE_FOAM_TITLE
$Crushable-Foam-Cathode
$$#     mid        ro         e        pr      lcid       tsc      damp    
$        14      4.e6      1.e6      0.01         3       1.0      0.05
$*MAT_CRUSHABLE_FOAM_TITLE
$Crushable-Foam-Cathode
$$#     mid        ro         e        pr      lcid       tsc      damp    
$        15      4.e6      1.e6      0.01         3       1.0      0.05
$*MAT_CRUSHABLE_FOAM_TITLE
$Crushable-Foam-Anode
$$#     mid        ro         e        pr      lcid       tsc      damp    
$       140      4.e6      1.e6      0.01         2       1.0      0.05
*DEFINE_CURVE_TITLE
Stress-Strain-curve
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         2         0       1.0       0.9       0.0       0.0         0         0
$#                a1                  o1  
                 0.0   1.2500000594e-004
              0.0168   3.1599999056e-004
              0.0359   7.2299997555e-004
              0.0539             0.00162
              0.0791               0.003
              0.0911             0.00483
               0.113             0.00694
               0.128             0.00752
               0.137             0.00983
               0.171              0.0145
               0.182              0.0152
               0.199              0.0231
               0.228              0.0259
               0.241               0.029
               0.262              0.0326
               0.271              0.0359
               0.289              0.0394
               0.309              0.0428
               0.322              0.0467
               0.333              0.0502
               0.351              0.0536
               0.362              0.0566
               0.389              0.0594
               0.405              0.0623
               0.423              0.0646
               0.439              0.0664
*DEFINE_CURVE_TITLE
Stress-Strain-curve
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         3         0       1.0       1.1       0.0       0.0         0         0
$#                a1                  o1  
                 0.0   1.2500000594e-004
              0.0168   3.1599999056e-004
              0.0359   7.2299997555e-004
              0.0539             0.00162
              0.0791               0.003
              0.0911             0.00483
               0.113             0.00694
               0.128             0.00752
               0.137             0.00983
               0.171              0.0145
               0.182              0.0152
               0.199              0.0231
               0.228              0.0259
               0.241               0.029
               0.262              0.0326
               0.271              0.0359
               0.289              0.0394
               0.309              0.0428
               0.322              0.0467
               0.333              0.0502
               0.351              0.0536
               0.362              0.0566
*DEFINE_CURVE
15
0.,1.0e-4
0.6,1.0e-4
5.,1.0e-2
1.0e3,1.0
1.e6,1.0
*DEFINE_CURVE
16
0.,0.025
0.50,0.025
1.e3,5.e3
1.e6,5.e3
*INCLUDE                                                                             
uVsSoc.k
em.k
thermal.k
mesh.k
*END
