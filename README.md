# Matrix semantic map [![Build Status](https://travis-ci.org/HumanCellAtlas/matrix_semantic_map.svg?branch=master)](https://travis-ci.org/HumanCellAtlas/matrix_semantic_map)

<img width="595" alt="image" src="https://user-images.githubusercontent.com/112839/54871602-28198780-4d8d-11e9-966f-75e7c42130d5.png">

## STATUS: DRAFT/EXPERIMENTAL


### Background

Popular formats for storing and sharing single-cell transcriptomic data and analysis (e.g. Loom; Single cell expression format) have relatively rich data structures for recording metadata, but the metadata itself is typically unstandardised and not linked to ontology terms. If, for example, an analysis file includes annotation of single cells or clusters with a cell-type or tissue type term, these are typically stored as free text.  Being able to link this free text unambiguously to ontology terms would ease integration across datasets.

For more detailed background and discussion see this [Request for comment](https://docs.google.com/document/u/1/d/1QEWgktwY8SvPwDNZxv4tfvCeTpzF2z931WlpfzSKfhU/edit)

This specification does not attempt to enforce column names or values or to force users to annoate with ontology terms. We need to be able to cope with cases where cell types are novel, or a mix of types which cannot (currently) be distinguished is present. Instead, this specification provides a way to map expression matrix metadata attached to columns, rows or whole matrices to ontology terms and, optionally, to specify the semantics of annotation. 

### This repo contains:

1. A formal specification of a [JSON schema for mapping expression matrix metadata to ontology terms](src/json_schema/expression_matrix_semantic_map.json). This specification is intended to be independent of expression matrix file format.
1. A Python library for generating and manipulating semantic mappings in Loom files, using this schema.  This library includes code for:
   * Validation of semantic mappings against JSON schema.
   * Semantic mapping content validation, using the [Ontology Lookup Service](https://www.ebi.ac.uk/ols/) [API](https://www.ebi.ac.uk/ols/api)
   * Writing semantic mappings to Loom files from csv. Mappings loaded from csv are checked against the JSON schema,  OLS and for consistency with Loom file metadata.
   * Enriching loom file metadata with labels and synonyms from ancestral classes to enhance search and query.
  
 ### Installation

    pip install matrix-semantic-map
 
 ### Quick guide

```.py 

from matrix_semantic_map.matrix_map_tools import MapBuilder

        mb = MapBuilder(
            loom="loom_filePath",
            cell_type_fields=['ca.Class'])
        mb.load_csv_map("tsv_filepath", sep='\t')
        mb.commit()  # Validate & if passes, add semantic map to loom file 
 ```
 
 For more detailed usage examples, please see [matrix_semantic_map snippets](https://github.com/HumanCellAtlas/matrix_semantic_map/blob/master/notebooks/matrix_semantic_map_snippets.ipynb).
 
#### Table specification:
 
 **Mandatory fields:**
 
  * *name*: annotation string used in loom file.
  * *applicable_to*: dot.path to the annotation field in which this name is used.  Multiple entries may be added, separate by a '|'.  See below for details of dot paths.
  * *maps_to_name*:  One or more ontology term names to which the name maps. Multiple entries are separated by a  '|' and must be in the same order as IDs in *map_to_id*.  As well as terms referring to (type of )entities (e.g. "neuron", "broca's area" "gastrula stage"), ontology terms used may refer to relationships between entities, e.g. a Tissue attribute used to annotate cells might be annotated to record the default relationship between an annotated cell and the tissue term it is annotated with (see below for example).
  * *map_to_id*:  One or more ontology term IDs to which the name maps. Multiple entries are separated by a '|'. IDs should be in the form of a [curie](). In the case of OBO foundry ontologies, OBO style IDs may be used (e.g. `GO:0000123`).
  
**Optional fields:**

Specify a relationship between entities(e.g. cells), annotated with the specified value and annotation under a second attribute (over-rides any default).
 
  * *relation_name*: The name of a standard ontology relation (AKA object property). 
  * *relation_id*: The ID (CURIE) of a standard ontology relation (AKA object property).
  * *subject*: dot.path to an annotation field the provides the subject of the relationship. 
  
The use of these fields is best illustrated with an example.  In classical anatomy, the vasculature that supplies blood to a brain region is not considered to be part of that brain region - blood supply and brain are separated by a blood-brain barrier.  But any analysis of all the cells in dissected brain region will include cells of endothelial cells of vasculture. In the table below, the annotation to endothelial-mural is linked to brain region via a 'contained in' relationship, rather than the default 'part of' 
  
**dot.path examples**

* `ca`: loom column attribute
*  `ca.Class`: Value of the 'Class' field under column attribute
*  `attrs.MetaData.clusterings[*].clusters[*].description`: Content of JSON stored in loom file header.
   *  `attrs`: Loom file attributes
   * `MetaData`: Attribute key
   * `clusterings[*].clusters[*].description`: [JPATH](https://goessner.net/articles/JsonPath/) string specifying location in JSON.  In this case, the first  element in the list of values in the decoded JSON structure is identified in Python by: `j['clusterings'][0]['clusters'][0]['description']`


**Example mapping tables**

name  | applicable_to  | maps_to_name  | maps_to_id  | relation_name  | relation_id  | object
 -- | -- | -- | -- | -- | --  | --
astrocytes_ependymal  | ca.Class  | ependymal cell\|astrocyte  | CL:0000065\|CL:0000127  |   |   | 
endothelial-mural  | ca.Class  | endothelial cell  | CL:0000115  | contained in  | RO:0001018  | ca.Tissue
sscortex  | ca.Tissue  | somatosensory cortex  | UBERON:0008930  |   |   | 
Mitochondrial  | ra.GeneType  | mitochondrial gene  | SO:0000088
Tissue  | ca  | part of  | BFO:0000050  |   |   | 
Class  | ca  | is_a  | rdfs:Type  |   |   | 


name  | applicable_to  | maps_to_name  | maps_to_id  
 -- | -- | -- | -- 
 T4/T5 - Cluster 2  | `attrs.MetaData.clusterings[*].clusters[*]`.description  | T neuron T4\|T neuron T5  | FBbt:00003731\|FBbt:00003736
T2/T3 - Cluster 6  | `attrs.MetaData.clusterings[*].clusters[*]`.description  | T neuron T2\|T neuron T3  | FBbt:00003728\|FBbt:00003730

Complete mapping tables and the loom files they are designed for can be found in the [resources directory](src/matrix_semantic_map/test/resources/).  The Loom files are: 

 - [Cortex.loom](src/matrix_semantic_map/test/resources/cortex.loom) **Data from**: Zeisel, et al. 2015. “Brain Structure. Cell Types in the Mouse Cortex and Hippocampus Revealed by Single-Cell RNA-Seq.” Science 347 (6226): 1138–42.  Downloaded from the [Linnarson Lab Loom browser](http://loom.linnarssonlab.org/dataset/cellmetadata/Previously%20Published/Cortex.loom)
 - Desplan_Fly_AdultOpticLobe_57k.loom.  **Data from**:  Kapuralin, K., Desplan, C., Barboza, L., Konstantinides, N., Fadil, C., & Satija, R. (2018). Phenotypic Convergence: Distinct Transcription Factors Regulate Common Terminal Features. Cell, 174(3), 622–635.e13. https://doi.org/10.1016/j.cell.2018.05.021
     - Available from the [Scope](http://scope.aertslab.org/) site from Stein Aerts group. 








  
  

  









