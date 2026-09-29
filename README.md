[![Linting](https://github.com/remyz17/odooghost/actions/workflows/lint.yaml/badge.svg)](https://github.com/remyz17/odooghost/actions/workflows/lint.yaml)
[![Testing](https://github.com/remyz17/odooghost/actions/workflows/test.yaml/badge.svg)](https://github.com/remyz17/odooghost/actions/workflows/test.yaml)
[![Deploy Documentation](https://github.com/remyz17/odooghost/actions/workflows/docs.yaml/badge.svg)](https://github.com/remyz17/odooghost/actions/workflows/docs.yaml)
# OdooGhost
*Making Odoo development a breeze.*  

OdooGhost is a powerful tool tailored for streamlining the development and deployment of Odoo instances. It offers an integrated solution that harnesses the power of Docker for orchestrating and managing these instances. With both a Command Line Interface (CLI) and an upcoming web interface, managing Odoo stacks has never been simpler.

## Features

- **Fine-grained Configuration**: Customize each Odoo instance with configuration files, tailoring settings to fit your specific needs.
- **Holistic Instance Management**: With just a few commands, you can create, update, start, stop, and even delete Odoo instances straight from the CLI.

## License
Licensed under the [MIT License](LICENSE).

---

# Guide développeur

OdooGhost est un outil CLI permettant de créer et gérer des environnements Odoo locaux basés sur Docker.

Version actuelle :

```text
0.17.0
```

---

## Installation

Installation recommandée avec `pipx` :

```bash
pipx install odooghost
```

Vérifier l'installation :

```bash
odooghost version
```

---

## Initialisation

Définir le répertoire de travail :

```bash
odooghost setup ~/odooghost
```

Afficher le répertoire configuré :

```bash
odooghost config working-dir
```

---

## Gestion des stacks

### Lister les stacks

Toutes les stacks :

```bash
odooghost stack ls
```

Stacks actuellement démarrées :

```bash
odooghost stack ps
```

### Valider une configuration

```bash
odooghost stack config check opennet.yaml
```

### Créer une stack

```bash
odooghost stack create opennet.yaml
```

Sans pull :

```bash
odooghost stack create opennet.yaml --no-pull
```

Forcer la recréation :

```bash
odooghost stack create opennet.yaml --force-recreate
```

---

## Démarrer une stack

### Démarrage classique

```bash
odooghost stack start opennet
```

Par défaut, OdooGhost démarre la stack puis affiche les logs du service Odoo.

Le nombre initial de lignes affichées peut être contrôlé avec :

```bash
odooghost stack start opennet --tail 100
```

Dans ce mode, `Ctrl+C` arrête la stack.

### Démarrage en arrière-plan

```bash
odooghost stack start opennet --detach
```

Le container continue alors de fonctionner et OdooGhost rend immédiatement la main au terminal.

---

## Mode interactif / PDB

Un mode interactif spécialement prévu pour le debugging est disponible :

```bash
odooghost stack start opennet --interactive
```

ou :

```bash
odooghost stack start opennet -i
```

Ce mode attache directement le terminal au container Odoo.

Il est recommandé pour :

- `breakpoint()`
- `pdb`
- `pdb++`
- le debugging Python interactif

Exemple :

```python
def action_test(self):
    breakpoint()
    result = 10

def action_test_2(self):
    import pdb; pdb.set_trace()
    result = 20
    ...
```

Démarrer ensuite Odoo avec :

```bash
odooghost stack start opennet -i
```

Lorsque le breakpoint est atteint :

```text
> /mnt/extra-addons/my_module/models/test.py(42)action_test()
(Pdb)
```

Le terminal permet alors d'utiliser normalement :

```text
n
s
c
l
p variable
pp variable
q
```

### Quitter le mode interactif

Pour détacher le terminal sans arrêter le container :

```text
Ctrl+P
Ctrl+Q
```

Pour arrêter :

```text
Ctrl+C
```

> Le mode `--interactive` nécessite un TTY et n'est actuellement pas supporté sous Windows.

---

## Ouvrir Odoo dans le navigateur

```bash
odooghost stack start opennet --open
```

Il est possible de choisir le mode d'ouverture :

```bash
odooghost stack start opennet --open --open-mode local
```

ou :

```bash
odooghost stack start opennet --open --open-mode subnet
```

Le mode par défaut dépend de la plateforme.

---

## Logs

Afficher les logs :

```bash
odooghost stack logs opennet
```

Afficher les 100 dernières lignes :

```bash
odooghost stack logs opennet --tail 100
```

Suivre les logs :

```bash
odooghost stack logs opennet --follow
```

ou :

```bash
odooghost stack logs opennet --follow --tail 100
```

Dans ce cas, `Ctrl+C` arrête uniquement le suivi des logs. La stack continue de fonctionner.

---

## Arrêter une stack

```bash
odooghost stack stop opennet
```

Avec un timeout spécifique :

```bash
odooghost stack stop opennet --timeout 30
```

Attendre l'arrêt :

```bash
odooghost stack stop opennet --wait
```

---

## Redémarrer une stack

```bash
odooghost stack restart opennet
```

---

## Exécuter une commande dans un container

`stack exec` exécute une commande dans un container existant.

### Shell Odoo

```bash
odooghost stack exec opennet odoo bash
```

### Shell PostgreSQL

```bash
odooghost stack exec opennet db bash
```

### PSQL

```bash
odooghost stack exec opennet db psql -- -U odoo test
```

Options disponibles notamment :

```text
-d / --detach
-u / --user
--privileged
--no-tty
-w / --workdir
```

---

## `stack run`

`stack run` lance une commande dans un **nouveau container temporaire** basé sur un service de la stack.

Exemple :

```bash
odooghost stack run opennet odoo bash
```

Le container créé est un container one-off. OdooGhost :

1. récupère la configuration du service ;
2. démarre les autres services nécessaires ;
3. crée un nouveau container ;
4. exécute la commande ;
5. supprime automatiquement le container lorsqu'il se termine.

L'option `-p / --port` permet d'exposer le port du service lors d'un `stack run`. Le port `8069` du container one-off est associé au `service_port` configuré pour le service Odoo.

```bash
odooghost stack run --port opennet odoo odoo -- \
    -d test \
    --dev=all
```

---

# Commandes de développement

Les workflows de développement les plus courants sont désormais disponibles
directement comme commandes natives OdooGhost (plus besoin de scripts bash).

## `stack dev`

Lance un container Odoo temporaire avec son port exposé et `--dev` activé.
Équivaut à `stack run --port <stack> odoo odoo -- -d <db> --dev=all`.

```bash
odooghost stack dev opennet
```

Avec une base spécifique :

```bash
odooghost stack dev opennet prod
```

Choisir la valeur de `--dev` (défaut : `all`) :

```bash
odooghost stack dev opennet test --dev=xml
```

## `stack install`

Installe un ou plusieurs modules Odoo dans un container one-off
(`odoo -i <module> --stop-after-init`).

```bash
odooghost stack install opennet my_module
```

Plusieurs modules :

```bash
odooghost stack install opennet module_a,module_b
```

Avec une base spécifique :

```bash
odooghost stack install opennet my_module --db prod
```

## `stack update-module`

Met à jour un ou plusieurs modules Odoo dans un container one-off
(`odoo -u <module> --stop-after-init`).

```bash
odooghost stack update-module opennet my_module
```

Plusieurs modules :

```bash
odooghost stack update-module opennet module_a,module_b
```

Avec une base spécifique :

```bash
odooghost stack update-module opennet my_module --db prod
```

## `stack psql`

Ouvre directement un shell PSQL sur la base de la stack
(raccourci de `stack exec <stack> db psql -- -U odoo <db>`).

```bash
odooghost stack psql opennet
```

Avec une base spécifique :

```bash
odooghost stack psql opennet prod
```

Avec un autre utilisateur PostgreSQL :

```bash
odooghost stack psql opennet prod --user odoo
```

---

## `stack start --interactive` vs `stack dev`

Les deux commandes répondent à des besoins différents.

| | `start --interactive` | `dev` |
|---|---|---|
| Container | principal | temporaire |
| One-off | non | oui |
| PDB interactif | oui | oui |
| Port Odoo | port normal | exposé automatiquement |
| Arguments Odoo personnalisés | non | oui (`--dev`, base) |
| `--dev=all` | configuration existante | activé par défaut |
| Auto-remove | non | oui |

---

## Pull

```bash
odooghost stack pull opennet
```

Plusieurs stacks :

```bash
odooghost stack pull opennet client18 client19
```

## Update (configuration)

```bash
odooghost stack update opennet.yaml
```

Sans pull :

```bash
odooghost stack update opennet.yaml --no-pull
```

---

## Supprimer une stack

```bash
odooghost stack drop opennet
```

Supprimer également les volumes :

```bash
odooghost stack drop opennet --volumes
```

> ⚠️ La suppression des volumes peut entraîner une perte définitive des données.

---

## Backup

```bash
odooghost stack data dump opennet test --dest ~/backups
```

---

# Tools (maintenance de base)

Le groupe `stack tools` regroupe des opérations de maintenance de base de
données, pratiques après la restauration d'un dump de production dans un
environnement de développement.

Toutes les commandes demandent une confirmation ; utilisez `-y` / `--yes` pour
la passer.

## `stack tools neutralize`

Neutralise la base (désactive les crons, les serveurs de mail entrants/sortants
et les fournisseurs de paiement).

```bash
odooghost stack tools neutralize opennet test
```

## `stack tools change-passwords`

Remplace le mot de passe de chaque utilisateur actif par son login.

```bash
odooghost stack tools change-passwords opennet test
```

## `stack tools disable-2fa`

Désactive l'authentification à deux facteurs (TOTP) pour tous les utilisateurs.

```bash
odooghost stack tools disable-2fa opennet test
```

## `stack tools set-admin`

Réinitialise les identifiants de l'utilisateur admin (id 2), `admin:admin` par
défaut.

```bash
odooghost stack tools set-admin opennet test
```

Avec des identifiants personnalisés :

```bash
odooghost stack tools set-admin opennet test --login admin --password secret
```

## `stack tools anonymize`

Anonymise les données personnelles des partenaires (emails, téléphones et
mobiles).

```bash
odooghost stack tools anonymize opennet test
```

---

# Cheatsheet

Convention native : `odooghost stack <commande> STACK [ARGUMENTS...]`

```bash
# ============================================================
# STACK
# ============================================================

odooghost stack start   STACK [--detach|--interactive|--open]
odooghost stack stop    STACK
odooghost stack restart STACK
odooghost stack logs    STACK [--follow --tail 100]


# ============================================================
# DEVELOPMENT
# ============================================================

# Stack normale + terminal interactif / PDB
odooghost stack start STACK --interactive

# Container Odoo temporaire + port + --dev=all
odooghost stack dev STACK [DATABASE]


# ============================================================
# SHELL / POSTGRESQL
# ============================================================

odooghost stack exec STACK odoo bash
odooghost stack exec STACK db bash
odooghost stack psql STACK [DATABASE]


# ============================================================
# MODULES
# ============================================================

odooghost stack install       STACK MODULE[,MODULE...] [--db DATABASE]
odooghost stack update-module STACK MODULE[,MODULE...] [--db DATABASE]


# ============================================================
# TOOLS
# ============================================================

odooghost stack tools neutralize        STACK DATABASE [-y]
odooghost stack tools change-passwords  STACK DATABASE [-y]
odooghost stack tools disable-2fa       STACK DATABASE [-y]
odooghost stack tools set-admin         STACK DATABASE [--login L --password P] [-y]
odooghost stack tools anonymize         STACK DATABASE [-y]


# ============================================================
# BACKUP
# ============================================================

odooghost stack data dump STACK DATABASE [--dest DESTINATION]
```

---

# Résumé des commandes de développement

| Commande | Action |
|---|---|
| `stack start --detach` | Démarrer une stack en arrière-plan |
| `stack stop` | Arrêter une stack |
| `stack restart` | Redémarrer une stack |
| `stack start --interactive` | Démarrer la stack avec terminal interactif / PDB |
| `stack dev` | Lancer un container Odoo temporaire avec port exposé et `--dev=all` |
| `stack logs --follow` | Suivre les logs Odoo |
| `stack exec ... odoo bash` | Ouvrir un shell dans le container Odoo |
| `stack exec ... db bash` | Ouvrir un shell dans le container PostgreSQL |
| `stack psql` | Ouvrir directement PSQL |
| `stack update-module` | Mettre à jour un module Odoo |
| `stack install` | Installer un module Odoo |
| `stack tools neutralize` | Neutraliser la base (crons, mails, paiements) |
| `stack tools change-passwords` | Mot de passe = login pour chaque utilisateur |
| `stack tools disable-2fa` | Désactiver la 2FA (TOTP) |
| `stack tools set-admin` | Réinitialiser l'admin (`admin:admin` par défaut) |
| `stack tools anonymize` | Anonymiser les données personnelles |
| `stack data dump` | Effectuer un dump |

## Contribute
Have ideas or enhancements for OdooGhost? We'd love to see them! Create a Pull Request to join in the journey of making Odoo development smoother for everyone.
