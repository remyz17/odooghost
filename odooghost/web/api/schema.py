import strawberry


@strawberry.type
class Query:
    async def hello(self) -> str:
        return "world"


schema = strawberry.Schema(query=Query)
