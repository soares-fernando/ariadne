from typing import Type, Union, cast

from graphql import (
    DefinitionNode,
    GraphQLTypeResolver,
    GraphQLSchema,
    GraphQLUnionType,
    UnionTypeDefinitionNode,
    UnionTypeExtensionNode,
)

from .base_type import BaseType
from .dependencies import get_dependencies_from_union_type
from .object_type import assert_requirements_are_met
from .types import RequirementsDict
from .utils import parse_definition

UnionNodeType = Union[UnionTypeDefinitionNode, UnionTypeExtensionNode]


class UnionTypeMeta(type):
    def __new__(cls, name: str, bases, kwargs: dict):
        if kwargs.pop("__abstract__", False):
            return super().__new__(cls, name, bases, kwargs)

        schema = kwargs.setdefault("__schema__", None)

        graphql_def = assert_schema_defines_valid_union(
            name, parse_definition(name, schema)
        )

        requirements: RequirementsDict = {
            req.graphql_name: req.graphql_type
            for req in kwargs.setdefault("__requires__", [])
        }

        if isinstance(graphql_def, UnionTypeExtensionNode):
            assert_requirements_contain_extended_union(name, graphql_def, requirements)

        dependencies = get_dependencies_from_union_type(graphql_def)
        assert_requirements_are_met(name, dependencies, requirements)

        kwargs["graphql_name"] = graphql_def.name.value
        kwargs["graphql_type"] = type(graphql_def)

        return super().__new__(cls, name, bases, kwargs)


def assert_schema_defines_valid_union(
    type_name: str, type_def: DefinitionNode
) -> UnionNodeType:
    if not isinstance(type_def, (UnionTypeDefinitionNode, UnionTypeExtensionNode)):
        raise ValueError(
            f"{type_name} class was defined with __schema__ containing "
            f"GraphQL definition for '{type(type_def).__name__}' "
            "(expected 'union')"
        )

    return cast(UnionNodeType, type_def)


def assert_requirements_contain_extended_union(
    type_name: str,
    type_def: UnionTypeExtensionNode,
    requirements: RequirementsDict,
):
    graphql_name = type_def.name.value
    if graphql_name not in requirements:
        raise ValueError(
            f"{type_name} class was defined without required GraphQL union "
            f"definition for '{graphql_name}' in __requires__"
        )

    if requirements[graphql_name] != UnionTypeDefinitionNode:
        raise ValueError(
            f"{type_name} requires '{graphql_name}' to be GraphQL union "
            f"but other type was provided in '__requires__'"
        )


class UnionType(BaseType, metaclass=UnionTypeMeta):
    __abstract__ = True

    graphql_type: Union[Type[UnionTypeDefinitionNode], Type[UnionTypeExtensionNode]]
    resolve_type: GraphQLTypeResolver

    @classmethod
    def __bind_to_schema__(cls, schema: GraphQLSchema):
        graphql_type = cast(GraphQLUnionType, schema.type_map.get(cls.graphql_name))
        graphql_type.resolve_type = cls.resolve_type
