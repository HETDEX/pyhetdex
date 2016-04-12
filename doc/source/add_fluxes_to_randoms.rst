.. _add-fluxes-to-randoms:

Add fluxes to randoms
*********************

.. warning::
    This is currently undergoing active development and testing

Instructions
============

Add fluxes and SNR to a random catalogues previously generated as in
:ref:`generate-randoms`. Fluxes are assigned based on a luminosity
function.

.. warning::
   This luminosity function currently just returns random values.

You can optionally apply a detection efficiency model which rejects
some fraction of the low-SNR points.

.. warning::
   The detection model is under active development and not carefully tested.

Running the code::

    add_fluxes_to_randoms [-h] [--det-eff] fn_in fn_out

    fn_in       Output filename (extension sets filetype)
    fn_out      Output filename (extension sets filetype)




