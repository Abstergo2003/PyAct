def global_context():
    """
    Global variables accessible from any template using <glb>var_name</glb>.
    """
    return {
        "organization": "Abstergo Creations",
        "system_version": "0.8.0",
        "project_code": "PYACT-2026"
    }
