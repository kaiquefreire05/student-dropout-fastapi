"""
=============================================================================
Suíte de Testes Automatizados com Pytest e TestClient (FastAPI)
=============================================================================
Este módulo valida a integridade de todas as rotas e regras de negócio da API.
O `TestClient` permite fazer requisições HTTP simuladas em memória,
sem a necessidade de rodar o servidor Uvicorn externamente.

Como executar no VS Code:
  python -m pytest tests -v
=============================================================================
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Inicializa o cliente de testes da FastAPI
client = TestClient(app)


def test_root():
    """Valida se a rota raiz (/) responde com status HTTP 200 e entrega a página HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_health():
    """Valida se o endpoint /health confirma que o modelo está carregado e operacional."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["model_name"] == "Logistic Regression"
    assert data["model_accuracy"] > 0.85


def test_model_info():
    """Valida se /model/info expõe os metadados corretos e o benchmark dos 5 modelos."""
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["best_model_name"] == "Logistic Regression"
    assert data["features_count"] == 34
    # Confirma que os modelos do Colab estão registrados no comparativo
    assert "Logistic Regression" in data["benchmark_comparison"]
    assert "Support Vector Classifier (SVC)" in data["benchmark_comparison"]
    assert "Random Forest" in data["benchmark_comparison"]


def test_predict_single_with_original_column_names():
    """
    Valida a predição individual utilizando as chaves exatamente como estão no CSV.
    Exemplo: "Marital status", "Mother's qualification", etc.
    """
    sample_payload = {
        "Marital status": 1,
        "Application mode": 8,
        "Application order": 5,
        "Course": 2,
        "Daytime/evening attendance": 1,
        "Previous qualification": 1,
        "Nationality": 1,
        "Mother's qualification": 13,
        "Father's qualification": 10,
        "Mother's occupation": 6,
        "Father's occupation": 10,
        "Displaced": 1,
        "Educational special needs": 0,
        "Debtor": 0,
        "Tuition fees up to date": 1,
        "Gender": 1,
        "Scholarship holder": 0,
        "Age at enrollment": 20,
        "International": 0,
        "Curricular units 1st sem (credited)": 0,
        "Curricular units 1st sem (enrolled)": 0,
        "Curricular units 1st sem (evaluations)": 0,
        "Curricular units 1st sem (approved)": 0,
        "Curricular units 1st sem (grade)": 0.0,
        "Curricular units 1st sem (without evaluations)": 0,
        "Curricular units 2nd sem (credited)": 0,
        "Curricular units 2nd sem (enrolled)": 0,
        "Curricular units 2nd sem (evaluations)": 0,
        "Curricular units 2nd sem (approved)": 0,
        "Curricular units 2nd sem (grade)": 0.0,
        "Curricular units 2nd sem (without evaluations)": 0,
        "Unemployment rate": 10.8,
        "Inflation rate": 1.4,
        "GDP": 1.74,
    }

    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["prediction"] in [0, 1]
    # Probabilidades devem estar sempre no intervalo [0, 1]
    assert 0.0 <= data["dropout_probability"] <= 1.0
    assert 0.0 <= data["retention_probability"] <= 1.0
    assert data["model_used"] == "Logistic Regression"


def test_predict_single_with_snake_case_names():
    """
    Valida a predição individual utilizando chaves no padrão Python snake_case.
    Exemplo: "marital_status", "mothers_qualification", etc.
    Simula um aluno com alto desempenho e bolsa de estudos (baixa chance de evasão).
    """
    sample_payload = {
        "marital_status": 1,
        "application_mode": 1,
        "application_order": 1,
        "course": 5,
        "daytime_evening_attendance": 1,
        "previous_qualification": 1,
        "nationality": 1,
        "mothers_qualification": 1,
        "fathers_qualification": 1,
        "mothers_occupation": 4,
        "fathers_occupation": 4,
        "displaced": 1,
        "educational_special_needs": 0,
        "debtor": 0,
        "tuition_fees_up_to_date": 1,
        "gender": 0,
        "scholarship_holder": 1,
        "age_at_enrollment": 18,
        "international": 0,
        "curricular_units_1st_sem_credited": 0,
        "curricular_units_1st_sem_enrolled": 6,
        "curricular_units_1st_sem_evaluations": 6,
        "curricular_units_1st_sem_approved": 6,
        "curricular_units_1st_sem_grade": 15.5,
        "curricular_units_1st_sem_without_evaluations": 0,
        "curricular_units_2nd_sem_credited": 0,
        "curricular_units_2nd_sem_enrolled": 6,
        "curricular_units_2nd_sem_evaluations": 6,
        "curricular_units_2nd_sem_approved": 6,
        "curricular_units_2nd_sem_grade": 16.0,
        "curricular_units_2nd_sem_without_evaluations": 0,
        "unemployment_rate": 8.0,
        "inflation_rate": 0.5,
        "gdp": 2.0,
    }

    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 0
    assert "Non-Dropout" in data["prediction_label"]
    assert data["risk_level"] == "Baixo Risco"


def test_predict_batch():
    """Valida a predição em lote de múltiplos alunos e as métricas agregadas da turma."""
    batch_payload = {
        "students": [
            # Aluno 1: Perfil de alto risco (inadimplente, reprovado em tudo)
            {
                "Marital status": 1,
                "Application mode": 8,
                "Application order": 5,
                "Course": 2,
                "Daytime/evening attendance": 1,
                "Previous qualification": 1,
                "Nationality": 1,
                "Mother's qualification": 13,
                "Father's qualification": 10,
                "Mother's occupation": 6,
                "Father's occupation": 10,
                "Displaced": 1,
                "Educational special needs": 0,
                "Debtor": 1,
                "Tuition fees up to date": 0,
                "Gender": 1,
                "Scholarship holder": 0,
                "Age at enrollment": 30,
                "International": 0,
                "Curricular units 1st sem (credited)": 0,
                "Curricular units 1st sem (enrolled)": 6,
                "Curricular units 1st sem (evaluations)": 6,
                "Curricular units 1st sem (approved)": 0,
                "Curricular units 1st sem (grade)": 0.0,
                "Curricular units 1st sem (without evaluations)": 0,
                "Curricular units 2nd sem (credited)": 0,
                "Curricular units 2nd sem (enrolled)": 6,
                "Curricular units 2nd sem (evaluations)": 6,
                "Curricular units 2nd sem (approved)": 0,
                "Curricular units 2nd sem (grade)": 0.0,
                "Curricular units 2nd sem (without evaluations)": 0,
                "Unemployment rate": 12.0,
                "Inflation rate": 2.0,
                "GDP": 1.0,
            },
            # Aluno 2: Perfil de aprovação (mensalidades em dia, notas altas)
            {
                "Marital status": 1,
                "Application mode": 1,
                "Application order": 1,
                "Course": 10,
                "Daytime/evening attendance": 1,
                "Previous qualification": 1,
                "Nationality": 1,
                "Mother's qualification": 1,
                "Father's qualification": 1,
                "Mother's occupation": 1,
                "Father's occupation": 1,
                "Displaced": 0,
                "Educational special needs": 0,
                "Debtor": 0,
                "Tuition fees up to date": 1,
                "Gender": 0,
                "Scholarship holder": 1,
                "Age at enrollment": 18,
                "International": 0,
                "Curricular units 1st sem (credited)": 0,
                "Curricular units 1st sem (enrolled)": 6,
                "Curricular units 1st sem (evaluations)": 6,
                "Curricular units 1st sem (approved)": 6,
                "Curricular units 1st sem (grade)": 16.0,
                "Curricular units 1st sem (without evaluations)": 0,
                "Curricular units 2nd sem (credited)": 0,
                "Curricular units 2nd sem (enrolled)": 6,
                "Curricular units 2nd sem (evaluations)": 6,
                "Curricular units 2nd sem (approved)": 6,
                "Curricular units 2nd sem (grade)": 16.5,
                "Curricular units 2nd sem (without evaluations)": 0,
                "Unemployment rate": 9.0,
                "Inflation rate": 1.0,
                "GDP": 2.0,
            },
        ]
    }

    response = client.post("/predict/batch", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_students"] == 2
    assert len(data["predictions"]) == 2
    assert "summary" in data
    assert data["summary"]["total_students"] == 2


def test_predict_batch_empty():
    """Valida se uma requisição com lista vazia é rejeitada com erro HTTP 400 Bad Request."""
    response = client.post("/predict/batch", json={"students": []})
    assert response.status_code == 400
