Config Files
=====================

Config files for accessing variables inside the source code.


DEAP
--------------------------------
DEAP config file list


deap_restraints.ini
.............................

Boundaries and restraints for free Parameters in DEAP
(Path: module/config/`deap_restraints.ini <../configfiles/deap_restraints.ini>`_).

.. deap_restraints:: ao

:id: AO
:blade: 0
:minimum: 0.0
:maximum:  0.1
:default: 0.0271
:digits: 4


.. deap_restraints:: div

:id: dist_blades
:blade: 0
:minimum: 0.51
:maximum: 0.61
:default: 0.56
:digits: 2


.. deap_restraints:: alph11

:id: alpha1
:blade: 1
:minimum: 6.0
:maximum: 28.0
:default: 17.0
:digits: 1


.. deap_restraints:: alph12

:id: alpha2
:blade: 1
:minimum: 2.0
:maximum: 18.0
:default: 7.0
:digits: 1


.. deap_restraints:: alph21

:id: alpha1
:blade: 2
:minimum: 10.0
:maximum: 26.0
:default: 18.0
:digits: 1


.. deap_restraints:: alph22

:id: alpha2
:blade: 2
:minimum: 12.0
:maximum: 32.0
:default: 23.0
:digits: 1


.. deap_restraints:: lambd1

:id: lambd
:blade: 1
:minimum: 40.0
:maximum: 45.0
:default: 43.0
:digits: 1


.. deap_restraints:: lambd2

:id: lambd
:blade: 2
:minimum: 20.0
:maximum: 25.0
:default: 23.0
:digits: 1


.. deap_restraints:: th1

:id: th
:blade: 1
:minimum: 0.0
:maximum: 0.05
:default: 0.0477
:digits: 4


.. deap_restraints:: th2

:id: th
:blade: 2
:minimum: 0.0
:maximum: 0.05
:default: 0.0477
:digits: 4


.. deap_restraints:: xmaxth1

:id: xmax_th
:blade: 1
:minimum: 0.375
:maximum: 0.425
:default: 0.4
:digits: 3


.. deap_restraints:: xmaxth2

:id: xmax_th
:blade: 2
:minimum: 0.375
:maximum: 0.425
:default: 0.4
:digits: 3


.. deap_restraints:: xmaxcamber1

:id: xmax_camber
:blade: 1
:minimum: 0.400
:maximum: 0.450
:default: 0.425
:digits: 3


.. deap_restraints:: xmaxcamber2

:id: xmax_camber
:blade: 2
:minimum: 0.470
:maximum: 0.500
:default: 0.472
:digits: 3


.. deap_restraints:: gamma_te1

:id: gamma_te
:blade: 1
:minimum: 0.10
:maximum: 0.20
:default: 0.14
:digits: 2


.. deap_restraints:: gamma_te2

:id: gamma_te
:blade: 2
:minimum: 0.10
:maximum: 0.20
:default: 0.14
:digits: 2


.. deap_restraints:: leth1

:id: th_le
:blade: 1
:minimum: 0.01
:maximum: 0.015
:default: 0.01
:digits: 3


.. deap_restraints:: leth2

:id: th_le
:blade: 2
:minimum: 0.01
:maximum: 0.015
:default: 0.01
:digits: 3


.. deap_restraints:: teth1

:id: th_te
:blade: 1
:minimum: 0.01
:maximum: 0.015
:default: 0.01
:digits: 3


.. deap_restraints:: teth2

:id: th_te
:blade: 2
:minimum: 0.01
:maximum: 0.015
:default: 0.01
:digits: 3

deap_settings.ini
.............................

Saved state of checkboxes and DEAP config. Will be overwritten by user input from GUI.
(Path: module/config/`deap_settings.ini <../configfiles/deap_settings.ini>`_).



mailinglist.ini
.............................

Config file containing recipient's email address
(Path: module/config/`mailinglist.ini <../configfiles/mailinglist.ini>`_).


optimizer_paths.ini
.............................

Path of project, iec, igg and design folder on RDP
(Path: module/config/`optimizer_paths.ini <../configfiles/optimizer_paths.ini>`_).


reference_blade.ini
.............................

Parameters of reference blade
(Path: module/config/`reference_blade.ini <../configfiles/reference_blade.ini>`_).


three_point_paths.ini
.............................

Path of .run files for design, upper and lower points
(Path: module/config/`three_point_paths.ini <../configfiles/three_point_paths.ini>`_).



Blade Generator
--------------------------

Blade config files:

default_blade.csv
.............................

Default blade parameters. Loaded at GUI start.
(Path: module/UI/config/`default_blade.csv <../configfiles/default_blade.csv>`_).
Rows:

- HEADER
- single blade parameters
- tandem blade 1 parameters
- tandem blade 2 parameters


init_values.csv
.............................

Some initial values for blade generation (scale, chord length, number of points, default points for spline).
(Path: module/UI/config/`init_values.csv <../configfiles/init_values.csv>`_).


restraints.txt
.............................

Restraints for blade generator parameters (sliders/input box)
(Path: module/UI/config/`restraints.txt <../configfiles/restraints.txt>`_).


restraints_annulus.txt
.............................

Restraints for the annulus gap generator
(Path: module/UI/config/`restraints_annulus.txt <../configfiles/restrains_annulus.txt>`_).


thdist_default.txt
.............................

Default points for thickness distribution
(Path: module/UI/config/`thdist_default.txt <../configfiles/thdist_default.txt>`_).



SSH Login config
--------------------------

SSH Login config file:

ssh_config.ini
...................

Config to save host, node, port and user credentials for the SSH connection
(Path: module/optimizer/ssh_login/`ssh_config.ini <../configfiles/ssh_config.ini>`_).

.. ssh:: ssh

:host: Host IP
:user: Username
:passwd: Password (encrypted)
:key: Key to decryption
:node: Node number (e.g. node05)
:timeout: Timeout in seconds
:port: Port number


