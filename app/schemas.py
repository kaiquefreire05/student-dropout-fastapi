"""
=============================================================================
Esquemas de Validação e Serialização de Dados (Pydantic Models)
=============================================================================
Este módulo define a estrutura formal dos dados que transitam pela API.
O Pydantic garante:
1. Validação estrita de tipos em tempo de execução (impede strings onde deve ser int/float).
2. Documentação automática com exemplos interativos no Swagger UI (/docs).
3. Flexibilidade de formato: graças ao parâmetro `alias` e `populate_by_name=True`,
   a API aceita tanto os nomes originais do CSV (ex: "Curricular units 1st sem (grade)")
   quanto nomes idiomáticos em Python snake_case (ex: "curricular_units_1st_sem_grade").
=============================================================================
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class StudentFeatures(BaseModel):
    """
    Representação dos 34 atributos de um estudante universitário.
    Estes são os mesmos atributos utilizados para treinar os 5 modelos no Colab.
    """

    # Configuração do Pydantic V2
    model_config = ConfigDict(
        populate_by_name=True,  # Permite enviar tanto pelo nome do campo quanto pelo alias
        json_schema_extra={
            # Exemplo exibido automaticamente na documentação do Swagger
            "example": {
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
        },
    )

    # -----------------------------------------------------------------------
    # 1. Dados Demográficos e de Ingresso
    # -----------------------------------------------------------------------
    marital_status: int = Field(1, alias="Marital status", description="Estado civil (1: Solteiro, 2: Casado, 3: Viúvo, 4: Divorciado, 5: União de fato, 6: Separado)")
    application_mode: int = Field(8, alias="Application mode", description="Código do modo de candidatura ao ensino superior")
    application_order: int = Field(5, alias="Application order", description="Ordem de preferência de escolha do curso (0 a 9)")
    course: int = Field(2, alias="Course", description="Código identificador do curso")
    daytime_evening_attendance: int = Field(1, alias="Daytime/evening attendance", description="Turno de frequência: 1 para diurno, 0 para noturno")
    previous_qualification: int = Field(1, alias="Previous qualification", description="Nível de escolaridade anterior ao ingresso")
    nationality: int = Field(1, alias="Nationality", description="Nacionalidade do estudante (1: Portuguesa, etc.)")

    # -----------------------------------------------------------------------
    # 2. Dados Familiares e Socioeconômicos
    # -----------------------------------------------------------------------
    mothers_qualification: int = Field(13, alias="Mother's qualification", description="Grau de instrução da mãe")
    fathers_qualification: int = Field(10, alias="Father's qualification", description="Grau de instrução do pai")
    mothers_occupation: int = Field(6, alias="Mother's occupation", description="Código da ocupação profissional da mãe")
    fathers_occupation: int = Field(10, alias="Father's occupation", description="Código da ocupação profissional do pai")
    displaced: int = Field(1, alias="Displaced", description="Estudante deslocado de sua residência original (1: Sim, 0: Não)")
    educational_special_needs: int = Field(0, alias="Educational special needs", description="Necessidades educacionais especiais (1: Sim, 0: Não)")
    debtor: int = Field(0, alias="Debtor", description="Estudante possui dívidas abertas (1: Sim, 0: Não)")
    tuition_fees_up_to_date: int = Field(1, alias="Tuition fees up to date", description="Pagamento de propinas/mensalidades em dia (1: Sim, 0: Não)")
    gender: int = Field(1, alias="Gender", description="Gênero: 1 para Masculino, 0 para Feminino")
    scholarship_holder: int = Field(0, alias="Scholarship holder", description="Estudante bolsista (1: Sim, 0: Não)")
    age_at_enrollment: int = Field(20, alias="Age at enrollment", description="Idade do estudante no momento da matrícula")
    international: int = Field(0, alias="International", description="Estudante estrangeiro/internacional (1: Sim, 0: Não)")

    # -----------------------------------------------------------------------
    # 3. Desempenho Acadêmico - 1º Semestre
    # -----------------------------------------------------------------------
    curricular_units_1st_sem_credited: int = Field(0, alias="Curricular units 1st sem (credited)", description="Disciplinas creditadas por equivalência no 1º semestre")
    curricular_units_1st_sem_enrolled: int = Field(0, alias="Curricular units 1st sem (enrolled)", description="Disciplinas matriculadas no 1º semestre")
    curricular_units_1st_sem_evaluations: int = Field(0, alias="Curricular units 1st sem (evaluations)", description="Avaliações realizadas no 1º semestre")
    curricular_units_1st_sem_approved: int = Field(0, alias="Curricular units 1st sem (approved)", description="Disciplinas aprovadas no 1º semestre")
    curricular_units_1st_sem_grade: float = Field(0.0, alias="Curricular units 1st sem (grade)", description="Nota média ponderada no 1º semestre (escala 0 a 20)")
    curricular_units_1st_sem_without_evaluations: int = Field(0, alias="Curricular units 1st sem (without evaluations)", description="Disciplinas sem avaliação no 1º semestre")

    # -----------------------------------------------------------------------
    # 4. Desempenho Acadêmico - 2º Semestre
    # -----------------------------------------------------------------------
    curricular_units_2nd_sem_credited: int = Field(0, alias="Curricular units 2nd sem (credited)", description="Disciplinas creditadas por equivalência no 2º semestre")
    curricular_units_2nd_sem_enrolled: int = Field(0, alias="Curricular units 2nd sem (enrolled)", description="Disciplinas matriculadas no 2º semestre")
    curricular_units_2nd_sem_evaluations: int = Field(0, alias="Curricular units 2nd sem (evaluations)", description="Avaliações realizadas no 2º semestre")
    curricular_units_2nd_sem_approved: int = Field(0, alias="Curricular units 2nd sem (approved)", description="Disciplinas aprovadas no 2º semestre")
    curricular_units_2nd_sem_grade: float = Field(0.0, alias="Curricular units 2nd sem (grade)", description="Nota média ponderada no 2º semestre (escala 0 a 20)")
    curricular_units_2nd_sem_without_evaluations: int = Field(0, alias="Curricular units 2nd sem (without evaluations)", description="Disciplinas sem avaliação no 2º semestre")

    # -----------------------------------------------------------------------
    # 5. Indicadores Macroeconômicos da Região
    # -----------------------------------------------------------------------
    unemployment_rate: float = Field(10.8, alias="Unemployment rate", description="Taxa de desemprego na região (%)")
    inflation_rate: float = Field(1.4, alias="Inflation rate", description="Taxa de inflação (%)")
    gdp: float = Field(1.74, alias="GDP", description="Taxa de crescimento do PIB (%)")

    def to_features_list(self) -> List[float]:
        """
        ATENÇÃO: A ordem dos atributos nesta lista DEVE ser idêntica
        à ordem das colunas em que o modelo foi treinado.
        Qualquer inversão alteraria completamente o resultado da inferência.
        """
        return [
            float(self.marital_status),
            float(self.application_mode),
            float(self.application_order),
            float(self.course),
            float(self.daytime_evening_attendance),
            float(self.previous_qualification),
            float(self.nationality),
            float(self.mothers_qualification),
            float(self.fathers_qualification),
            float(self.mothers_occupation),
            float(self.fathers_occupation),
            float(self.displaced),
            float(self.educational_special_needs),
            float(self.debtor),
            float(self.tuition_fees_up_to_date),
            float(self.gender),
            float(self.scholarship_holder),
            float(self.age_at_enrollment),
            float(self.international),
            float(self.curricular_units_1st_sem_credited),
            float(self.curricular_units_1st_sem_enrolled),
            float(self.curricular_units_1st_sem_evaluations),
            float(self.curricular_units_1st_sem_approved),
            float(self.curricular_units_1st_sem_grade),
            float(self.curricular_units_1st_sem_without_evaluations),
            float(self.curricular_units_2nd_sem_credited),
            float(self.curricular_units_2nd_sem_enrolled),
            float(self.curricular_units_2nd_sem_evaluations),
            float(self.curricular_units_2nd_sem_approved),
            float(self.curricular_units_2nd_sem_grade),
            float(self.curricular_units_2nd_sem_without_evaluations),
            float(self.unemployment_rate),
            float(self.inflation_rate),
            float(self.gdp),
        ]


class BatchPredictionRequest(BaseModel):
    """Esquema de requisição para predição em lote."""
    students: List[StudentFeatures] = Field(..., description="Lista contendo os dados de múltiplos estudantes")


class PredictionResponse(BaseModel):
    """Esquema de resposta para inferência individual."""
    prediction: int = Field(..., description="Classe predita: 1 para Dropout (Evasão), 0 para Não-Evasão")
    prediction_label: str = Field(..., description="Descrição textual amigável do resultado")
    risk_level: str = Field(..., description="Classificação do risco de evasão (Baixo Risco, Médio Risco, Alto Risco de Evasão)")
    dropout_probability: float = Field(..., description="Probabilidade estimada de evasão escolar (entre 0 e 1)")
    retention_probability: float = Field(..., description="Probabilidade estimada de permanência/conclusão")
    model_used: str = Field(..., description="Nome do modelo utilizado na inferência")
    model_accuracy: float = Field(..., description="Acurácia do modelo no conjunto de teste")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora da inferência em UTC")


class BatchPredictionResponse(BaseModel):
    """Esquema de resposta para inferência em lote com sumário executivo."""
    total_students: int = Field(..., description="Total de estudantes avaliados")
    predictions: List[PredictionResponse] = Field(..., description="Lista com os resultados de cada estudante")
    summary: Dict[str, Any] = Field(..., description="Estatísticas agregadas da turma avaliada")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora da inferência em UTC")


class HealthResponse(BaseModel):
    """Esquema de resposta do healthcheck da API."""
    status: str = Field(..., description="Status do serviço (ex: 'healthy')")
    model_loaded: bool = Field(..., description="Booleano confirmando se os artefatos estão carregados")
    model_name: str = Field(..., description="Nome do melhor modelo ativo")
    model_accuracy: float = Field(..., description="Acurácia do modelo ativo")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora em UTC")


class ModelInfoResponse(BaseModel):
    """Esquema com todos os metadados técnicos do modelo e comparação com os outros 4 modelos."""
    best_model_name: str
    best_accuracy: float
    hyperparameters: Dict[str, Any]
    target_mapping: Dict[str, str]
    features_count: int
    features: List[str]
    metrics: Dict[str, Any]
    benchmark_comparison: Dict[str, Any]
