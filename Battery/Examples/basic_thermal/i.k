$-----------------------------------------------------------------------------
$
$ Example provided by Iñaki (LSTC)
$
$
$ Web: https://www.dynaexamples.com/
$
$ Copyright © Livermore Software Technology Corporation
$ Copying for non-commercial usage allowed if
$ copy bears this notice completely.
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
EM: Battery simulation
$Objective : study of normal unit cell discharge in a resistance and check
$ the joule heating
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             PARAMETERS                                       $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*PARAMETER
R    T_end      1500
R  dt_plot        10
$
$--- EM
R    em_dt       2.0
$
$--- STRUC
R struc_dt       0.5
$
$--- THERMAL
R therm_dt       0.5
$
*INCLUDE
mesh.k
*INCLUDE
structure.k
*INCLUDE
em.k
*INCLUDE
thermal.k
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
*END
