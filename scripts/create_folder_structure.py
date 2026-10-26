import json
import re
import unicodedata
from pathlib import Path


def slugify(value: str) -> str:
    """Normalise une chaîne de caractères pour l'utiliser sans risque dans un chemin de dossier.

    Exemple: "Licence Fondamentale" -> "licence_fondamentale"
    "Digital skills & intelligence artificielle" -> "digital_skills_intelligence_artificielle"
    """
    # 1. Supprimer les accents (NFD decomposition)
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")

    # 2. Mettre en minuscules
    value = value.lower()

    # 3. Remplacer les caractères non alphanumériques par des tirets bas
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-\s]+", "_", value)

    # 4. Supprimer les tirets bas en début/fin
    return value.strip("_")


def generate_folder_structure(json_path: str, base_dir: str = "data/raw"):
    """Lit le JSON et crée l'arborescence des dossiers."""
    json_file = Path(json_path)

    if not json_file.exists():
        print(f"❌ Erreur : Le fichier {json_path} n'existe pas.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    created_count = 0

    # Lecture de chaque type de formation (Licence Fondamentale, Master, Doctorat...)
    for formation_type in data:
        type_name = slugify(formation_type.get("type", "inconnu"))

        for dept in formation_type.get("departements", []):
            dept_name = slugify(dept.get("departement", "inconnu"))

            for filiere_info in dept.get("formations", []):
                filiere_name = slugify(filiere_info.get("Filière", "inconnu"))

                # Cas des Licences & Masters (contiennent un tableau "CONTENU" avec semestres/modules)
                if "CONTENU" in filiere_info:
                    for item in filiere_info["CONTENU"]:
                        semestre_num = f"s{item.get('semestre', 0)}"

                        for module in item.get("modules", []):
                            module_name = slugify(module)

                            # Création des sous-dossiers standards pour chaque module
                            for subfolder in ["cours", "td", "tp"]:
                                path = (
                                    Path(base_dir)
                                    / type_name
                                    / dept_name
                                    / filiere_name
                                    / semestre_num
                                    / module_name
                                    / subfolder
                                )

                                path.mkdir(parents=True, exist_ok=True)
                                created_count += 1

                # Cas spécifique du Doctorat (qui utilise AXES_DE_RECHERCHE)
                elif "AXES_DE_RECHERCHE" in filiere_info:
                    for axe in filiere_info["AXES_DE_RECHERCHE"]:
                        axe_name = slugify(axe)
                        for subfolder in ["publications", "documents"]:
                            path = (
                                Path(base_dir)
                                / type_name
                                / dept_name
                                / filiere_name
                                / axe_name
                                / subfolder
                            )
                            path.mkdir(parents=True, exist_ok=True)
                            created_count += 1

    print(
        f"✅ Arborescence créée avec succès dans '{base_dir}' ! ({created_count} dossiers générés)"
    )


if __name__ == "__main__":
    # Chemin vers votre fichier JSON et destination de l'arborescence
    JSON_PATH = "data/processed/structure_faculte.json"
    OUTPUT_BASE_DIR = "data/raw"

    generate_folder_structure(JSON_PATH, OUTPUT_BASE_DIR)