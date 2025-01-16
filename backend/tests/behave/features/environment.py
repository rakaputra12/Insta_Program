def before_all(context):
    """Initialisiert Ressourcen für alle Tests."""
    print("Starting test suite...")

def after_all(context):
    """Freigeben der Ressourcen nach allen Tests."""
    if hasattr(context, "driver"):
        context.driver.quit()
    print("Test suite complete.")
