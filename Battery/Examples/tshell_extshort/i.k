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
$X------------------------------------------------------------------------------
$# UNITS: (kg/m/s) 
$X------------------------------------------------------------------------------
$X
*KEYWORD
*TITLE
EM: External short with composite thick shells
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             PARAMETERS                                       $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*PARAMETER
R    T_end      100.
R  dt_plot       2.0
$
$--- EM
R    em_dt       1.
$
$--- STRUC
R struc_dt      0.1
$
$--- THERMAL
R therm_dt      1.0
$
*INCLUDE
mesh4.k
*INCLUDE
structure.k
*INCLUDE
em.k
*INCLUDE
thermal.k
*INCLUDE
uVsSoc.k
*INCLUDE
current.k
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             DATABASE                                         $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*DATABASE_ELOUT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt    binary      lcur     ioopt   option1   option2   option3   option4
  0.500000         0         0         1         0         0         0         0
*DATABASE_GLSTAT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt    binary      lcur     ioopt     
  0.500000         0         0         1
*DATABASE_SPCFORC
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt    binary      lcur     ioopt     
  0.500000         0         0         1
*DATABASE_BINARY_D3PLOT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt      lcdt      beam     npltc    psetid      
  &dt_plot         0         0         0         0
$#   ioopt     
         0
*DATABASE_EXTENT_BINARY
$--------1---------2---------3---------4---------5---------6---------7---------8
$#   neiph     neips    maxint    strflg    sigflg    epsflg    rltflg    engflg
         0         0         4         1         1         1         1         1
$#  cmpflg    ieverp    beamip     dcomp      shge     stssz    n3thdt   ialemat
         0         0         0         1         1         1         2         1
$# nintsld   pkp_sen      sclp     hydro     msscl     therm    intout    nodout
         0         0  1.000000         0         0         0ALL       ALL
$#    dtdt    resplt      
         0         0
*DATABASE_HISTORY_TSHELL
$--------1---------2---------3---------4---------5---------6---------7---------8
$#     id1       id2       id3       id4       id5       id6       id7       id8
         1         0         0         0         0         0         0         0
*END
