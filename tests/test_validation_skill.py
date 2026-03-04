import pytest
import asyncio
from typing import Annotated, Sequence, TypedDict
import operator
from langchain_core.messages import BaseMessage, AIMessage

from src.rag.validator_skill import node_validator

@pytest.mark.asyncio
async def test_validator_skill_passed():
    state = {
        "messages": [AIMessage(content="Segundo o artigo 15 do manual...")],
        "context_docs": "O Art. 15 diz que bla bla bla.",
        "validation_passed": None
    }
    
    result = await node_validator(state)
    assert result["validation_passed"] is True
    
@pytest.mark.asyncio
async def test_validator_skill_failed():
    state = {
        "messages": [AIMessage(content="O procedimento está na página 42.")],
        "context_docs": "Página 10: Inelegibilidade.",
        "validation_passed": None
    }
    
    result = await node_validator(state)
    assert result["validation_passed"] is False

@pytest.mark.asyncio
async def test_validator_skill_inconclusivo():
    state = {
        "messages": [AIMessage(content="INCONCLUSIVO.")],
        "context_docs": "Não há nada aqui.",
        "validation_passed": None
    }
    
    result = await node_validator(state)
    assert result["validation_passed"] is True
