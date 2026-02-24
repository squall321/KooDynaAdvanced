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
$X    Requires LS-DYNA Beta (aka Dev) version 144100 (or higher) 
$X                       with double precision 
$X
$X------------------------------------------------------------------------------
$# UNITS: (kg/m/s) 
$X------------------------------------------------------------------------------
$X
*TITLE
EM: Randles circuit order comparison
$ Model Description :
$ This set of input decks aims to show different Randles circuits set up
$ By including the different 'em_batmac_....k' files, the user can choose
$ between definining a Randles circuit of order 0, 1 or 2. 
$ Using em_batmac_rtables shows an example of how to have the Randles circuit 
$ parameters function of Temperature and SOC while em_batmac_rdfunc shows how
$ the classic Randles circuit model can be replaced by the user's own circuit
$ equation and using *DEFINE_FUNCTIONs (in this case, a Randles circuit order 2
$ has been reproduced). 
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
Rrho_foam     2200.
R  E_foam      1.e9
R pr_foam      0.05
R rho_tab      8200.
R   E_tab     2.e11
R  nu_tab       0.3
$
$--- THERMAL
R therm_dt      1.0
$
*PARAMETER
R sigmaTab    5.88e7
R sigmaXXP    8.41e9
R sigmaYYP    8.41e9
R sigmaZZP    8.41e9
R sigmaXXN    4.54e9
R sigmaYYN    4.54e9
R sigmaZZN    4.54e9
R cell_cap       20.
R cell_fac   0.02777
R cell_soc      100.
R  cell_r0      0.02
R cell_r10     0.002
R cell_c10      500.
R cell_r20     0.001
R cell_c20     1000.
R    r_ext      0.05
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             DATABASE                                         $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*DATABASE_BINARY_D3PLOT
$--------1---------2---------3---------4---------5---------6---------7---------8
$#      dt      lcdt      beam     npltc    psetid      
  &dt_plot         0         0         0         0
$#   ioopt     
         0
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
$embatmac_order0.k
$embatmac_order1.k
embatmac_order2.k
strucbatmac.k
*END
