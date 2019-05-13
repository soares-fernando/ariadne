import json
from unittest.mock import ANY, Mock

from ariadne.contrib.django.views import GraphQLView


def execute_query(request_factory, schema, query, **kwargs):
    view = GraphQLView.as_view(schema=schema, **kwargs)
    request = request_factory.post(
        "/graphql/", data=query, content_type="application/json"
    )
    response = view(request)
    return json.loads(response.content)


def test_custom_context_value_is_passed_to_resolvers(schema, request_factory):
    data = execute_query(
        request_factory,
        schema,
        {"query": "{ testContext }"},
        context_value={"test": "TEST-CONTEXT"},
    )
    assert data == {"data": {"testContext": "TEST-CONTEXT"}}


def test_custom_context_value_function_is_set_and_called_by_app(
    schema, request_factory
):
    get_context_value = Mock(return_value=True)
    execute_query(
        request_factory,
        schema,
        {"query": "{ status }"},
        context_value=get_context_value,
    )
    get_context_value.assert_called_once()


def test_custom_context_value_function_result_is_passed_to_resolvers(
    schema, request_factory
):
    get_context_value = Mock(return_value={"test": "TEST-CONTEXT"})
    data = execute_query(
        request_factory,
        schema,
        {"query": "{ testContext }"},
        context_value=get_context_value,
    )
    assert data == {"data": {"testContext": "TEST-CONTEXT"}}


def test_custom_root_value_is_passed_to_resolvers(schema, request_factory):
    data = execute_query(
        request_factory,
        schema,
        {"query": "{ testRoot }"},
        root_value={"test": "TEST-ROOT"},
    )
    assert data == {"data": {"testRoot": "TEST-ROOT"}}


def test_custom_root_value_function_is_set_and_called_by_app(schema, request_factory):
    get_root_value = Mock(return_value=True)
    execute_query(
        request_factory, schema, {"query": "{ status }"}, root_value=get_root_value
    )
    get_root_value.assert_called_once()


def test_custom_root_value_function_is_called_with_context_value(
    schema, request_factory
):
    get_root_value = Mock(return_value=True)
    execute_query(
        request_factory,
        schema,
        {"query": "{ status }"},
        context_value={"test": "TEST-CONTEXT"},
        root_value=get_root_value,
    )
    get_root_value.assert_called_once_with({"test": "TEST-CONTEXT"}, ANY)
