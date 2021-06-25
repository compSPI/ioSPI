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
    if os.path.isfile(path):
        is_pdb = path.lower().endswith(".pdb")
        is_cif = path.lower().endswith(".cif")
        if is_pdb:
            model = read_gemmi_model_from_pdb(path, i_model, clean)
        if is_cif:
            model = read_gemmi_model_from_cif(path, i_model, clean)
        if not is_pdb or not is_cif:
            model = None
            raise ValueError("File format not recognized.")
    else:
        model = None
        raise OSError("File could not be found.")
    return model


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
    model = structure[i_model]
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
    model = structure[i_model]
    assembly = structure.assemblies[i_model]
    chain_naming = gemmi.HowToNameCopiedChain.AddNumber
    model = gemmi.make_assembly(assembly, model, chain_naming)
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
    is_pdb = path.lower().endswith(".pdb")
    is_cif = path.lower().endswith(".cif")
    if if not is_pdb or not is_cif:
        raise ValueError("File format not recognized.")

    structure = gemmi.Structure()
    structure.add_model(model, pos=-1)
    structure.renumber_models()

    if is_cif:
        structure.make_mmcif_document().write_file(path)
    if is_pdb:
        structure.write_pdb(path)
