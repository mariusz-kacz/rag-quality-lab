from rag_quality_lab.routing.categories import (
    CATEGORY_BY_NAME,
    REQUIRED_CATEGORIES,
    category_descriptions,
    category_names,
    get_category,
)
from rag_quality_lab.schemas import REQUIRED_KNOWLEDGE_CATEGORIES


def test_required_categories_match_schema_names_in_order() -> None:
    assert category_names() == REQUIRED_KNOWLEDGE_CATEGORIES
    assert len(REQUIRED_CATEGORIES) == 5
    assert set(CATEGORY_BY_NAME) == set(REQUIRED_KNOWLEDGE_CATEGORIES)


def test_required_categories_have_descriptions_and_embedding_refs() -> None:
    descriptions = category_descriptions()

    for category in REQUIRED_CATEGORIES:
        assert category.description
        assert len(category.description.split()) >= 8
        assert category.embedding_ref
        assert descriptions[category.name] == category.description


def test_get_category_returns_category_by_string_or_enum_value() -> None:
    category = get_category("RAG and context handling")

    assert category.name == "RAG and context handling"
    assert get_category(category.name) == category
