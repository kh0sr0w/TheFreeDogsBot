from pydantic_settings import BaseSettings, SettingsConfigDict
from bot.utils.logger import log
logo = """

The Free Dogs
                                                                                      
"""

class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

	API_ID: int
	API_HASH: str
	
	TAPS_ENABLED: bool = True
	TAPS_PER_SECOND: list[int] = [80, 100] # tested with 4 fingers
	

	SLEEP_BETWEEN_START: list[int] = [20, 360]
	ERRORS_BEFORE_STOP: int = 3
	USE_PROXY_FROM_FILE: bool = False
	DEFAULT_RATE_LIMIT: int = 5 
	REF_CODE: str = 'ref_nqrF9bYq'
try:
	config = Settings()
except Exception as error:
	log.error(error)
	config = False