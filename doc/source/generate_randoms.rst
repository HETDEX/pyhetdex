.. _generate-randoms:

Generate Randoms
****************

.. warning::
    This is currently undergoing active development and testing

Instructions
============
This code is the first step in generating a random catalogue that accounts for the HETDEX
LAE selection function from the variance maps and the maps containing the fraction
of PSF flux in the detection aperture that are output from detect. In this first step,
random positions are generated and the variance and the fraction of flux in the 
detection aperture is saved for each of them. 


Running the code::

   generate_randoms [-h] fn_variance_map fn_detaper_fluxfrac fn_out nrands

   fn_variance_map      Filename of a detect variance cube
   fn_detaper_fluxfrac  Filename of a datcube cube containing the fraction of
                        flux in detection aperture from detect.
   fn_out               Output filename (extension sets filetype)
   nrands               Number of randoms to generate
 

The next step is to assign fluxes to the randoms, and see if they would be 
detected. For this you need to see :ref:`add-fluxes-to-randoms`.
    


