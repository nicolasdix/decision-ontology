# A Data Model for Collective Decision Making

This repository contains all artifacts produced during my bachelor's thesis on data modeling for collective decision-making. Please read about licensing conditions under [License](#License).

## Structure
- `data/` – datasets (raw, cleaned, metadata)
- `ontology/` – ontology files and exports
- `mappings/` – dataset-to-ontology mappings
- `scripts/` – utilities and processing scripts
- `figures/` – plots and diagrams for the thesis
- `converter/` – .soc to .ttl converter
- `transformations/` – all transformed .soc files

## Thesis Abstract
Preference and election datasets are increasingly published as open data, yet their interoperability remains limited due to inconsistent formats and the absence of explicit semantics. Prior work provides syntactic specifications but fails to support semantic integration and machine-queryable context. By analyzing ten heterogeneous datasets, from political elections to human-AI preference data, this thesis investigates recurring semantic concepts and structural differences in the respective data models. Based on the analysis, an ontology for preference data is developed to formalize agents, ballots, options, context and results independently of file-level encodings. The ontology is evaluated through manual and tool-supported data mappings, knowledge queries driven by competency questions and a prototype automation. The findings demonstrate that separating preference semantics from representation formats improves interoperability and query expressiveness. The results highlight the limitations of format-centric approaches and underline the potential of ontology-based standards for collective decision making data.

## License
Apache License Version 2.0
