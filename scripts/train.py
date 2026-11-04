"""
=============================================================================
Pipeline de Treinamento, Benchmark e Exportação do Melhor Modelo de ML
=============================================================================
Este script reproduz o experimento completo executado no Google Colab:
  Link: https://colab.research.google.com/drive/1u0L7dhDVGh_r0NCNaKmYZD72lQwU1s7K

Etapas do Pipeline:
  1. Leitura do dataset CSV de estudantes (data/student-dropout-dataset.csv).
  2. Correção de erro de digitação de coluna ('Nacionality' -> 'Nationality').
  3. Binarização da variável alvo ('Target'):
     - 1 = Dropout (Evasão Escolar)
     - 0 = Graduate / Enrolled (Conclusão / Permanência)
  4. Separação de X (34 atributos preditivos) e y (variável alvo).
  5. Padronização de escala com StandardScaler: z = (x - média) / desvio_padrão.
  6. Divisão reprodutível (random_state=42):
     - 80% Treino + Validação / 20% Teste Independente
     - Do conjunto de treino, 80% Treino Efetivo / 20% Validação
  7. Treinamento comparativo de 5 algoritmos supervisionados:
     - Regressão Logística (LogisticRegression)
     - Árvore de Decisão (DecisionTreeClassifier)
     - Máquinas de Vetores de Suporte (SVC com kernel RBF)
     - Floresta Aleatória (RandomForestClassifier otimizado)
     - K-Vizinhos Mais Próximos (KNeighborsClassifier com k=13)
  8. Avaliação de acurácia no conjunto de teste independente.
  9. Identificação automática do algoritmo campeão (Regressão Logística).
 10. Serialização dos artefatos (best_model.joblib, scaler.joblib, model_metadata.json).
=============================================================================
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

# ---------------------------------------------------------------------------
# Definição de Diretórios do Projeto
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "student-dropout-dataset.csv"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def train_and_select_best_model():
    """Executa o pipeline completo de treinamento, avaliação e exportação."""
    
    # -----------------------------------------------------------------------
    # 1. Carregamento do Dataset
    # -----------------------------------------------------------------------
    print(f"[*] Carregando dataset de: {DATA_PATH}")
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo de dados não encontrado em {DATA_PATH}. "
            "Certifique-se de que o arquivo 'student-dropout-dataset.csv' está na pasta 'data'."
        )

    data = pd.read_csv(DATA_PATH)
    print(f"[+] Dataset carregado com sucesso: {data.shape[0]} linhas, {data.shape[1]} colunas.")

    # -----------------------------------------------------------------------
    # 2. Pré-processamento e Limpeza
    # -----------------------------------------------------------------------
    # No notebook do Colab, o autor corrige um erro de digitação na coluna Nacionality
    if "Nacionality" in data.columns:
        data.rename(columns={"Nacionality": "Nationality"}, inplace=True)

    # -----------------------------------------------------------------------
    # 3. Transformação da Variável Alvo (Target)
    # No notebook original (Célula 50):
    # - Cria-se variáveis dummy para a coluna Target ('Dropout', 'Enrolled', 'Graduate')
    # - Descarta-se as colunas 'Enrolled' e 'Graduate'
    # - Mantém-se apenas 'Dropout': 1 se desistiu, 0 se concluiu ou continua matriculado
    # -----------------------------------------------------------------------
    target_dummies = pd.get_dummies(data["Target"])
    for col in ["Enrolled", "Graduate"]:
        if col in target_dummies.columns:
            target_dummies.drop(columns=[col], inplace=True)

    data["Target"] = target_dummies["Dropout"].astype(int)

    # -----------------------------------------------------------------------
    # 4. Separação de Atributos (X) e Rótulos (y)
    # -----------------------------------------------------------------------
    y = np.array(data["Target"])
    X_features = data.drop("Target", axis=1)
    feature_names = list(X_features.columns)

    print(f"[+] Quantidade de atributos (features): {len(feature_names)}")
    print(f"[+] Distribuição do Target (0=Não-Evasão, 1=Evasão): {dict(pd.Series(y).value_counts())}")

    # -----------------------------------------------------------------------
    # 5. Normalização de Escala (StandardScaler)
    # Como variáveis como 'Idade', 'PIB' e 'Notas' possuem escalas muito distintas,
    # a padronização Z-Score é fundamental para convergência da Regressão Logística e SVM.
    # -----------------------------------------------------------------------
    scaler = StandardScaler()
    X = scaler.fit_transform(X_features)

    # -----------------------------------------------------------------------
    # 6. Divisão Reprodutível dos Dados
    # Célula 55 do Colab: Divisão Treino/Teste (80% treino / 20% teste, random_state=42)
    # -----------------------------------------------------------------------
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Célula 57 do Colab: Divisão Treino/Validação (80% treino / 20% validação, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.2, random_state=42
    )

    print(f"[+] Tamanho do conjunto de treino efetivo: {X_train.shape[0]} amostras")
    print(f"[+] Tamanho do conjunto de validação:       {X_val.shape[0]} amostras")
    print(f"[+] Tamanho do conjunto de teste (inédito): {X_test.shape[0]} amostras")

    # -----------------------------------------------------------------------
    # 7. Treinamento e Avaliação dos 5 Modelos
    # -----------------------------------------------------------------------

    # Modelo 1: Regressão Logística (Célula 62)
    # Modelo linear com regularização L2 e função sigmoide
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    lr_model.fit(X_train, y_train)
    lr_test_pred = lr_model.predict(X_test)
    lr_acc = round(accuracy_score(y_test, lr_test_pred), 4)

    # Modelo 2: Árvore de Decisão (Célula 68)
    # Profundidade max_depth=6 identificada na curva de validação do notebook
    dt_model = DecisionTreeClassifier(max_depth=6, random_state=42)
    dt_model.fit(X_train, y_train)
    dt_test_pred = dt_model.predict(X_test)
    dt_acc = round(accuracy_score(y_test, dt_test_pred), 4)

    # Modelo 3: Máquinas de Vetores de Suporte - SVM (Célula 75)
    # Kernel RBF identificado como o melhor na validação do notebook
    svm_model = SVC(kernel="rbf", random_state=42, probability=True)
    svm_model.fit(X_train, y_train)
    svm_test_pred = svm_model.predict(X_test)
    svm_acc = round(accuracy_score(y_test, svm_test_pred), 4)

    # Modelo 4: Floresta Aleatória - Random Forest (Célula 81)
    # Melhores hiperparâmetros obtidos via GridSearchCV no notebook
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        max_leaf_nodes=9,
        max_features=None,
        random_state=42,
    )
    rf_model.fit(X_train, y_train)
    rf_test_pred = rf_model.predict(X_test)
    rf_acc = round(accuracy_score(y_test, rf_test_pred), 4)

    # Modelo 5: K-Nearest Neighbors - KNN (Célula 92)
    # Melhores vizinhos (k=13) encontrados pelo elbow method do notebook
    knn_model = KNeighborsClassifier(n_neighbors=13)
    knn_model.fit(X_train, y_train)
    knn_test_pred = knn_model.predict(X_test)
    knn_acc = round(accuracy_score(y_test, knn_test_pred), 4)

    # Dicionário consolidado para ranking
    comparison = {
        "Logistic Regression": {
            "model": lr_model,
            "test_accuracy": lr_acc,
            "params": {"max_iter": 1000, "random_state": 42},
            "predictions": lr_test_pred,
        },
        "Support Vector Classifier (SVC)": {
            "model": svm_model,
            "test_accuracy": svm_acc,
            "params": {"kernel": "rbf", "random_state": 42, "probability": True},
            "predictions": svm_test_pred,
        },
        "Random Forest": {
            "model": rf_model,
            "test_accuracy": rf_acc,
            "params": {
                "n_estimators": 100,
                "max_depth": 6,
                "max_leaf_nodes": 9,
                "max_features": None,
                "random_state": 42,
            },
            "predictions": rf_test_pred,
        },
        "Decision Tree": {
            "model": dt_model,
            "test_accuracy": dt_acc,
            "params": {"max_depth": 6, "random_state": 42},
            "predictions": dt_test_pred,
        },
        "K-Nearest Neighbors (KNN)": {
            "model": knn_model,
            "test_accuracy": knn_acc,
            "params": {"n_neighbors": 13},
            "predictions": knn_test_pred,
        },
    }

    # -----------------------------------------------------------------------
    # 8. Exibição da Tabela de Benchmark
    # -----------------------------------------------------------------------
    print("\n================ COMPARAÇÃO DE ACURÁCIA (TESTE) ================")
    for name, data_m in sorted(
        comparison.items(), key=lambda item: item[1]["test_accuracy"], reverse=True
    ):
        print(f" - {name:<32}: {data_m['test_accuracy'] * 100:.2f}%")
    print("=================================================================\n")

    # -----------------------------------------------------------------------
    # 9. Seleção Automática do Modelo com Maior Acurácia
    # -----------------------------------------------------------------------
    best_name = max(comparison, key=lambda k: comparison[k]["test_accuracy"])
    best_info = comparison[best_name]
    best_model = best_info["model"]
    best_acc = best_info["test_accuracy"]

    print(f"[*] Melhor modelo selecionado: {best_name} com {best_acc * 100:.2f}% de acuracia!")

    # Cálculo da matriz de confusão e relatório de precisão/recall/F1
    cm = confusion_matrix(y_test, best_info["predictions"]).tolist()
    cr = classification_report(y_test, best_info["predictions"], output_dict=True)

    # -----------------------------------------------------------------------
    # 10. Serialização e Salvamento dos Artefatos
    # -----------------------------------------------------------------------
    model_file = MODELS_DIR / "best_model.joblib"
    scaler_file = MODELS_DIR / "scaler.joblib"
    metadata_file = MODELS_DIR / "model_metadata.json"

    # Salva o modelo e o scaler com joblib
    joblib.dump(best_model, model_file)
    joblib.dump(scaler, scaler_file)

    # Prepara o JSON com todos os metadados para a rota /model/info da API
    metadata = {
        "best_model_name": best_name,
        "best_accuracy": best_acc,
        "best_model_file": model_file.name,
        "scaler_file": scaler_file.name,
        "hyperparameters": best_info["params"],
        "target_mapping": {
            "0": "Non-Dropout (Graduate / Enrolled)",
            "1": "Dropout (Evasao Escolar)",
        },
        "features": feature_names,
        "metrics": {
            "accuracy": best_acc,
            "confusion_matrix": cm,
            "classification_report": cr,
        },
        "benchmark_comparison": {
            name: {
                "test_accuracy": data_m["test_accuracy"],
                "hyperparameters": data_m["params"],
            }
            for name, data_m in comparison.items()
        },
    }

    # Salva o arquivo JSON de metadados
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[OK] Modelo salvo em: {model_file}")
    print(f"[OK] Scaler salvo em: {scaler_file}")
    print(f"[OK] Metadados salvos em: {metadata_file}")


if __name__ == "__main__":
    train_and_select_best_model()
