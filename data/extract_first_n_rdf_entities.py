import re

INPUT_FILE = "data/data.rdf"
OUTPUT_FILE = "data/data-test.rdf"
N_ENTITIES = 100

# Tags que representam entidades/classes/indivíduos RDF
ENTITY_TAGS = [
    "owl:Class",
    "owl:ObjectProperty",
    "owl:DatatypeProperty",
    "owl:AnnotationProperty",
    "owl:NamedIndividual",
    "rdf:Description",
]

# Regex para encontrar início de entidade
ENTITY_START_RE = re.compile(r"<(?P<tag>{})[ >]".format("|".join(ENTITY_TAGS)))
ENTITY_END_RE = re.compile(r"</(?P<tag>{})>".format("|".join(ENTITY_TAGS)))


def extract_first_n_entities(input_path, output_path, n_entities):
    with open(input_path, "r") as fin:
        lines = fin.readlines()

    # Encontrar cabeçalho (antes da primeira entidade)
    header = []
    i = 0
    while i < len(lines):
        if ENTITY_START_RE.search(lines[i]):
            break
        header.append(lines[i])
        i += 1

    # Extrair entidades
    entities = []
    count = 0
    while i < len(lines) and count < n_entities:
        start_match = ENTITY_START_RE.search(lines[i])
        if start_match:
            entity_lines = [lines[i]]
            tag = start_match.group("tag")
            # Procurar fechamento
            depth = 1 if not lines[i].strip().endswith("/>") else 0
            i += 1
            while i < len(lines) and depth > 0:
                entity_lines.append(lines[i])
                if ENTITY_START_RE.search(lines[i]):
                    depth += 1
                if ENTITY_END_RE.search(lines[i]):
                    depth -= 1
                i += 1
            entities.extend(entity_lines)
            count += 1
        else:
            i += 1

    # Encontrar rodapé (após a última entidade)
    footer = []
    while i < len(lines):
        footer.append(lines[i])
        i += 1

    # Escrever arquivo de saída
    with open(output_path, "w") as fout:
        fout.writelines(header)
        fout.writelines(entities)
        fout.writelines(footer)

if __name__ == "__main__":
    extract_first_n_entities(INPUT_FILE, OUTPUT_FILE, N_ENTITIES)
