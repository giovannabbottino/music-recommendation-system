from application.ontology_service import OntologyService

if __name__ == "__main__":
    service = OntologyService("data/graph.owl")
    service.load_ontology()
    
    # Aplica a regra para inferir preferências de gênero baseadas em avaliações
    print("Aplicando regra de preferência de gênero...")
    service.apply_genre_preference_rule()
    
    # Aplica a regra de recomendação de música baseada no gênero preferido
    print("Aplicando regra de recomendação de música...")
    service.apply_music_recommendation_rule()
    
    print("Processo de recomendação concluído!")
