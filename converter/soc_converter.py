import sys
from pathlib import Path
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD, URIRef

# ONTOLOGY NAMESPACE
DO_NS = Namespace("http://www.semanticweb.org/soap#")

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python soc_converter.py <path/to/file.soc>", file=sys.stderr)
        return 1

    soc_path = Path(sys.argv[1])
    if not soc_path.exists() or not soc_path.is_file():
        print(f"File not found: {soc_path}", file=sys.stderr)
        return 1

    dataset_id = soc_path.stem
    out_path = soc_path.with_suffix(".ttl")

    # DYNAMIC DATA NAMESPACE
    DATA_NS = Namespace(f"http://www.semanticweb.org/soap/data/{dataset_id}/")
    
    # Parse the file
    header_lines = []
    data_lines = []

    with soc_path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                header_lines.append(line)
            else:
                data_lines.append(line)

    # Extract Title
    title = dataset_id
    for line in header_lines:
        if line.startswith("# TITLE:"):
            title = line[len("# TITLE:"):].strip()
            break

    # Extract Alternatives
    alternatives = {}
    for line in header_lines:
        if line.startswith("# ALTERNATIVE NAME"):
            rest = line[len("# ALTERNATIVE NAME"):].strip()
            try:
                number_part, name_part = rest.split(":", 1)
                alt_id = int(number_part.strip())
                alternatives[alt_id] = name_part.strip()
            except ValueError:
                continue

    # Extract Rankings
    rankings = []
    for line in data_lines:
        try:
            count_part, order_part = line.split(":", 1)
            multiplicity = int(count_part.strip())
            # Handle empty order part just in case
            if not order_part.strip():
                order = []
            else:
                order = [int(x.strip()) for x in order_part.split(",")]
            rankings.append((multiplicity, order))
        except ValueError:
            continue

    # Build the Graph
    g = Graph()
    g.bind("soap", DO_NS)
    g.bind("data", DATA_NS)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    # Define Context
    context_iri = URIRef(DATA_NS + f"context/{dataset_id}")
    g.add((context_iri, RDF.type, DO_NS.Context))
    g.add((context_iri, RDFS.label, Literal(title)))

    # Define Options
    options = {}
    for alt_id in sorted(alternatives):
        opt_iri = URIRef(DATA_NS + f"option/{dataset_id}/{alt_id}")
        options[alt_id] = opt_iri
        
        g.add((opt_iri, RDF.type, DO_NS.Option))
        g.add((opt_iri, RDFS.label, Literal(alternatives[alt_id])))
        g.add((context_iri, DO_NS.hasAvailableOption, opt_iri))

    # Define Ballots and Agents
    for ballot_index, (multiplicity, order) in enumerate(rankings, start=1):
        ballot_iri = URIRef(DATA_NS + f"ballot/{dataset_id}/{ballot_index}")
        agent_iri = URIRef(DATA_NS + f"agent/{dataset_id}/{ballot_index}")

        # Ballot Types
        g.add((ballot_iri, RDF.type, DO_NS.Ballot))
        g.add((ballot_iri, RDF.type, DO_NS.RankedBallot))
        g.add((ballot_iri, RDF.type, DO_NS.CompleteBallot))
        g.add((ballot_iri, RDF.type, DO_NS.AggregatedBallot))

        # Ballot Properties
        g.add((ballot_iri, DO_NS.hasContext, context_iri))
        g.add((ballot_iri, DO_NS.hasMultiplicity, Literal(multiplicity, datatype=XSD.int)))

        # Agent
        g.add((agent_iri, RDF.type, DO_NS.Agent))
        g.add((agent_iri, RDFS.label, Literal(f"Synthetic agent {ballot_index} ({dataset_id})")))
        g.add((agent_iri, DO_NS.hasExpressed, ballot_iri))

        # Ballot Options (Ranking positions)
        for rank_pos, alt_id in enumerate(order, start=1):
            if alt_id not in options:
                continue # Skip if ID mentioned in ranking but not defined in header

            bo_iri = URIRef(DATA_NS + f"bo/{dataset_id}/{ballot_index}/{alt_id}")
            
            # Link Ballot -> BallotOption
            g.add((ballot_iri, DO_NS.hasBallotOption, bo_iri))
            
            # Define BallotOption
            g.add((bo_iri, RDF.type, DO_NS.BallotOption))
            g.add((bo_iri, DO_NS.refersToOption, options[alt_id]))
            g.add((bo_iri, DO_NS.hasRank, Literal(rank_pos, datatype=XSD.int)))

    # Serialize output
    g.serialize(destination=out_path, format="turtle", encoding="utf-8")

    print(
f"""\

██╗  ██╗██████╗ 
██║  ██║╚════██╗
███████║ █████╔╝
╚════██║██╔═══╝ 
     ██║███████╗
     ╚═╝╚══════╝

The Answer to the Ultimate Question of Life, the Universe, and Everything
might be found by querying a knowledge graph → {out_path}
"""
)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())