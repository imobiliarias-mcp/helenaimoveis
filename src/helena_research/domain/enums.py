"""Domain enumerations for real estate transactions, property types, and ordering."""

from enum import Enum


class TransactionType(str, Enum):
    """Transaction purpose: rental or sale."""

    LOCACAO = "locacao"
    VENDA = "venda"
    TODOS = "todos"


class SortOrder(str, Enum):
    """Sorting order for property search listings."""

    DEFAULT = ""
    MENOR_VALOR = "menor_valor"
    MAIOR_VALOR = "maior_valor"
    RECENTES = "recentes"


class PropertyType(str, Enum):
    """Known property categories on the Helena Imóveis platform."""

    TODOS = "todos"
    APARTAMENTO = "apartamento"
    CASA = "casa"
    COMERCIAL = "comercial"
    KITNET = "kitnet"
    LOJA = "loja"
    LOTE = "lote"
    POUSADA = "pousada"
    COBERTURA = "cobertura"
    CONSULTORIO_MEDICO = "consultorio-medico"
    STUDIO = "studio"
    CASA_GEMINADA = "casa-geminada"
    RESIDENCIAL_E_COMERCIAL = "residencial-e-comercial"
