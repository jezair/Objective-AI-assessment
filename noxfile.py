import nox

@nox.session(python=["3.12"])
def tests(session):
    """Запуск pytest"""
    session.run("poetry", "install", external=True)
    session.run("pytest", external=True)

@nox.session(python=["3.12"])
def lint(session):
    """Линтинг через black и flake8"""
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "black", "--check", ".", external=True)
    session.run("poetry", "run", "flake8", ".", external=True)
