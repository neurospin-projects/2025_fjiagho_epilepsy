
Beta-VAE anomaly detection using cortical folding representations
###########################################################################

In this project, the main goal is to detect epileptic foci using a beta-VAE model. For this, I trained a beta-VAE on a dataset with 42000 subjects (UKB). Then, I used successively two epileptic databases: epilepsy_PBS (with 40 patients), and PEPR_MArseille (with 1000 patients). All the codes are available on "betaVAE" repository. 

This repository is based on https://github.com/neurospin-projects/2023_jlaval_STSbabies. It aims to apply the self-supervised deep learning pipepline to preterm-specific folding pattern analysis and explore explainability methods.
It's also based on the works by Louise Guillon on identification of rare cortical folding (`paper <https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00084/119130>`_).

The final presentation that I made at the end of the work is available here ('<https://fr.overleaf.com/project/6970e8eb54f410fe89ea3692>'_)


Dependencies
------------
- python >= 3.6
- pytorch >= 1.4.0
- numpy >= 1.16.6
- pandas >= 0.23.3


Set up the work environment
---------------------------
First, the repository can be cloned thanks to:

.. code-block:: shell

    git clone https://github.com/neurospin-projects/2025_fjiagho_epilepsy.git
    cd 2025_fjiagho_epilepsy

Then, install a virtual environment through the following command lines:

.. code-block:: shell

    python3 -m venv venv
    . venv/bin/activate
    pip3 install --upgrade pip
    pip3 install -e .

Alternatively, you can use the requirements file:

.. code-block:: shell

    python3 -m venv venv
    . venv/bin/activate
    pip3 install -r requirements_venv.txt

Note that you might need a `BrainVISA <https://brainvisa.info>`_ environment to run
some of the functions or notebooks.

Train the beta-VAE
---------------------------

To train the beta-VAE, change the configs file, then run

.. code-block:: shell

    cd betaVAE
    python3 main.py 

Once the model is trained, we can generate the embeddings by running:

.. code-block:: shell

    cd betaVAE
    python3 generate_embeddings.py

More details
---------------------------

For more information, refer to the more detailed README : `detailed README.md <betaVAE/notebooks/fred/README.md>`_
