import re
from pathlib import Path


def sanitize_filename_fully(root_dir: str = "data/raw"):
  base_path = Path(root_dir)

  if not base_path.exists():
    print(f"❌ Le dossier {root_dir} n'existe pas.")
    return

  renamed_count = 0
  for path in sorted(base_path.rglob("*"), reverse=True):
    if path.is_file():
      stem = path.stem
      suffix = path.suffix

      # 1. Remplacer explicitement '&' par 'et'
      new_stem = stem.replace("&", "et")

      # 2. Remplacer les espaces par des underscores
      new_stem = new_stem.replace(" ", "_")

      # 3. Supprimer les caractères spéciaux gênants (parenthèses, virgules, etc.)
      # On ne garde que les lettres (avec accents), chiffres, tirets et underscores
      new_stem = re.sub(r"[^\w\-]", "_", new_stem)

      # 4. Nettoyer les doublons d'underscores consécutifs (__ -> _)
      new_stem = re.sub(r"_+", "_", new_stem).strip("_")

      new_name = f"{new_stem}{suffix}"
      new_path = path.with_name(new_name)

      if path.name != new_name:
        if new_path.exists():
          print(f"⚠️ Ignoré (existe déjà) : '{new_name}'")
          continue

        path.rename(new_path)
        print(f"✨ Ultra-nettoyé : '{path.name}' ➔ '{new_name}'")
        renamed_count += 1

  print(f"\n✅ Nettoyage avancé terminé ! {renamed_count} fichiers modifiés.")


if __name__ == "__main__":
  sanitize_filename_fully("data/raw")