# Music Recommendation System

## Overview

This project uses an OWL ontology to represent entities and relationships in the music domain, such as songs, genres, singers, users, and ratings.

## Project Structure

- `src/domain/`: Domain entities (Music, Genre, Singer, User, Rating)
- `src/application/`: Application services (e.g., OntologyService)
- `src/infrastructure/`: Integration with external technologies (e.g., Owlready2)
- `src/app.py`: Application entry point
- `data/data.rdf`: OWL ontology file
- `tests/`: Tests for the application

## How to Run Locally

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Run the main app:

```bash
python src/app.py
```

## Running Tests

1. Make sure you have pytest installed:

```bash
pip install -r requirements.txt
```

2. Run the tests:

```bash
pytest tests
```

The tests include verification of SWRL rules for inferring user preferences based on their ratings.

## How to Run with Docker

1. Build the Docker image:

```bash
docker build -t music-recommendation-system .
```

2. Run the application:

```bash
docker run --rm -it music-recommendation-system
```

## About the Ontology

The file `data/data.rdf` should be a valid OWL ontology in Turtle or RDF/XML format. If you encounter parsing errors with `owlready2`, validate the file using an [online Turtle validator](https://ttl-online-tool.com/) or Protégé.

## Contact

Questions or suggestions? Open an issue or contact the project maintainers.
