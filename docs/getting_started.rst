Getting Started
==================================

| A small guide on how to get this software running and which customizations and modifications are possible.
| Most theoretical knowledge required are covered in my thesis, which can be accessed <here> when it is released.


Prerequisites
---------------

| BOT runs entirely on Python 3.7, so make sure to have it installed. Please refer to `Packages <packages.html>`__ for
  all the python packages required to run this.
|
| Note that `Optimizer <optimizer.html>`__ and `DEAP <deap.html>`__ requires an account at the institutes server since
  all simulations run on the server, but Blade Generator works regardless.

First configurations
----------------------

| In order to use all features of BOT, some configurations have to be done.


SSH Connection
...............

| Click on <Optimize>-<create config> and enter your credentials and the node where the simulations should run as
  described :ref:`sec_ssh_config`.


Display
........

| BOT runs simulations on NUMECA via Python scripts by creating and sending it via console. NUMECA requires the
  VNC-Display to start, so run  ``echo $DISPLAY`` in the linux terminal and enter the output in the GUI text field.
  The output should look like this: ``localhost:15.0``.


Paths
......

| Change paths of NUMECA project working directory inside the optimizer tab, affects :ref:`ssec_three_point_paths` and
  :ref:`ssec_optimizer_paths`.




