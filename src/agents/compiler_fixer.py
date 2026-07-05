class CompilerFixer:
    def __init__(self):
        pass
    
    def compile(self, script: str):
        errors = []
        
        if "import" not in script:
            errors.append("Missing import statements")
        
        if "Composition" not in script:
            errors.append("Missing Composition component")
        
        if "{" not in script or "}" not in script:
            errors.append("Missing brackets")
        
        if "return" not in script:
            errors.append("Missing return statement")
        
        if len(errors) == 0:
            return True, []
        else:
            return False, errors