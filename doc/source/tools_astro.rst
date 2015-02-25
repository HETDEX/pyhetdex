.. :py:currentmodule:: pyhetdex.tools

:py:mod:`tools.astro` -- Astronomical tools
*******************************************

:py:mod:`iq_fit` -- image quality fitting
=========================================

.. automodule:: pyhetdex.tools.astro.iq_fit

Reconstruct the IFU head and fit the 2D Moffat
----------------------------------------------
.. autofunction:: pyhetdex.tools.astro.iq_fit.fit_image_quality

The fitter
----------
.. autoclass:: pyhetdex.tools.astro.iq_fit.MonteCarlo_Moffat2D
   :members: evaluate, __call__
   :show-inheritance:

.. autofunction:: pyhetdex.tools.astro.iq_fit.montecarlo_2d

The sampler
-----------
.. autoclass:: pyhetdex.tools.astro.iq_fit._BaseSampler
   :members:
   :show-inheritance:
.. autoclass:: pyhetdex.tools.astro.iq_fit.RandomSampler
   :members:
   :show-inheritance:
.. autoclass:: pyhetdex.tools.astro.iq_fit.GridSampler
   :members:
   :show-inheritance:

Utilities
---------
.. autofunction:: pyhetdex.tools.astro.iq_fit.get_fwhm


:py:mod:`sky` -- Sky subtraction and estimation
===============================================

.. automodule:: pyhetdex.tools.astro.sky
   :member-order: bysource
   :members:
   :undoc-members:
   :private-members:
  
:py:mod:`dss_image` -- Fetch and plot DSS/SDSS images
===============================================================

.. automodule:: pyhetdex.tools.astro.dss_image
   :member-order: groupwise
   :members:
   :undoc-members:
   :private-members:

