# SETUP
import sys
from pathlib import Path

# NAMESPACE
DO_NS = "http://www.semanticweb.org/decision-ontology#"
DATA_NS = "http://www.semanticweb.org/decision-ontology/data/preflib/"

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python soc_to_ttl.py <file.soc>", file=sys.stderr)
        return 1

    soc_path = Path(sys.argv[1])
    if not soc_path.exists() or not soc_path.is_file():
        print(f"File not found: {soc_path}", file=sys.stderr)
        return 1

    dataset_id = soc_path.stem
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

    # Title
    title = None
    for line in header_lines:
        if line.startswith("# TITLE:"):
            title = line[len("# TITLE:"):].strip()
            break
    if title is None:
        title = dataset_id  # fallback

    # Alternatives
    alternatives = {}
    for line in header_lines:
        if line.startswith("# ALTERNATIVE NAME"):
            rest = line[len("# ALTERNATIVE NAME"):].strip()
            number_part, name_part = rest.split(":", 1)
            alt_id = int(number_part.strip())
            alt_name = name_part.strip()
            alternatives[alt_id] = alt_name

    # Rankings
    rankings = []
    for line in data_lines:
        count_part, order_part = line.split(":", 1)
        weight = int(count_part.strip())
        order = [int(x.strip()) for x in order_part.split(",")]
        rankings.append((weight, order))

    # Build TTL
    ttl = (
        f"@prefix do: <{DO_NS}> .\n"
        f"@prefix data: <{DATA_NS}> .\n"
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"
    )

    context_iri = f"data:context/{dataset_id}"
    ttl += f"{context_iri} a do:Context ;\n"
    ttl += f'  rdfs:label "{title}" .\n\n'

    option_iris = {alt_id: f"data:option/{dataset_id}/{alt_id}" for alt_id in sorted(alternatives)}
    ttl += (
        f"{context_iri} do:hasAvailableOption "
        f"{', '.join(option_iris[a] for a in sorted(option_iris))} .\n\n"
    )

    for alt_id in sorted(alternatives):
        ttl += f'{option_iris[alt_id]} a do:Option ; rdfs:label "{alternatives[alt_id]}" .\n'
    ttl += "\n"

    for ballot_index, (weight, order) in enumerate(rankings, start=1):
        ballot_iri = f"data:ballot/{dataset_id}/{ballot_index}"
        agent_iri = f"data:agent/{dataset_id}/{ballot_index}"
        bo_iris = [f"data:bo/{dataset_id}/{ballot_index}/{alt_id}" for alt_id in order]

        ttl += (
            f"{ballot_iri} a do:Ballot, do:RankedBallot, do:CompleteBallot, do:AggregatedBallot ;\n"
            f"  do:hasContext {context_iri} ;\n"
            f"  do:hasWeight \"{weight}\"^^xsd:int ;\n"
            f"  do:hasBallotOption {', '.join(bo_iris)} .\n\n"
        )

        for rank_pos, alt_id in enumerate(order, start=1):
            bo_iri = f"data:bo/{dataset_id}/{ballot_index}/{alt_id}"
            ttl += (
                f"{bo_iri} a do:BallotOption ;\n"
                f"  do:refersToOption {option_iris[alt_id]} ;\n"
                f"  do:optionRank \"{rank_pos}\"^^xsd:int .\n\n"
            )

        ttl += (
            f"{agent_iri} a do:Agent ;\n"
            f'  rdfs:label "Synthetic agent {ballot_index} ({dataset_id})" ;\n'
            f"  do:hasExpressed {ballot_iri} .\n\n"
        )

    out_path = soc_path.with_suffix(".ttl")
    with out_path.open("w", encoding="utf-8") as f:
        f.write(ttl)

    print(f"Congratulations, you just converted a .soc file to .ttl --> {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
