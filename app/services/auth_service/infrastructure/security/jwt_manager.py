from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request
from app.services.auth_service.domain.entities import UserEntity
from flask import request
from flask_jwt_extended.exceptions import NoAuthorizationError
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    def __init__(self, access_expires: timedelta = timedelta(hours=1),
                 refresh_expires: timedelta = timedelta(days=30)):
        self._access_expires = access_expires
        self._refresh_expires = refresh_expires

    def create_access_token(self, user: UserEntity) -> str:
        """Create a new access token for a user"""
        return create_access_token(
            identity=str(user.id),
            expires_delta=False,
            additional_claims={
                "username": user.username,
                "is_admin": user.is_admin
            }
        )

    def create_refresh_token(self, user: UserEntity) -> str:
        """Create a new refresh token for a user"""
        return create_refresh_token(
            identity=str(user.id),
            expires_delta=self._refresh_expires
        )
        
    def decode_refresh_token(self) -> str:
        """
        Decodes the refresh token from the request and returns the user ID
        
        Returns:
            The user ID from the token
        
        Raises:
            InvalidCredentialsError: If token is invalid or missing
        """
        try:
            # Verify that a valid refresh token is present
            verify_jwt_in_request(refresh=True)
            
            # Extract user ID from token
            user_id = get_jwt_identity()
            return user_id
        except NoAuthorizationError as e:
            logger.error(f"Invalid refresh token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error decoding refresh token: {str(e)}")
            return None
            
    def get_token_from_header(self) -> str:
        """
        Extract the JWT token from the Authorization header
        
        Returns:
            The token string or None if not found
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        return auth_header.split(' ')[1]
        
    def verify_access_token(self) -> str:
        """
        Verify that a valid access token is present and return the user ID
        
        Returns:
            The user ID from the token
            
        Raises:
            Exception: If token verification fails
        """
        try:
            verify_jwt_in_request()
            return get_jwt_identity()
        except Exception as e:
            logger.error(f"Invalid access token: {str(e)}")
            raise

