# expression_matrix_2_ontology

Specification for a JSON schema to map expression matrix annotations to ontology terms

## STATUS: DRAFT/EXPERIMENTAL

THIS SCHEMA IS EXPERIMENTAL AND UNDER DEVELOPMENT.  IT MAY NOT BE STABLE !


### Background

Popular formats for storing and sharing single-cell transcriptomic data and analysis, such as Loom and Single cell expression format have relatively rich data structures for recording metadata, but the metadata itself is typically unstandardised and not linked to ontology terms. If, for example, an analysis file includes annotation of single cells or clusters with a cell-type or tissue type term, these are typically stored as free text.  Being able to link this free text unambiguously to ontology terms would ease integration across datasets.

### Outline:

This specification does not attempt to enforce paticular column names or values (specification of these is needed, but is out of scope).   Forcing users into annotating direcly with ontologies would be too limiting: we need to be able to cope with case where cell types are novel, or a mix of types which cannot (currently) be distinguished is present.  Instead, this specification provides a way to map columns and their values to ontology terms and to (optionally) specify the semantics of annotation. 

We assume that format allows file level metadata.  We use this to store a JSON string that maps column names and values to ontology terms/relations.


...









