from typing import List, Optional, Union

from graphql import GraphQLSchema, build_schema

from .resolvers import set_default_resolvers


def make_executable_schema(
    type_defs: Union[str, List[str]],
    resolvers: Optional[Union[dict, List[dict]]] = None,
) -> GraphQLSchema:
    if isinstance(type_defs, list):
        type_defs = join_type_defs(type_defs)

    schema = build_schema(type_defs)

    if isinstance(resolvers, list):
        for type_resolvers in resolvers:
            type_resolvers.bind_to_schema(schema)
    elif resolvers:
        resolvers.bind_to_schema(schema)

    set_default_resolvers(schema)

    return schema


def join_type_defs(type_defs: List[str]) -> str:
    return "\n\n".join(t.strip() for t in type_defs)
