import os

import gemmi


def file2model(filepath):
    ''' file2model
    '''
    _, file_ext = os.path.splitext(filepath)
    if(file_ext == '.cif'):
        cif_block = gemmi.cif.read(filepath)[0]
        st = gemmi.make_structure_from_block(cif_block)
    elif file_ext == ".pdb":
        st = gemmi.read_structure(filepath)
    st.remove_alternative_conformations()
    st.remove_hydrogens()
    st.remove_waters()
    st.remove_ligands_and_waters()
    st.remove_empty_chains()
    if file_ext == ".cif":
        model = gemmi.make_assembly(
            st.assemblies[0], st[0], gemmi.HowToNameCopiedChain.AddNumber
        )
    elif file_ext == ".pdb":
        model = st[0]
    return model
