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
        if os.path.isfile(path):
            if path.lower().endswith(".pdb"):
                return read_gemmi_model_from_pdb(path, i_model, clean)
            elif path.lower().endswith(".cif"):
                return read_gemmi_model_from_cif(path, i_model, clean)
            else:
                raise ValueError("File format not recognized.")
        else:
            raise OSError
    except OSError as ose:
        print(type(ose), "::", ose)
    except ValueError as ve:
        print(type(ve), "::", ve)


def read_gemmi_model_from_pdb(path, i_model=0, clean=True):
    """Read Gemmi Model from PDB file.

    Parameters
    ----------
    path: string
        Path to PDB file.
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
    """

    structure = gemmi.read_structure(path)
    if clean:
        structure = clean_gemmi_structure(structure)
    model = st[i_model]
    return model


def read_gemmi_model_from_cif(path, i_model=0, clean=True):
    """Read Gemmi Model from CIF file.

    Parameters
    ----------
    path: string
        Path to mmCIF file.
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
    """

    cif_block = gemmi.cif.read(path)[0]
    structure = gemmi.make_structure_from_block(cif_block)
    if clean:
        structure = clean_gemmi_structure(structure)
    model = st[i_model]
    assembly = st.assemblies[i_model]
    model = gemmi.make_assembly(assembly, model, gemmi.HowToNameCopiedChain.AddNumber)
    return model


def clean_gemmi_structure(structure=None):
    """Clean Gemmi Structure.

    Parameters
    ----------
    structure: Gemmi Class
        Gemmi Structure object

    Returns
    -------
    structure: Gemmi Class
        Same object, cleaned up of unnecessary atoms.

    """

    if structure is not None:
        structure.remove_alternative_conformations()
        structure.remove_hydrogens()
        structure.remove_waters()
        structure.remove_ligands_and_waters()
        structure.remove_empty_chains()

    return structure


def write_gemmi_model(path, model=gemmi.Model("model")):
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
