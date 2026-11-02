# Présentation — plan de 7 diapositives

1. **TravelMate AI** — problème: planifier un voyage personnalisé est dispersé; public: citoyens/voyageurs.
2. **MVP et limites** — demande structurée, destination, budget indicatif, itinéraire; pas de réservation ni de données live.
3. **Architecture LangGraph** — quatre agents spécialisés et un Supervisor; schéma dans `architecture.md`.
4. **Démo du voyage** — saisir Casablanca → Maroc, 7 jours, 6 000 MAD; afficher le plan et la répartition.
5. **Observabilité** — suivre le Correlation ID, les statuts, durées et logs.
6. **Incident simulé** — provoquer une panne Budget Agent; montrer retry, FAILED, DEGRADED et fallback.
7. **Tests et suite** — commandes Pytest, documentation; prochaines étapes: sources officielles, stockage, déploiement public.

Ne pas annoncer un déploiement, un test ou une source live avant d'en avoir la preuve.
