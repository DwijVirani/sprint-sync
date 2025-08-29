from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.entities import User
from app.models.auth import TokenResponse

class AuthRepository:
    def __init__(self, session: Session):
        self.session: Session = session

    async def get_user(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def create_token(self, token_data: dict[str, Any]) -> TokenResponse:
        token = TokenResponse(**token_data)
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token
