"""
=============================================================================
Aplicação FastAPI - API de Predição de Evasão Escolar (Student Dropout)
=============================================================================
Este módulo define os endpoints da API HTTP utilizando o framework FastAPI.
Ele expõe o modelo de Machine Learning que obteve a melhor acurácia no Google
Colab (Regressão Logística com ~86.67% / 87.0% de acurácia no teste).

Rotas disponíveis:
  - GET  /              : Interface web interativa para testes no navegador
  - GET  /health        : Healthcheck para monitorar o status da API e do modelo
  - GET  /model/info    : Metadados, hiperparâmetros e benchmark comparativo
  - POST /predict       : Predição individual para 1 estudante
  - POST /predict/batch : Predição em lote para múltiplos estudantes
=============================================================================
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

# Importação do serviço singleton que gerencia o modelo e o scaler
from app.model import model_service

# Importação dos esquemas Pydantic para validação e serialização de dados
from app.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
    StudentFeatures,
)

# ---------------------------------------------------------------------------
# Configuração de Caminhos Base
# ---------------------------------------------------------------------------
# BASE_DIR aponta para a raiz do projeto (student_dropout_fastapi)
BASE_DIR = Path(__file__).resolve().parent.parent

# STATIC_INDEX aponta para o arquivo HTML da interface gráfica web
STATIC_INDEX = BASE_DIR / "app" / "static" / "index.html"

# ---------------------------------------------------------------------------
# Instanciação da Aplicação FastAPI com Documentação Swagger Automática
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Student Dropout Prediction API",
    description=(
        "API para predição de evasão escolar baseada no modelo de Machine Learning "
        "com a melhor acurácia do Google Colab (Regressão Logística com 87.0% de acurácia no teste).\n\n"
        "Suporta inferência individual, em lote, consulta de metadados e benchmark comparativo."
    ),
    version="1.0.0",
    docs_url="/docs",      # URL da documentação interativa Swagger UI
    redoc_url="/redoc",    # URL da documentação técnica ReDoc
)

# ---------------------------------------------------------------------------
# Configuração de Middleware CORS (Cross-Origin Resource Sharing)
# Permite que aplicações web (React, Vue, mobile, etc.) consumam esta API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Permite requisições de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],       # Permite todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],       # Permite todos os cabeçalhos HTTP
)


# ===========================================================================
# ROTA 1: Interface Web Interativa (Raiz "/")
# ===========================================================================
@app.get(
    "/",
    summary="Página Inicial / Interface Web",
    response_class=HTMLResponse,
    include_in_schema=False,  # Oculta da documentação OpenAPI para manter o foco nos endpoints REST
)
def root():
    """
    Retorna o painel visual (HTML/CSS/JS) no navegador.
    Permite ao usuário testar o modelo preenchendo os dados diretamente na tela.
    """
    if STATIC_INDEX.exists():
        return FileResponse(STATIC_INDEX)
    return HTMLResponse("<h2>Student Dropout Prediction API está online! Acesse <a href='/docs'>/docs</a></h2>")


# ===========================================================================
# ROTA 2: Verificação de Integridade (Health Check)
# ===========================================================================
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificação de Saúde do Serviço",
    tags=["Monitoramento"],
)
def health_check():
    """
    Verifica a saúde do serviço:
    - Retorna status: 'healthy'
    - Confirma se o modelo e o scaler foram carregados em memória com sucesso
    - Informa o nome do modelo ativo e sua acurácia no teste
    """
    return HealthResponse(
        status="healthy",
        model_loaded=model_service.is_loaded,
        model_name=model_service.metadata.get("best_model_name", "Logistic Regression"),
        model_accuracy=model_service.metadata.get("best_accuracy", 0.8667),
    )


# ===========================================================================
# ROTA 3: Metadados, Arquitetura e Benchmark dos Modelos
# ===========================================================================
@app.get(
    "/model/info",
    response_model=ModelInfoResponse,
    summary="Informações e Benchmark do Modelo",
    tags=["Modelo"],
)
def get_model_info():
    """
    Retorna a ficha técnica completa do modelo em produção:
    - Nome do melhor modelo e sua acurácia
    - Hiperparâmetros utilizados no treinamento
    - Lista das 34 features exigidas na entrada
    - Matriz de confusão e relatório de classificação
    - Benchmark comparativo dos 5 modelos avaliados no Google Colab:
      (Regressão Logística, SVC, Random Forest, Decision Tree e KNN)
    """
    if not model_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O modelo de Machine Learning ainda não foi carregado em memória.",
        )

    meta = model_service.metadata
    return ModelInfoResponse(
        best_model_name=meta.get("best_model_name", "Logistic Regression"),
        best_accuracy=meta.get("best_accuracy", 0.8667),
        hyperparameters=meta.get("hyperparameters", {}),
        target_mapping=meta.get("target_mapping", {}),
        features_count=len(meta.get("features", [])),
        features=meta.get("features", []),
        metrics=meta.get("metrics", {}),
        benchmark_comparison=meta.get("benchmark_comparison", {}),
    )


# ===========================================================================
# ROTA 4: Inferência Individual (POST /predict)
# ===========================================================================
@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predição Individual de Estudante",
    tags=["Predição"],
)
def predict_student(student: StudentFeatures):
    """
    Recebe os 34 atributos de um estudante e realiza a inferência:
    
    Passos executados:
    1. Validação dos tipos de dados via Pydantic (StudentFeatures).
    2. Ordenação das features na ordem exata de treinamento.
    3. Padronização dos valores via StandardScaler (scaler.joblib).
    4. Cálculo da predição binária (0 = Não-Evasão, 1 = Evasão).
    5. Cálculo das probabilidades calibradas (predict_proba).
    6. Determinação da faixa de risco (Baixo Risco, Médio Risco, Alto Risco de Evasão).
    """
    try:
        return model_service.predict_one(student)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro durante o processamento da inferência: {str(e)}",
        )


# ===========================================================================
# ROTA 5: Inferência em Lote (POST /predict/batch)
# ===========================================================================
@app.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Predição em Lote (Múltiplos Estudantes)",
    tags=["Predição"],
)
def predict_batch_students(payload: BatchPredictionRequest):
    """
    Recebe uma lista de estudantes e processa todos em uma única chamada.
    
    Retorna:
    - Lista com a predição detalhada de cada aluno.
    - Sumário executivo: total de alunos, total de evasões previstas,
      percentual previsto de evasão da turma e probabilidade média de evasão.
    """
    # Validação para evitar lista vazia
    if not payload.students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A lista de estudantes não pode ser vazia.",
        )
    try:
        return model_service.predict_batch(payload.students)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro durante a predição em lote: {str(e)}",
        )
