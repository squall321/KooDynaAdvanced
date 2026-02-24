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
$X    Requires LS-DYNA Beta version 132836 (or higher) with double precision 
$X
$X------------------------------------------------------------------------------
$# UNITS: (kg/m/s) 
$X------------------------------------------------------------------------------
$X
*TITLE
EM: Randles circuits parameters function of SOC and Temperature
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             PARAMETERS                                       $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*PARAMETER
R    T_end     1400.
R  dt_plot       5.0
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
*PARAMETER
R sigmaXXP    8.41e9
R sigmaYYP    8.41e9
R sigmaZZP    8.41e9
R sigmaXXN    4.54e9
R sigmaYYN    4.54e9
R sigmaZZN    4.54e9
$R sigmaXXP    5.88e7
$R sigmaYYP    5.88e7
$R sigmaZZP    5.88e7
$R sigmaXXN    3.70e7
$R sigmaYYN    3.70e7
$R sigmaZZN    3.70e7
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
$*DATABASE_HISTORY_TSHELL
$$--------1---------2---------3---------4---------5---------6---------7---------8
$$#     id1       id2       id3       id4       id5       id6       id7       id8
$         1         0         0         0         0         0         0         0
*INCLUDE
uVsSoc.k
*INCLUDE
current.k
*INCLUDE
main_struc.k
main_em.k
*INCLUDE
embatmac.k
strucbatmac.k
r0_chg.k
r0_dschg.k
c10_chg.k
c10_dschg.k
r10_chg.k
r10_dschg.k
*END
