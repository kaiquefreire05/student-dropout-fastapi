"""
=============================================================================
Camada de Serviço de Machine Learning (ML Service)
=============================================================================
Este módulo é responsável por:
1. Carregar os artefatos serializados do modelo em disco (.joblib e .json).
2. Manter uma instância única em memória (padrão Singleton) para evitar recargas
   lentas a cada requisição HTTP.
3. Transformar os dados de entrada recebidos da API usando o mesmo `StandardScaler`
   ajustado no treinamento.
4. Executar o método `predict` (classe predita) e `predict_proba` (probabilidade).
5. Calcular a classificação heurística de risco de evasão (Baixo, Médio, Alto).
=============================================================================
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import joblib
import numpy as np
import pandas as pd

from app.schemas import (
    BatchPredictionResponse,
    PredictionResponse,
    StudentFeatures,
)

# Caminho para o diretório raiz do projeto e pasta de modelos
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"


class MLModelService:
    """
    Serviço que gerencia o ciclo de vida do modelo de Machine Learning.
    É instanciado uma única vez ao iniciar o servidor FastAPI.
    """

    def __init__(self):
        self.model = None              # Instância do modelo scikit-learn (Regressão Logística)
        self.scaler = None             # Objeto StandardScaler ajustado no treinamento
        self.metadata: Dict[str, Any] = {} # Dicionário com métricas e lista de features
        self.is_loaded = False         # Flag booleana indicando status de carregamento
        self.load()                    # Executa o carregamento inicial dos artefatos

    def load(self):
        """
        Lê os arquivos gerados pelo script de treinamento (scripts/train.py):
        - best_model.joblib: O classificador com a maior acurácia (86.67% / 87.0%)
        - scaler.joblib: O padronizador de escala para normalizar as 34 variáveis
        - model_metadata.json: Relatório completo de métricas e comparação dos 5 modelos
        """
        model_path = MODELS_DIR / "best_model.joblib"
        scaler_path = MODELS_DIR / "scaler.joblib"
        metadata_path = MODELS_DIR / "model_metadata.json"

        # Validação preventiva de existência dos arquivos
        if not model_path.exists() or not scaler_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"Artefatos do modelo não encontrados na pasta {MODELS_DIR}. "
                "Para gerá-los, execute no terminal: python scripts/train.py"
            )

        # Desserialização dos objetos com joblib (rápido e otimizado para numpy)
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

        # Leitura dos metadados salvos em JSON (UTF-8)
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.is_loaded = True
        print(f"[OK] Modelo '{self.metadata.get('best_model_name')}' carregado com sucesso!")

    def _determine_risk_level(self, dropout_prob: float) -> str:
        """
        Classifica a probabilidade contínua de evasão em faixas de risco acionáveis:
        - >= 70%: Alto Risco de Evasão (Intervenção prioritária da instituição)
        - 40% a 69%: Médio Risco (Acompanhamento pedagógico recomendado)
        - < 40%: Baixo Risco (Estudante com boa tendência de permanência)
        """
        if dropout_prob >= 0.70:
            return "Alto Risco de Evasão"
        elif dropout_prob >= 0.40:
            return "Médio Risco"
        else:
            return "Baixo Risco"

    def predict_one(self, student: StudentFeatures) -> PredictionResponse:
        """
        Processa a predição para um único estudante.

        Parâmetros:
          student (StudentFeatures): Objeto Pydantic com os 34 atributos do aluno.

        Retorna:
          PredictionResponse: Objeto com a classe predita, rótulo, risco e probabilidades.
        """
        # 1. Extrai a lista de 34 valores float na exata ordem das colunas do dataset
        features = student.to_features_list()

        # 2. Converte para DataFrame com os nomes originais das colunas
        # Isso garante compatibilidade total com o StandardScaler treinado
        df_input = pd.DataFrame([features], columns=self.metadata["features"])

        # 3. Aplica a padronização Z-score: z = (x - média) / desvio_padrão
        scaled_array = self.scaler.transform(df_input)

        # 4. Executa a predição da classe (0 = Não-Evasão, 1 = Evasão)
        pred = int(self.model.predict(scaled_array)[0])

        # 5. Obtém a probabilidade estimada para cada classe
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(scaled_array)[0]
            retention_prob = float(round(probs[0], 4)) # Probabilidade da classe 0 (Formado/Matriculado)
            dropout_prob = float(round(probs[1], 4))   # Probabilidade da classe 1 (Evasão)
        else:
            # Fallback determinístico caso o modelo não suporte probabilidades
            dropout_prob = 1.0 if pred == 1 else 0.0
            retention_prob = 1.0 - dropout_prob

        # 6. Mapeamento de texto explicativo
        label = "Dropout (Evasão Escolar)" if pred == 1 else "Non-Dropout (Permanência / Conclusão)"
        risk_level = self._determine_risk_level(dropout_prob)

        # 7. Montagem do payload de resposta estruturado
        return PredictionResponse(
            prediction=pred,
            prediction_label=label,
            risk_level=risk_level,
            dropout_probability=dropout_prob,
            retention_probability=retention_prob,
            model_used=self.metadata.get("best_model_name", "Logistic Regression"),
            model_accuracy=self.metadata.get("best_accuracy", 0.8667),
        )

    def predict_batch(self, students: List[StudentFeatures]) -> BatchPredictionResponse:
        """
        Processa uma lista de estudantes em lote (turmas ou semestres).

        Retorna:
          BatchPredictionResponse: Lista de predições individuais + estatísticas agregadas.
        """
        # Executa a inferência para cada estudante da lista
        results = [self.predict_one(s) for s in students]

        # Contabilização de métricas agregadas da turma
        dropout_count = sum(1 for r in results if r.prediction == 1)
        retention_count = sum(1 for r in results if r.prediction == 0)
        avg_dropout_prob = round(
            float(np.mean([r.dropout_probability for r in results])), 4
        ) if results else 0.0

        # Sumário consolidado para tomada de decisão institucional
        summary = {
            "total_students": len(results),
            "predicted_dropout_count": dropout_count,
            "predicted_retention_count": retention_count,
            "dropout_rate_percent": round((dropout_count / len(results)) * 100, 2) if results else 0.0,
            "average_dropout_probability": avg_dropout_prob,
        }

        return BatchPredictionResponse(
            total_students=len(results),
            predictions=results,
            summary=summary,
        )


# Instância global (Singleton) utilizada por toda a aplicação FastAPI
model_service = MLModelService()
