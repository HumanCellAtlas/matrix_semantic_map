# expression_matrix_2_ontology [![Build Status](https://travis-ci.org/HumanCellAtlas/expression_matrix_2_ontology.svg?branch=master)](https://travis-ci.org/HumanCellAtlas/expression_matrix_2_ontology) [![Coverage Status](https://coveralls.io/repos/github/HumanCellAtlas/expression_matrix_2_ontology/badge.svg?branch=master)](https://coveralls.io/github/HumanCellAtlas/expression_matrix_2_ontology?branch=master)

Specification for a JSON schema to map expression matrix annotations to ontology terms

## STATUS: DRAFT/EXPERIMENTAL

THIS SCHEMA IS EXPERIMENTAL AND UNDER DEVELOPMENT.  IT MAY NOT BE STABLE !

### Background

Popular formats for storing and sharing single-cell transcriptomic data and analysis, such as Loom and Single cell expression format have relatively rich data structures for recording metadata, but the metadata itself is typically unstandardised and not linked to ontology terms. If, for example, an analysis file includes annotation of single cells or clusters with a cell-type or tissue type term, these are typically stored as free text.  Being able to link this free text unambiguously to ontology terms would ease integration across datasets.

For more detailed background and discussion see this [Request for comment](https://docs.google.com/document/u/1/d/1QEWgktwY8SvPwDNZxv4tfvCeTpzF2z931WlpfzSKfhU/edit)

This specification does not attempt to enforce paticular column names or values (specification of these is needed, but is out of scope). Forcing users into annotating direcly with ontologies would be too limiting: we need to be able to cope with case where cell types are novel, or a mix of types which cannot (currently) be distinguished is present. Instead, this specification provides a way to map expression matrix metadata attached to columns, rows or wholes matrices to ontology terms and to (optionally) specify the semantics of annotation. 

### This repo contains:

(a) A formal specification of a JSON schema for mapping expression matrix metadata to ontology terms. This specification is intended to be independent of expression matrix file format.
(b) A Python library for generating and manipulating semantic mappings in Loom files, using this schema.  This library includes code for:
  * Validation of semantic mappings against JSON schema.
  * Semantic mapping content validation, using the (Ontology Lookup Service)[https://www.ebi.ac.uk/ols/] [API](https://www.ebi.ac.uk/ols/api)
  * Writing semantic mappings to Loom files from csv. Mappings loaded from csv are checked against the JSON schema,  OLS and for consistency with Loom file metadata.
  * Enriching loom file metadata with labels and synonyms from ancestral classes to enhance search and query.
  
 ### Installation
 
 Details TBA - submission to PyPy is pending.









