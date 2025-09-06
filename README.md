# Agent IA - Déploiement Render

## Déploiement
1. Copier toutes vos variables d'environnement dans Render (Environment → coller contenu du .env).
2. Pousser le dépôt sur GitHub.
3. Créer un service Docker sur Render et connecter au repo.
4. Render construira automatiquement l'image et déploiera le service.
5. L'agent sera accessible via l'URL fournie par Render.

## Notes
- Le fichier `.env` n’est pas nécessaire dans le dépôt si les variables sont définies dans Render.
- Pour ajouter des clés API supplémentaires, modifiez l'environnement sur Render.
