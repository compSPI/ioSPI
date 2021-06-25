"""Read and Write atomic models in various formats."""

import os

import gemmi


def read_gemmi_model(path, i_model=0, clean=True):
    """Read PDB or mmCIF file.

    Use Gemmi library to read PDB or mmCIF files and return a Gemmi model.
    The hierarchy in Gemmi follows:
    Structure - Model - Chain - Residue - Atom

    Parameters
    ----------
    path: string
        Path to PDB or mmCIF file.
    i_model: integer
        Optional, default: 0
        Index of the returned model in the Gemmi Structure.
    clean: bool
        Optional, default: True
        If True, use Gemmi remove_* methods to clean up structure.

    Returns
    -------
    model: Gemmi Class
        Gemmi model

    Example
    -------
    TO DO

    Reference
    ---------
    See https://gemmi.readthedocs.io/en/latest/mol.html for a definition of
    gemmi objects.

    """
    try:
        if not os.path.exists(path):
            raise OSError
        if path.lower().endswith(".pdb"):
            st = gemmi.read_structure(path)
        elif path.lower().endswith(".cif"):
            cif_block = gemmi.cif.read(path)[0]
            st = gemmi.make_structure_from_block(cif_block)
        else:
            raise ValueError("File format not recognized.")
    except OSError as ose:
        print(type(ose), "::", ose)
    except ValueError as ve:
        print(type(ve), "::", ve)

    if clean:
        st.remove_alternative_conformations()
        st.remove_hydrogens()
        st.remove_waters()
        st.remove_ligands_and_waters()
        st.remove_empty_chains()

    model = st[i_model]
    if path.lower().endswith(".cif"):
        assembly = st.assemblies[i_model]
        model = gemmi.make_assembly(
            assembly, model, gemmi.HowToNameCopiedChain.AddNumber
        )
    # elif path.lower().endswith(".pdb"):
    #    model = st[i_model]

    return model


def write_gemmi_model(path, model=gemmi.Model('model')):
    """Write Gemmi model to PDB or mmCIF file.

    Use Gemmi library to write an atomic model to file.

    Parameters
    ----------
    path: string
        Path to PDB or mmCIF file.
    model: Gemmi Class
        Optional, default: gemmi.Model()
        Gemmi model

    Example
    -------
    TO DO

    Reference
    ---------
    See https://gemmi.readthedocs.io/en/latest/mol.html for a definition of
    gemmi objects.

    """
    try:
        if path.lower().endswith(".pdb"):
            pass
        elif path.lower().endswith(".cif"):
            pass
        else:
            raise ValueError("File format not recognized.")
    except ValueError as ve:
        print(ve)

    structure = gemmi.Structure()
    structure.add_model(model, pos=-1)
    structure.renumber_models()

    if path.lower().endswith(".cif"):
        structure.make_mmcif_document().write_file(path)
    elif path.lower().endswith(".pdb"):
        structure.write_pdb(path)
