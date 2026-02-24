*KEYWORD
*TITLE
EM: Battery simulation
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                              THERMAL                                         $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*CONTROL_SOLUTION
$--------1---------2---------3---------4---------5---------6---------7---------8
$     soln
         2
*CONTROL_THERMAL_SOLVER
$--------1---------2---------3---------4---------5---------6---------7---------8
$    atype     ptype    solver     cgtol       gpt    eqheat     fwork       sbc
         1         0        11    1.e-06         8       1.0       1.0       0.0
$   msglvl    maxitr    abstol    reltol     omega                           tsf
         0       500   1.0e-10    1.0e-4       1.0                           1.0
*CONTROL_THERMAL_TIMESTEP
$--------1---------2---------3---------4---------5---------6---------7---------8
$       ts       tip       its      tmin      tmax     dtemp      tscp      lcts
         0        1. &therm_dt &therm_dt &therm_dt        1.       0.5         0
*INITIAL_TEMPERATURE_SET
$--------1---------2---------3---------4---------5---------6---------7---------8
$      nid      temp 
         0       25.
*MAT_THERMAL_ISOTROPIC
$--------1---------2---------3---------4---------5---------6---------7---------8
$     tmid       tro     tgrlc    tgmult      tlat      hlat    
         1    8930.0       0.0       0.0       0.0       0.0
$       hc        tc  
     386.0       200
*END
