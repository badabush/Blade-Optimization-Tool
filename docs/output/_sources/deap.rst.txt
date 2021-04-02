DEAP
=====================

Genetic Algorithm for Tandem Blade Optimization.

geomTurbo File Generation
--------------------------------

Generation of NUMECA file (geomTurbo) from GUI-blades.

.. automodule:: module.optimizer.geomturbo
   :members:
   :undoc-members:
   :show-inheritance:


Logging
--------------------------------

Logging of Runs. Uses the package logging in deap_run_handle.py.
Logs are shaped as follows:

- HEADER
- individual (generation)
- best fitness (generation)
- best individual (total)
- blade1/blade2 parameters

.. tabularcolumns:: |p{5cm}|p{1cm}|p{1cm}|p{7cm}|

.. csv-table:: Log structure
  :file: tables/log_table.csv
  :header-rows: 1
  :class: longtable
  :widths: 3 1 1 6

Visualization of Results
--------------------------------

Different Plots of the Run from Logs.

.. automodule:: module.optimizer.genetic_algorithm.deap_visualize
   :members:
   :undoc-members:
   :show-inheritance:


Feature/Density Plot
...............................

Plot density of all free parameters.

.. image:: images/feature_density.png
   :width: 800
   :alt: Feature/Density Plot

.. automodule:: module.optimizer.genetic_algorithm.plot.plot_feature_density
   :members:
   :undoc-members:
   :show-inheritance:


Feature/Time Plot
...............................

.. automodule:: module.optimizer.genetic_algorithm.plot.plot_feature_time
   :members:
   :undoc-members:
   :show-inheritance:

.. image:: images/alph_time.png
   :width: 800
   :alt: Feature/Time Plot


Fitness/Gen Plot
...............................

.. automodule:: module.optimizer.genetic_algorithm.plot.plot_fitness_generation
   :members: fitness_generation
   :undoc-members:
   :show-inheritance:

.. image:: images/fitness_generation.png
   :width: 800
   :alt: Fitness/Generation Plot


Fitness/Gen Scatter Plot
...............................

.. automodule:: module.optimizer.genetic_algorithm.plot.plot_fitness_generation
   :members: fitness_generation_scatter
   :undoc-members:
   :show-inheritance:
   :noindex:

.. image:: images/fitness_generation_scatter.png
   :width: 800
   :alt: Fitness/Generation Scatter Plot


Three-Point Plot
...............................

.. automodule:: module.optimizer.genetic_algorithm.plot.plot_threepoint
   :members:
   :undoc-members:
   :show-inheritance:

.. image:: images/ref_best_three_point.png
   :width: 800
   :alt: Ref/Best Three-Point Plot


Ref-/Best-Blade Plot
...............................

.. automodule:: module.optimizer.genetic_algorithm.plot.plot_blades
   :members:
   :undoc-members:
   :show-inheritance:

.. image:: images/blades.png
   :width: 800
   :alt: Ref/Best Blade Plot


Camber-/Thickness Distribution (ref/best) Plot
................................................

.. automodule:: module.optimizer.genetic_algorithm.plot.plot_camber_thickness
   :members:
   :undoc-members:
   :show-inheritance:

.. image:: images/camber_distribution.png
   :width: 800
   :alt: Camber Distribution Plot


.. image:: images/thickness_distribution.png
   :width: 800
   :alt: Thickness Distribution Plot


Contour Plot
...............................

.. automodule:: module.optimizer.genetic_algorithm.plot.plot_contour
   :members:
   :undoc-members:
   :show-inheritance:


Auto-Mailing
--------------------------------

Automatically send a mail to recipients after a run has finished.

.. automodule:: module.optimizer.mail.mail_script
   :members:
   :undoc-members:
   :show-inheritance:

