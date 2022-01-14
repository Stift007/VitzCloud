from .abc import Settings

class FASS:
    def __init__(self,app) -> None:
        """FlaskAppSQLSecuring (FASS Class) Prevents SQL Injections

        Args:
            app (Flask)
        """
        self.app = app
        app.config['FASS_OVERRIDE'] = {
            'SQL':'NO-INJECT'
        }

class Rule:
    def __init__(self,settings:Settings=Settings()):
        self.set = settings

        