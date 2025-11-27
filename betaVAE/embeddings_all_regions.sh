#!/bin/bash
# === CONFIGURATION ===
A="/neurospin/dico/fred/Runs/01_betaVAE/Program/2023_jlaval_STSbabies/betaVAE/configs/dataset/cristobal"       # dossier A contenant UKB, hcp, epilepsy_PBS
B="/neurospin/tmp/fred/models/2025-11-10"       # dossier B contenant les sous-dossiers correspondants
SCRIPT="generate_embeddings.py"         # script Python à exécuter

# === BOUCLE PRINCIPALE ===
for subfolder in UKB hcp epilepsy_PBS; do
    echo "=== Traitement du sous-dossier $subfolder ==="
    for yaml_file in "$A/$subfolder"/*.yaml; do
        # Vérifie qu'il y a bien des fichiers
        [ -e "$yaml_file" ] || continue

        # Nom du fichier sans extension
        fname=$(basename "$yaml_file" .yaml)

        # Trouve le sous-dossier correspondant dans B
        target_dir=$(find "$B" -maxdepth 1 -type d -name "${fname}_*" | head -n 1)

        if [ -z "$target_dir" ]; then
            echo "⚠️ Aucun dossier correspondant pour $fname dans B"
            continue
        fi

        # Détermine le sous-dossier de destination selon la catégorie

        case $subfolder in
            UKB)
                arg2="${target_dir}"
                ;;
            hcp)
                arg2="${target_dir}/hcp"
                ;;
            epilepsy_PBS)
                arg2="${target_dir}/epilepsy_PBS"
                ;;
        esac

        # Vérifie l'existence de inputs.npy
        if [ -f "$arg2/inputs.npy" ]; then
            echo "⏩ Fichier déjà présent : $arg2/inputs.npy → SKIP"
            continue
        else
            echo "▶️ Aucun inputs.npy trouvé → Exécution du script"
        fi
        
        # Premier argument : chemin du .yaml sans extension
        arg1="cristobal/${subfolder}/${fname}"

        # Exécute le script Python
        echo "➡️  Exécution : python3 $SCRIPT n=75 +dataset=$arg1 +test_model_dir=$arg2"
        python3 "$SCRIPT" n=75 +dataset="$arg1" +test_model_dir="$arg2"

    done
done

